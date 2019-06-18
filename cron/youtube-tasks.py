import time
import os, sys
import MySQLdb
from django.db.models import Q

# setting django environment
from django.core.wsgi import get_wsgi_application
from config import *
sys.path.append(SPOKEN_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from youtube.tasks import upload_videos, create_playlists, append_to_playlist


upload_videos()
create_playlists()
append_to_playlist()
