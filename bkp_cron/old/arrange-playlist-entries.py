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

ldb = MySQLdb.connect(host = DB_HOST, user = 'stadmin', passwd = 'Listdb*4321sT', \
    db = 'cron_logs')
lcur = ldb.cursor()

db = MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASS, \
    db = DB_NAME)

cur = db.cursor()
cur.execute("SELECT * FROM creation_fosscategory ORDER BY foss ASC")
rows = cur.fetchall()
error_log_file_head = open(LOG_ROOT + 'order-playlistitem-error-log.txt',"w")
success_log_file_head = open(LOG_ROOT + 'order-playlistitem-success-log.txt', \
    "w")

for row in rows:
    cur.execute("SELECT clg.id, clg.name, clg.user_id, clg.created, \
        clg.updated FROM creation_language clg WHERE clg.id IN (SELECT \
        DISTINCT U0.language_id FROM creation_tutorialresource U0 INNER JOIN \
        creation_tutorialdetail U1 ON ( U0.tutorial_detail_id = U1.id ) WHERE \
        U1.foss_id = %s ) ORDER BY clg.name ASC", [row[0]])
    langs = cur.fetchall()
    for lang in langs:
        cur.execute("SELECT cpi.id, cpi.foss_id, cpi.language_id, \
        cpi.playlist_id FROM creation_playlistinfo cpi WHERE \
        (cpi.language_id = %s  AND cpi.foss_id = %s)", [lang[0], row[0]])
        playlist = cur.fetchone()
        if not playlist:
            error_string = row[1] + ' - ' + lang[1] + ' -- Playlist Missing'
            error_log_file_head.write(error_string + '\n')
            print error_string
            continue

        cur.execute("SELECT ctr.id, ctr.tutorial_detail_id, \
            ctr.common_content_id, ctr.language_id, ctr.outline, \
            ctr.outline_user_id, ctr.outline_status, ctr.script, \
            ctr.script_user_id, ctr.script_status, ctr.timed_script, \
            ctr.video, ctr.video_id, ctr.playlist_item_id, ctd.id, \
            ctd.foss_id, ctd.tutorial, ctd.level_id, ctd.order, ctd.user_id, \
            ctd.created, ctd.updated FROM creation_tutorialresource ctr \
            INNER JOIN creation_tutorialdetail ctd ON \
            ( ctr.tutorial_detail_id = ctd.id ) WHERE ((ctr.status = 1  OR \
            ctr.status = 2 ) AND ctd.foss_id = %s AND ctr.language_id = %s \
            AND ctr.video_id IS NOT NULL AND ctr.playlist_item_id IS NOT NULL \
            ) ORDER BY ctd.level_id, ctd.order ASC", [row[0], lang[0]])
        tutorials = cur.fetchall()
        counter = 1
        for tutorial in tutorials:
            playlist_uri = 'http://gdata.youtube.com/feeds/api/playlists/' + \
                playlist[3]
            entry = youtube.get_feed_from_video_id(tutorial[12])
            tr_log_rec = lcur.execute('SELECT count(id) AS idcnt FROM playlist_arranger WHERE trid=' + str(tutorial[0]))
            tr_log = lcur.fetchone()
            if tr_log and int(tr_log[0]):
                print tutorial[0], '-- Skipping...'
                counter += 1
                continue
            if entry:
                try:
                    playlist_entry = youtube.service.UpdatePlaylistVideoEntryMetaData(
                        playlist_uri, tutorial[13], entry.media.title.text,
                        entry.media.description.text, counter
                    )
                except:
                    error_string = str(tutorial[0]) + str(playlist[3]) + ' -- Error...'
                    error_log_file_head.write(error_string + '\n')
                    print error_string
                    time.sleep(2)
                    continue
                counter += 1
                print str(tutorial[0]) + ' -- Success --' + playlist_entry.id.text.replace(playlist_uri, '').strip('/')
                lcur.execute("INSERT INTO playlist_arranger (trid) VALUES(%s)", [tutorial[0]])
                ldb.commit()
            else:
                error_string = str(tutorial[0]) + ' -- Failed to get video entry'
                error_log_file_head.write(error_string + '\n')
                print error_string
            time.sleep(1)
        #time.sleep(1)
    #time.sleep(1)
error_log_file_head.close()
success_log_file_head.close()
