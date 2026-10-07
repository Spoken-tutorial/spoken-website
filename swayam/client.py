import logging
import requests

from django.conf import settings
from django.core.cache import cache

from .exceptions import (
    SwayamAuthenticationError,
        SwayamAuthorizationError,
        SwayamConfigurationError,
        SwayamError,
        SwayamInvalidTransitionError,
        SwayamNotFoundError,
        SwayamNotProvisionedError,
        SwayamValidationError,
    )

logger = logging.getLogger(__name__)
# SwayamClient is M2M. It has nothing to do with the student's browser login.
# Our Django server
#     ↓
# SWAYAM API
class SwayamClient(object):
    TOKEN_CACHE_KEY = 'swayam:m2m:access_token'
    # SWAYAM token lifetime is 600 seconds.
    # Cache slightly less so that we do not use a token
    # right at its expiry boundary.
    TOKEN_CACHE_SECONDS = 540

    def __init__(self):
        self.base_url = getattr(settings, 'SWAYAM_BASE_URL', '').rstrip('/')
        self.client_id = getattr(settings, 'SWAYAM_M2M_CLIENT_ID', '')
        self.client_secret = getattr(settings, 'SWAYAM_M2M_CLIENT_SECRET', '')

        if not self.base_url:
            raise SwayamConfigurationError('SWAYAM_BASE_URL is not configured.')
        if not self.client_id or not self.client_secret:
            raise SwayamConfigurationError('SWAYAM M2M credentials are not configured.')

    def _url(self, path):
        return '{}{}'.format(self.base_url, path)

    def _fetch_access_token(self):
        """
        OAuth2 client_credentials flow.
        This authenticates our LMS SERVER to SWAYAM.
        No learner is involved.
        """
        url = self._url('/oidc/token')
        try:
            response = requests.post(url,
                                     auth=(
                                         self.client_id, self.client_secret
                                     ),
                                     data={
                                         'grant_type': 'client_credentials',
                                         'scope': (
                                            'partner.enrollments:read '
                                            'partner.completions:write'
                                         ),
                                     }, timeout=15,)
                                     
        except requests.RequestException as exc:
            raise SwayamError(
                'Could not connect to SWAYAM token endpoint: {}'.format(exc)
            )

        if response.status_code != 200:
            logger.error(
                'SWAYAM token request failed. status=%s body=%s',
                response.status_code,response.text[:1000],
            )
            raise SwayamAuthenticationError('SWAYAM rejected the M2M credentials.')
        try:
            data = response.json()
        except ValueError:
            raise SwayamError('SWAYAM token endpoint returned invalid JSON.')

        token = data.get('access_token')
        if not token:
            raise SwayamAuthenticationError('SWAYAM token response did not contain access_token.')
        expires_in = data.get('expires_in', 600)

        # Keep a little margin before the actual expiry.
        cache_seconds = max(
                    1,
                    min(int(expires_in) - 30, self.TOKEN_CACHE_SECONDS),
                )
        cache.set(self.TOKEN_CACHE_KEY, token, cache_seconds)
        return token

    def get_access_token(self, force_refresh=False):
        if not force_refresh:
            token = cache.get(self.TOKEN_CACHE_KEY)
            if token:
                return token
        return self._fetch_access_token()

    def _request(self, method, path, params=None, json=None, retry_on_401=True):
        token = self.get_access_token()
        headers = {'Authorization': 'Bearer {}'.format(token)}
        try:
            response = requests.request(
                        method=method,
                        url=self._url(path),
                        headers=headers,
                        params=params,
                        json=json,
                        timeout=20,
                    )
        except requests.RequestException as exc:
            raise SwayamError(
                'Could not connect to SWAYAM: {}'.format(exc)
            )
        # Token may simply have expired.
        if response.status_code == 401 and retry_on_401:
            cache.delete(self.TOKEN_CACHE_KEY)
            token = self.get_access_token(force_refresh=True)
            headers['Authorization'] = ('Bearer {}'.format(token))

            try:
                response = requests.request(
                    method=method,
                    url=self._url(path),
                    headers=headers,
                    params=params,
                    json=json,
                    timeout=20,
                )
            except requests.RequestException as exc:
                raise SwayamError('Could not connect to SWAYAM: {}'.format(exc))
        self._raise_for_error(response)
        return response

    def _raise_for_error(self, response):
        if 200 <= response.status_code < 300:
            return

        try:
            data = response.json()
        except ValueError:
            data = {}
        error_code = data.get('error')
        message = data.get('message', '')

        logger.error(
            'SWAYAM API error. status=%s error=%s body=%s',
            response.status_code,
            error_code,
            response.text[:1000],
        )

        if response.status_code == 400:
            raise SwayamValidationError(message or error_code or 'Invalid request.')

        if response.status_code == 401:
                    raise SwayamAuthenticationError('SWAYAM access token is invalid or expired.')        
        
        if response.status_code == 403:
                    raise SwayamAuthorizationError(
                        message or error_code or 'SWAYAM denied this request.'
                    )
        
        if ( response.status_code == 404 and error_code == 'SSO_NOT_PROVISIONED'):
            raise SwayamNotProvisionedError('Learner has not yet launched the LMS through SWAYAM.')

        if response.status_code == 404:
            raise SwayamNotFoundError( message or error_code or 'SWAYAM resource not found.')

        if ( response.status_code == 409 and error_code == 'INVALID_HANDOFF_TRANSITION'):
            raise SwayamInvalidTransitionError( message or error_code )

        raise SwayamError( 'Unexpected SWAYAM response: HTTP {}'.format(response.status_code))

    def ping(self):
         response = self._request(
              'GET',
              '/api/v1/partner/ping',
         )
         return response.json()

    def get_enrollments(self, page=1, limit=100, course_id=None, status=None):
        params = {
              'page': page,
              'limit': limit
        }
        if course_id:
             params['courseId'] = course_id
        if status:
             params['status'] = status
        response = self._request(
             'GET',
             '/api/v1/partner/enrollments',
             params=params
        )
        return response.json()

    def iter_enrollments(self):
        """
        Iterate through every enrollment page.

        SWAYAM does not send a total count. We stop when a
        page contains fewer than 100 records.
        """
        page = 1
        limit = 100

        while True:
             data = self.get_enrollments(page=page, limit=limit)
             rows = data.get('enrollments', [])
             for row in rows:
                  yield row
             if len(rows) < limit:
                  break
             page += 1

    def get_student_enrollments(self, swayam_sub):
        """
        Fetch enrollments for one particular SWAYAM user.
        """
        path = (
                    '/api/v1/partner/students/{}/enrollments'
                    .format(swayam_sub)
                )
        response = self._request(
                    'GET',
                    path,
                )
        return response.json()

    def confirm_completion(self, enrollment_id):
        """
        We include this API now although progress reporting
        will be implemented later.

        Call this ONLY when local completion rules are final.
        """
        path = (
                    '/api/v1/partner/enrollments/{}/completion'
                    .format(enrollment_id)
                )
        
        self._request(
                    'POST',
                    path,
                    json={},
                )

    # to transmit learner progress percentage to swayam api
    def update_progress(self, enrollment_id, progress_percent):
        path = (
            '/api/v1/partner/enrollments/{}/progress'
            .format(enrollment_id)
        )
        logger.info(
            'Sending SWAYAM progress update. enrollment_id=%s progress_percent=%s',
            enrollment_id,
            progress_percent,
        )
        try:
            return self._request(
                'POST',
                path,
                json={'progressPercent': int(progress_percent)},
            )
        except Exception as exc:
            logger.warning(
                'SWAYAM update_progress request skipped or failed: %s',
                exc,
            )
            return None

    