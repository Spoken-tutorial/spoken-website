import json
from django.conf import settings
import uuid

def dump_json_logs(data):
    with open(settings.MEDIA_ROOT+"logs/"+str(uuid.uuid4())+".json", 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
	
