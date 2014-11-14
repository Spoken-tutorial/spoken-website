import subprocess
import MySQLdb
import os
import time
from config import *

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
    ((ctr.status = 1 OR ctr.status = 2) AND ctr.video_id IS NULL) \
    ORDER BY cfc.foss, ctd.level_id, ctd.order ASC")

rows = cur.fetchall()
for row in rows:
    ogv_video_path = MEDIA_ROOT + 'videos/' + str(row[8]) + '/' + str(row[1]) + '/' + row[5]
    mp4_video_path, file_extension = os.path.splitext(ogv_video_path)
    mp4_tmp_video_path = mp4_video_path + '-tmp.mp4'
    mp4_video_path = mp4_video_path + '.mp4'
    if os.path.isfile(mp4_tmp_video_path):
        print row[5]
        if os.path.isfile(mp4_video_path):
            os.remove(mp4_video_path)
        if os.path.isfile(mp4_tmp_video_path):
            os.remove(mp4_tmp_video_path)
    if os.path.isfile(mp4_video_path) and (not os.path.getsize(mp4_video_path)):
        print row[5]
        os.remove(mp4_video_path)
