from .utils import check_server_status, is_valid_page_param
from django.shortcuts import render
from django.core.cache import cache
from statistics.models import WhitelistedIP
from time import time
from .config import TIME_WINDOW, MAX_REQUEST
import ipaddress


def is_ip_whitelisted(ip_str):
    ip = ipaddress.ip_address(ip_str)
    for entry in WhitelistedIP.objects.all():
        try:
            net = ipaddress.ip_network(entry.ip_address, strict=False)
            if ip in net:
                return True
        except ValueError:
            continue
    return False


def rate_limited_view(view_func):
    def _wrapped_view(request, *args, **kwargs):
        ip = request.META.get("REMOTE_ADDR")
        if not is_ip_whitelisted(ip):
            if not request.user.is_authenticated and not is_valid_page_param(request):
                message = "Invalid or malformed page parameter."
                return render(request, 'statistics/templates/temporary_disabled.html', {"message": message})

            okay = check_server_status()
            if not okay:
                message = "This page is temporarily unavailable due to high server load. We’re working to restore access soon — thank you for your patience."
                return render(request, 'statistics/templates/temporary_disabled.html', {"message": message})
            # check rate limit
            key = f'rl:{ip}'
            data = cache.get(key, {'count': 0, 'start': time()})
            now = time()

            if now - data['start'] < TIME_WINDOW:
                if data['count'] >= MAX_REQUEST:
                    message = "You’ve exceeded the allowed number of requests. Please wait a few moments before trying again."
                    return render(request, 'statistics/templates/temporary_disabled.html', {"message": message})
                data['count'] +=1
            else:
                data = {"count": 1, "start": now}
            cache.set(key, data, timeout=TIME_WINDOW)
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
