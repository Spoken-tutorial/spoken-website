import MySQLdb
import time
from youtube_upload import *
from config import *

# creating youtube object
youtube = Youtube(DEVELOPER_KEY)
debug("Login to Youtube API: email='%s', password='%s'" %
      (EMAIL, "*" * len(PASSWORD)))
try:
    youtube.login(EMAIL, PASSWORD)
except gdata.service.BadAuthentication:
    raise BadAuthentication("Authentication failed")

db = MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASS, \
    db = DB_NAME)

cur = db.cursor()
cur.execute("SELECT ctr.id, ctr.tutorial_detail_id, ctr.common_content_id, \
    ctr.language_id, ctr.outline, ctr.video, ctr.video_id, \
    ctr.playlist_item_id, ctd.foss_id, ctd.tutorial, ctd.level_id, ctd.order, \
    ctc.keyword, clg.name FROM creation_tutorialresource ctr INNER JOIN \
    creation_tutorialdetail ctd ON (ctr.tutorial_detail_id = ctd.id) \
    INNER JOIN creation_fosscategory cfc ON (ctd.foss_id = cfc.id) INNER JOIN \
    creation_tutorialcommoncontent ctc ON (ctr.common_content_id = ctc.id) \
    INNER JOIN creation_language clg ON (ctr.language_id = clg.id) WHERE \
    ((ctr.status = 1 OR ctr.status = 2) AND ctr.video_id IS NOT NULL AND ctr.playlist_item_id IS NULL) ORDER BY \
    cfc.foss, ctd.level_id, ctd.order ASC")
rows = cur.fetchall()
error_log_file_head = open(LOG_ROOT + 'playlistitem-error-log.txt',"w")
success_log_file_head = open(LOG_ROOT + 'playlistitem-success-log.txt',"w")

for row in rows:
    cur.execute("SELECT cpi.id, cpi.foss_id, cpi.language_id, \
        cpi.playlist_id, cpi.created, cpi.updated FROM creation_playlistinfo \
        cpi WHERE (cpi.language_id = %s  AND cpi.foss_id = %s)" % (row[3], row[8]))
    playlist = cur.fetchone()
    if not playlist:
        error_string = row[8] + ' - ' + row[3] + ' -- Playlist Missing'
        error_log_file_head.write(error_string + '\n')
        print error_string
        continue
    video_id = row[6]
    try:
        item_id = youtube.add_video_to_playlist(video_id, playlist[3])
    except Exception, e:
        print e
        time.sleep(1)
        continue
    if item_id:
        currtime = time.strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("UPDATE creation_tutorialresource SET \
            playlist_item_id='%s' WHERE id=%s" % (item_id, row[0]))
        cur.execute("INSERT INTO creation_playlistitem (playlist_id, \
            item_id, created, updated) VALUES('%s', '%s', '%s', '%s')" % \
            (playlist[0], item_id, currtime, currtime))
        db.commit()
        success_string = error_string = row[9] + ' - ' + row[13] + ' -- success'
        success_log_file_head.write(success_string + '\n')
        print success_string
    else:
        error_string = row[9] + ' - ' + row[13] + ' -- Failed'
        error_log_file_head.write(error_string + '\n')
        print error_string
    time.sleep(1)
error_log_file_head.close()
success_log_file_head.close()
