import MySQLdb
import time
import cgi
from youtube_upload import *
from config import *
from text2html import *

# creating youtube object
youtube = Youtube(DEVELOPER_KEY)
debug("Login to Youtube API: email='%s', password='%s'" %
      (EMAIL, "*" * len(PASSWORD)))
try:
    youtube.login(EMAIL, PASSWORD)
except gdata.service.BadAuthentication:
    raise BadAuthentication("Authentication failed")


db = MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASS, \
    db = DB_NAME, charset='utf8', use_unicode=True)
cur = db.cursor()
cur.execute("SELECT ctr.id, ctr.tutorial_detail_id, ctr.common_content_id, \
    ctr.language_id, ctr.outline, ctr.video, ctr.video_id, \
    ctr.playlist_item_id, ctd.foss_id, ctd.tutorial, ctd.level_id, ctd.order, \
    ctc.keyword, clg.name FROM creation_tutorialresource ctr INNER JOIN \
    creation_tutorialdetail ctd ON (ctr.tutorial_detail_id = ctd.id) \
    INNER JOIN creation_fosscategory cfc ON (ctd.foss_id = cfc.id) INNER JOIN \
    creation_tutorialcommoncontent ctc ON (ctr.common_content_id = ctc.id) \
    INNER JOIN creation_language clg ON (ctr.language_id = clg.id) WHERE \
    ((ctr.status = 1 OR ctr.status = 2) AND ctr.video_id IS NOT NULL) ORDER BY \
    cfc.foss, ctd.level_id, ctd.order ASC")
rows = cur.fetchall()
error_log_file_head = open(LOG_ROOT + 'video-meta-error-log.txt',"w")
for row in rows:
    entry = youtube.get_feed_from_video_id(row[6])
    entry.media.description = gdata.media.Description(description_type = \
        'html', text = convert_to_html(row[4]))
    entry.media.keywords = gdata.media.Keywords(row[12])
    try:
        youtube.service.UpdateVideoEntry(entry)
        print entry.media.title, '-- Success'
    except Exception, e:
        print convert_to_html(row[4])
        print entry.media.title, '-- Failed'
        error_string = row[9] + ' - ' + row[13] + ' -- Failed'
        error_log_file_head.write(error_string + '\n')
        print e
    time.sleep(1)
error_log_file_head.close()
