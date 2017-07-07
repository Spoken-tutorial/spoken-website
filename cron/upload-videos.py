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
    db = DB_NAME, charset='utf8')
cur = db.cursor()
cur.execute("SELECT ctr.id, ctr.tutorial_detail_id, ctr.common_content_id, \
    ctr.language_id, ctr.outline, ctr.video, ctr.video_id, \
    ctr.playlist_item_id, ctd.foss_id, ctd.tutorial, ctd.level_id, ctd.order, \
    ctc.keyword, clg.name FROM creation_tutorialresource ctr INNER JOIN \
    creation_tutorialdetail ctd ON (ctr.tutorial_detail_id = ctd.id) \
    INNER JOIN creation_fosscategory cfc ON (ctd.foss_id = cfc.id) INNER JOIN \
    creation_tutorialcommoncontent ctc ON (ctr.common_content_id = ctc.id) \
    INNER JOIN creation_language clg ON (ctr.language_id = clg.id) WHERE \
    ((ctr.status = 1 OR ctr.status = 2) AND ctr.video_id IS NULL) ORDER BY \
    cfc.foss, ctd.level_id, ctd.order ASC")
rows = cur.fetchall()
error_log_file_head = open(LOG_ROOT + 'video-error-log.txt',"w")
success_log_file_head = open(LOG_ROOT + 'video-success-log.txt',"w")
for row in rows:
    ogv_video_path = MEDIA_ROOT + 'videos/' + str(row[8]) + '/' + str(row[1]) + '/' + str(row[5])
    mp4_video_path, file_extn = os.path.splitext(ogv_video_path)
    mp4_video_path = mp4_video_path + '.mp4'
    if not os.path.isfile(mp4_video_path):
         print row[9] + ' - ' + row[13] + ' -- MP4 video missing'
         continue
    options = {
        'title': str(row[9]) + ' - ' + str(row[13]),
        'description': row[4],
        'keywords': row[12],
        'category': 'Education',
        'private': False,
        'location': None,
        'unlisted': False
    }
    try:
        video_id = upload_video(youtube, options, mp4_video_path)
    except:
        video_id = None
    if not video_id:
        options = {
            'title': str(row[9]) + ' - ' + str(row[13]),
            'description': '',
            'keywords': '',
            'category': 'Education',
            'private': False,
            'location': None,
            'unlisted': False
        }
        video_id = upload_video(youtube, options, mp4_video_path)
    if video_id:
        cur.execute("UPDATE creation_tutorialresource SET video_id='%s' \
            WHERE id=%s" % (video_id, row[0]))
        db.commit()
        success_string = row[9] + ' - ' + row[13] + ' -- ' + video_id
        success_log_file_head.write(success_string + '\n')
        print success_string
    else:
        error_string = row[9] + ' - ' + row[13] + ' -- Failed'
        error_log_file_head.write(error_string + '\n')
        print error_string
    time.sleep(1)
error_log_file_head.close()
success_log_file_head.close()
