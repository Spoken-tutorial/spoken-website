from .utils import check_server_status
from django.shortcuts import render
from django.core.cache import cache
from statistics.models import RateLimitWhitelist
from time import time
from .config import TIME_WINDOW, MAX_REQUEST


def rate_limited_view(view_func):
    def _wrapped_view(request, *args, **kwargs):
        ip = request.META.get("REMOTE_ADDR")
        whitelisted = RateLimitWhitelist.objects.filter(ip_address=ip).exists()

        if not whitelisted:
            okay = check_server_status()
            if not okay:
                return render(request, 'statistics/templates/temporary_disabled.html', {})
            # check rate limit
            key = f'rl:{ip}'
            data = cache.get(key, {'count': 0, 'start': time()})
            now = time()

            if now - data['start'] < TIME_WINDOW:
                if data['count'] >= MAX_REQUEST:
                    return render(request, 'statistics/templates/temporary_disabled.html', {})
                data['count'] +=1
            else:
                data = {"count": 1, "start": now}
            cache.set(key, data, timeout=TIME_WINDOW)
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
