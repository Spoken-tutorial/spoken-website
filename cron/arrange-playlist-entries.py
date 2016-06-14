import time
import os, sys
import MySQLdb
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

# connecting and creating cursor to cron_logs DB
ldb = MySQLdb.connect(
  host = DB_HOST,
  user = DB_USER,
  passwd = DB_PASS,
  db = 'cron_logs'
)
lcur = ldb.cursor()

# fetching all foss
rows = FossCategory.objects.all().order_by('foss')

for row in rows:
  # fetching  available languages for current foss(row)
  langs = Language.objects.filter(
    id__in=TutorialResource.objects.filter(
      tutorial_detail__foss_id=row.id
    ).values_list('language_id').distinct()
  )

  for lang in langs:
    # fetching playlist record
    playlist = PlaylistInfo.objects.filter(
      language_id=lang.id,
      foss_id=row.id
    ).first()

    # throw error if the playlist entry is not available
    if not playlist:
      error_string = row.foss + ' - ' + lang.name + ' -- Playlist Missing'
      print error_string
      continue

    # fetch tutorial_resource records based on foss and language
    tutorials = TutorialResource.objects.filter(
      Q(status=1)|Q(status=2),
      tutorial_detail__foss_id = row.id,
      language_id = lang.id,
      video_id__isnull=False,
      playlist_item_id__isnull=False
    ).order_by('tutorial_detail__level_id', 'tutorial_detail__order')

    counter = 1
    for tutorial in tutorials:
      # fetching count of log entries for current tutorial_resource
      lcur.execute("SELECT count(id) AS idcnt FROM playlist_arranger " + \
        "WHERE trid=" + str(tutorial.id))
      tr_log = lcur.fetchone()

      # skip tutorial_resource(tutorial) if log entry count > 0
      if tr_log and int(tr_log[0]):
        print tutorial.id, '-- Skipping...'
        counter += 1
        continue
      # fetching video feed from youtube
      entry = youtube.get_feed_from_video_id(tutorial.video_id)

      if entry:
        # playlist url for sending api call
        playlist_uri = 'http://gdata.youtube.com/feeds/api/playlists/' + \
          playlist.playlist_id
        try:
          # update video entry position in playlist
          playlist_entry = youtube.service.UpdatePlaylistVideoEntryMetaData(
            playlist_uri, tutorial.playlist_item_id, entry.media.title.text,
            entry.media.description.text, counter
          )
        except Exception, e:
          # throw error if api call is not success
          print e
          error_string = str(tutorial.id) + ' - ' + str(playlist.playlist_id) + ' -- Error...'
          print error_string
          time.sleep(2)
          continue

        # increase position counter
        counter += 1

        # print success message
        print str(tutorial.id) + ' -- Success --' + \
          playlist_entry.id.text.replace(playlist_uri, '').strip('/')

        # add tutorial_resource(tutorial) id to playlist_arranger
        lcur.execute(
          "INSERT INTO playlist_arranger (trid) VALUES(%s)",
          [str(tutorial.id)]
        )
        ldb.commit()
      else:
        # throw error if video entry is not available
        error_string = str(tutorial.id) + ' -- Failed to get video entry'
        print error_string
      time.sleep(1)
    #time.sleep(1)
  #time.sleep(1)
