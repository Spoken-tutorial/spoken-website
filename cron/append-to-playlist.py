import time
import os, sys
from django.db.models import Q

# setting django environment
from django.core.wsgi import get_wsgi_application
sys.path.append("/websites_dir/django_spoken/spoken")
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from config import *
from youtube_upload import *
from creation.models import *

# creating youtube object
youtube = Youtube(DEVELOPER_KEY)
debug("Login to Youtube API: email='%s', password='%s'" %
  (EMAIL, "*" * len(PASSWORD)))

# login to youtube
try:
  youtube.login(EMAIL, PASSWORD)
except gdata.service.BadAuthentication:
  raise BadAuthentication("Authentication failed")

# fetching tutorial resource records
rows = TutorialResource.objects.filter(
  Q(status=1)|Q(status=2),
  video_id__isnull=False,
  playlist_item_id__isnull=True
).order_by(
  'tutorial_detail__foss__foss',
  'tutorial_detail__level_id',
  'tutorial_detail__order'
)

# opening log file to keep details of updated records
today = time.strftime('%Y-%m-%d_%H-%M-%S')

error_log_file_head = open(
  LOG_ROOT + 'playlistitem-error-log-' + today + '.txt',
  "w"
)

success_log_file_head = open(
  LOG_ROOT + 'playlistitem-success-log-' + today + '.txt',
  "w"
)

for row in rows:
  # fetching playlist record
  playlist = PlaylistInfo.objects.filter(
    language_id=row.language_id,
    foss_id=row.tutorial_detail.foss.id
  ).first()

  # throw error if the playlist entry is not available
  if not playlist:
    error_string = str(row.tutorial_detail.foss.id) + ',' + str(row.language_id) + ',Playlist-Missing'
    error_log_file_head.write(error_string + '\n')
    print error_string
    continue

  # adding video to playlist
  try:
    item_id = youtube.add_video_to_playlist(row.video_id, playlist.playlist_id)
  except Exception, e:
    print e
    time.sleep(1)
    continue

  # check if the item_id is generated or not
  if item_id:
    # save the item_id to tutorial_resource
    row.playlist_item_id = item_id
    row.save()

    # insert item_id to playlistitem
    PlaylistItem.objects.create(playlist=playlist, item_id=item_id)

    # generating success message
    success_string = row.tutorial_detail.tutorial + ',' + row.language.name + ',Success'
    success_log_file_head.write(success_string + '\n')
    print success_string
  else:
    # generating failure message
    error_string = row.tutorial_detail.tutorial + ',' + row.language.name + ',Failed'
    error_log_file_head.write(error_string + '\n')
    print error_string
  time.sleep(1)
error_log_file_head.close()
success_log_file_head.close()
