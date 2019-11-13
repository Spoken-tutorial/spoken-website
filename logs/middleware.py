from .urls import EVENT_NAME_DICT
import requests
import json

class Logs:

    def __init__(self, get_response):
        self.LOG_CLASS = "MIDDLEWARE"
        self.get_response = get_response
        self.c_url =  "http://localhost:9600" 

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.META['PATH_INFO'] in EVENT_NAME_DICT.keys():
            data = {}
            data['path_info'] = request.META['PATH_INFO']
            data['method'] = request.method
            data['view_args'] = view_args
            data['view_kwargs'] = view_kwargs
            data['event_name'] = EVENT_NAME_DICT[data['path_info']]['name']
            r =requests.put(self.c_url, json=data)
            print(r.status_code)
        return None