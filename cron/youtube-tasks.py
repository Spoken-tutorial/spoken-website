import time
import os, sys
import MySQLdb
from django.db.models import Q

# setting django environment
from django.core.wsgi import get_wsgi_application
# sys.path.append("/websites_dir/django_spoken/spoken")
sys.path.append("/home/vishnu/mine/spoken-website")
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from config import *
from youtube.tasks import upload_videos, create_playlists, append_to_playlist


# upload_videos()
# create_playlists()
append_to_playlist()
