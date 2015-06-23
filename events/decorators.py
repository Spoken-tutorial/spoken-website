from functools import wraps
from django.conf import settings
from django.contrib import messages
from django.shortcuts import resolve_url
from django.utils.decorators import available_attrs
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.six.moves.urllib.parse import urlparse

default_message = "You don't have enough permission to view this page."

def user_passes_test(test_func, login_url=None, \
    redirect_field_name=REDIRECT_FIELD_NAME):

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request): 
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view 
    return decorator

def group_required(*group_names):
    def in_groups(request):
        if request.user.is_authenticated():
            if bool(request.user.groups.filter(name__in=group_names)):
                return True
            else:
                messages.error(request, default_message)
        return False
    return user_passes_test(in_groups)
