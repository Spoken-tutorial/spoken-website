import json
from django.conf import settings
import uuid
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

def create_thread(func):
   @wraps(func)
   def async_thread(data):
       with ThreadPoolExecutor(max_workers=2) as executor:
           executor.submit(func, data)
   return async_thread


@create_thread
def dump_json_logs(data):
    with open(settings.MEDIA_ROOT+"logs/"+str(uuid.uuid4())+".json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
	
