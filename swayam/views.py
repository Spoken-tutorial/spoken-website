import base64
import hashlib
import hmac
import json
import logging
import os

import jwt
import requests

from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from .client import SwayamClient
from .services import (
    SwayamEnrollmentService,
    SwayamUserService,
    SwayamProgressService,
)
from .utils import (
    is_swayam_user,
    is_swayam_foss,
)


logger = logging.getLogger(__name__)


SWAYAM_OIDC_SESSION_KEY = 'swayam_oidc_login'


def _random_urlsafe_string(num_bytes=32):
    value = base64.urlsafe_b64encode(
        os.urandom(num_bytes)
    )

    if not isinstance(value, str):
        value = value.decode('ascii')

    return value.rstrip('=')


def _pkce_challenge(verifier):
    digest = hashlib.sha256(
        verifier.encode('ascii')
    ).digest()

    challenge = base64.urlsafe_b64encode(
        digest
    )

    if not isinstance(challenge, str):
        challenge = challenge.decode('ascii')

    return challenge.rstrip('=')


def _expected_issuer():
    return (
        settings.SWAYAM_BASE_URL.rstrip('/')
        + '/oidc'
    )


def _is_allowed_target(target):
    """
    Prevent open redirects.

    Allow:
        /some/local/path

    or HTTPS URLs belonging to Spoken Tutorial.
    """

    if not target:
        return False

    parsed = urlparse(target)

    # Relative URL.
    if not parsed.scheme and not parsed.netloc:
        return (
            target.startswith('/')
            and not target.startswith('//')
        )

    allowed_hosts = (
        'spoken-tutorial.org',
        # 'www.spoken-tutorial.org',
        'beta.spoken-tutorial.org',
        # 'www.beta.spoken-tutorial.org',
    )

    return (
        parsed.scheme == 'https'
        and parsed.hostname in allowed_hosts
    )

def sso_start(request):
    issuer = request.GET.get('iss', '')
    login_hint = request.GET.get('login_hint', '')
    target = request.GET.get('target_link_uri', '')
    enrollment_id = request.GET.get('lti_message_hint','')

    if issuer != _expected_issuer():
        return HttpResponseBadRequest(
            'Invalid SWAYAM issuer.'
        )

    if not enrollment_id:
        return HttpResponseBadRequest(
            'Missing SWAYAM enrollment ID.'
        )

    if target and not _is_allowed_target(target):
        return HttpResponseBadRequest(
            'Invalid target_link_uri.'
        )

    state = _random_urlsafe_string()
    nonce = _random_urlsafe_string()
    code_verifier = _random_urlsafe_string(48)

    code_challenge = _pkce_challenge(
        code_verifier
    )

    request.session[SWAYAM_OIDC_SESSION_KEY] = {
        'state': state,
        'nonce': nonce,
        'code_verifier': code_verifier,
        'login_hint': login_hint,
        'enrollment_id': enrollment_id,
        'target_link_uri': target,
    }

    authorization_endpoint = (
        settings.SWAYAM_BASE_URL.rstrip('/')
        + '/oidc/auth'
    )

    params = {
        'client_id': settings.SWAYAM_OIDC_CLIENT_ID,
        'redirect_uri': (
            settings.SWAYAM_OIDC_REDIRECT_URI
        ),
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'nonce': nonce,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
    }

    if login_hint:
        params['login_hint'] = login_hint

    authorization_url = '{}?{}'.format(
        authorization_endpoint,
        urlencode(params),
    )

    return redirect(authorization_url)

def _exchange_authorization_code(
    code,
    code_verifier,
):
    """
    Exchange the short-lived OIDC authorization code
    for tokens.

    SWAYAM requires client_secret_basic.
    """

    token_endpoint = (
        settings.SWAYAM_BASE_URL.rstrip('/')
        + '/oidc/token'
    )

    try:
        response = requests.post(
            token_endpoint,
            auth=(
                settings.SWAYAM_OIDC_CLIENT_ID,
                settings.SWAYAM_OIDC_CLIENT_SECRET,
            ),
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': (
                    settings.SWAYAM_OIDC_REDIRECT_URI
                ),
                'code_verifier': code_verifier,
            },
            timeout=15,
        )

    except requests.RequestException:
        logger.exception(
            'Could not reach SWAYAM OIDC token endpoint.'
        )
        raise

    if response.status_code != 200:
        logger.error(
            'SWAYAM OIDC code exchange failed. '
            'status=%s body=%s',
            response.status_code,
            response.text[:1000],
        )

        raise ValueError(
            'SWAYAM authorization code exchange failed.'
        )

    try:
        data = response.json()
    except ValueError:
        raise ValueError(
            'SWAYAM token endpoint returned invalid JSON.'
        )

    if not data.get('id_token'):
        raise ValueError(
            'SWAYAM token response has no id_token.'
        )

    return data

def _fetch_jwks():
    jwks_url = (
        settings.SWAYAM_BASE_URL.rstrip('/')
        + '/oidc/jwks'
    )

    try:
        response = requests.get(
            jwks_url,
            timeout=15,
        )

    except requests.RequestException:
        logger.exception(
            'Could not fetch SWAYAM JWKS.'
        )
        raise

    if response.status_code != 200:
        raise ValueError(
            'Could not fetch SWAYAM JWKS.'
        )

    try:
        return response.json()
    except ValueError:
        raise ValueError(
            'SWAYAM JWKS endpoint returned invalid JSON.'
        )

def _get_signing_key(id_token):
    try:
        header = jwt.get_unverified_header(
            id_token
        )
    except Exception:
        raise ValueError(
            'Invalid SWAYAM ID token header.'
        )

    kid = header.get('kid')
    algorithm = header.get('alg')

    if algorithm != 'RS256':
        raise ValueError(
            'Unexpected SWAYAM ID token algorithm: {}'
            .format(algorithm)
        )

    if not kid:
        raise ValueError(
            'SWAYAM ID token has no kid.'
        )

    jwks = _fetch_jwks()

    keys = jwks.get('keys', [])

    matching_key = None

    for key in keys:
        if key.get('kid') == kid:
            matching_key = key
            break

    if matching_key is None:
        raise ValueError(
            'No matching SWAYAM signing key found.'
        )

    try:
        public_key = (
            jwt.algorithms.RSAAlgorithm.from_jwk(
                json.dumps(matching_key)
            )
        )
    except Exception:
        logger.exception(
            'Could not construct SWAYAM RSA public key.'
        )

        raise ValueError(
            'Invalid SWAYAM signing key.'
        )

    return public_key


def _verify_id_token(
    id_token,
    expected_nonce,
):
    public_key = _get_signing_key(
        id_token
    )

    try:
        claims = jwt.decode(
            id_token,
            key=public_key,
            algorithms=['RS256'],
            audience=settings.SWAYAM_OIDC_CLIENT_ID,
            issuer=_expected_issuer(),
        )

    except jwt.ExpiredSignatureError:
        raise ValueError(
            'SWAYAM ID token has expired.'
        )

    except jwt.InvalidAudienceError:
        raise ValueError(
            'SWAYAM ID token has invalid audience.'
        )

    except jwt.InvalidIssuerError:
        raise ValueError(
            'SWAYAM ID token has invalid issuer.'
        )

    except jwt.InvalidTokenError:
        logger.exception(
            'SWAYAM ID token validation failed.'
        )

        raise ValueError(
            'Invalid SWAYAM ID token.'
        )

    token_nonce = claims.get('nonce')

    if not token_nonce:
        raise ValueError(
            'SWAYAM ID token has no nonce.'
        )

    if not hmac.compare_digest(
        str(token_nonce),
        str(expected_nonce),
    ):
        raise ValueError(
            'SWAYAM ID token nonce does not match.'
        )

    sub = claims.get('sub')

    if not sub:
        raise ValueError(
            'SWAYAM ID token has no sub.'
        )

    return claims

def sso_callback(request):
    #
    # SWAYAM may return an OAuth/OIDC error instead
    # of an authorization code.
    #
    oidc_error = request.GET.get('error')

    if oidc_error:
        logger.warning(
            'SWAYAM OIDC returned error=%s description=%s',
            oidc_error,
            request.GET.get(
                'error_description',
                '',
            ),
        )

        return HttpResponseBadRequest(
            'SWAYAM login failed.'
        )

    code = request.GET.get('code', '')
    returned_state = request.GET.get(
        'state',
        '',
    )

    if not code:
        return HttpResponseBadRequest(
            'Missing authorization code.'
        )

    login_data = request.session.get(
        SWAYAM_OIDC_SESSION_KEY
    )

    if not login_data:
        return HttpResponseBadRequest(
            'SWAYAM login session has expired.'
        )

    expected_state = login_data.get(
        'state',
        ''
    )

    #
    # First security check:
    # callback must correspond to the login we initiated.
    #
    if not (
        returned_state
        and expected_state
        and hmac.compare_digest(
            str(returned_state),
            str(expected_state),
        )
    ):
        return HttpResponseBadRequest(
            'Invalid SWAYAM login state.'
        )

    try:
        #
        # Exchange authorization code for tokens.
        #
        token_data = (
            _exchange_authorization_code(
                code=code,
                code_verifier=login_data[
                    'code_verifier'
                ],
            )
        )

        id_token = token_data['id_token']

        #
        # Cryptographically verify the ID token.
        #
        claims = _verify_id_token(
            id_token=id_token,
            expected_nonce=login_data[
                'nonce'
            ],
        )

        swayam_sub = claims['sub']

        email = (
            claims.get('email')
            or ''
        )

        name = (
            claims.get('name')
            or ''
        )

        #
        # Optional but useful consistency check:
        #
        # login_hint came from the initial SWAYAM
        # launch. The VERIFIED sub is authoritative.
        #
        login_hint = login_data.get(
            'login_hint'
        )

        if (
            login_hint
            and str(login_hint) != str(swayam_sub)
        ):
            logger.warning(
                'SWAYAM login_hint/sub mismatch. '
                'login_hint=%s sub=%s',
                login_hint,
                swayam_sub,
            )

        #
        # Find/create the Django user.
        #
        user_service = SwayamUserService()

        user, user_created = (
            user_service.get_or_create_user(
                swayam_sub=swayam_sub,
                email=email,
                name=name,
            )
        )

        #
        # Immediately fetch this particular student's
        # SWAYAM enrollments.
        #
        # This means we don't depend entirely on the
        # nightly roster sync.
        #
        client = SwayamClient()

        student_enrollment_data = (
            client.get_student_enrollments(
                swayam_sub
            )
        )

        enrollment_service = (
            SwayamEnrollmentService(
                client=client
            )
        )

        for row in student_enrollment_data.get(
            'enrollments',
            []
        ):
            enrollment_service.sync_enrollment_row(
                row
            )

        #
        # Link THIS launch's enrollment to the user.
        #
        enrollment = (
            user_service.link_enrollment(
                user=user,
                swayam_enrollment_id=(
                    login_data['enrollment_id']
                ),
            )
        )

        #
        # Log the Django User into Spoken Tutorial.
        #
        login(
            request,
            user,
            backend=(
                'django.contrib.auth.backends.'
                'ModelBackend'
            ),
        )

        #
        # Remove one-time OIDC login state.
        #
        request.session.pop(
            SWAYAM_OIDC_SESSION_KEY,
            None,
        )

        target = login_data.get(
            'target_link_uri'
        )

        if target and _is_allowed_target(
            target
        ):
            return redirect(target)

        #
        # Fallback destination.
        #
        # Replace '/' later with the preferred course
        # page if desired.
        #
        return redirect('/')

    except Exception as exc:
        logger.exception(
            'SWAYAM SSO callback failed.'
        )

        #
        # Do NOT display exception details,
        # tokens or claims to the learner.
        #
        return HttpResponseBadRequest(
            'Could not complete SWAYAM login.'
        )


# Endpoint for saving swayam learner video progress
@csrf_exempt
def save_progress(request):
    is_auth = request.user.is_authenticated() if callable(request.user.is_authenticated) else request.user.is_authenticated
    if not is_auth:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
    if not is_swayam_user(request.user):
        return JsonResponse({'status': 'error', 'message': 'Not a SWAYAM user'}, status=403)

    foss_id = request.POST.get('foss_id')
    tutorial_id = request.POST.get('tutorial_id')
    lang_id = request.POST.get('lang_id')
    video_time = request.POST.get('videotime', 0.0)
    duration = request.POST.get('duration', 0.0)

    if not foss_id or not is_swayam_foss(foss_id):
        return JsonResponse({'status': 'error', 'message': 'FOSS is not part of SWAYAM'}, status=400)

    try:
        from creation.models import FossCategory, TutorialDetail, Language
        foss = FossCategory.objects.get(pk=int(foss_id))
        tutorial = TutorialDetail.objects.get(pk=int(tutorial_id))
        language = Language.objects.filter(pk=int(lang_id)).first() if lang_id else None

        progress = SwayamProgressService().record_progress(
            user=request.user,
            foss=foss,
            tutorial_detail=tutorial,
            video_time=video_time,
            duration=duration,
            language=language,
        )
        return JsonResponse({
            'status': 'success',
            'progress_percent': progress.progress_percent,
            'is_completed': progress.is_completed,
            'course_progress_percent': progress.enrollment.progress_percent if progress.enrollment else 0,
        })
    except Exception as exc:
        logger.warning('save_progress error: %s', exc)
        return JsonResponse({'status': 'error', 'message': str(exc)}, status=400)