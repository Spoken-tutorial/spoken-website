import MySQLdb
import time
import sys
#sys.path.insert(0, '../spoken')
#sys.path.insert(0, '../../spoken')
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
cur.execute("SELECT * FROM creation_fosscategory ORDER BY foss")
rows = cur.fetchall()
error_log_file_head = open(LOG_ROOT + 'playlist-error-log.txt',"w")
success_log_file_head = open(LOG_ROOT + 'playlist-success-log.txt',"w")
for row in rows:
    cur.execute("SELECT creation_language.id, creation_language.name FROM \
        creation_language WHERE (creation_language.id IN (SELECT DISTINCT \
        U0.language_id FROM creation_tutorialresource U0 INNER JOIN \
        creation_tutorialdetail U1 ON ( U0.tutorial_detail_id = U1.id ) \
        WHERE ((U0.status = 1  OR U0.status = 2 ) AND U1.foss_id = %s )) \
        AND NOT (creation_language.id IN (SELECT U0.language_id FROM \
        creation_playlistinfo U0 WHERE U0.foss_id = %s ))) ORDER BY \
        creation_language.name ASC" % (row[0], row[0]))
    langrows = cur.fetchall()
    for langrow in langrows:
        title = row[1] + ' - ' + langrow[1]
        playlistid = youtube.create_playlist(title, row[2])
        if playlistid:
            currtime = time.strftime('%Y-%m-%d %H:%M:%S')
            sql = """INSERT INTO creation_playlistinfo (foss_id, language_id, \
                playlist_id, created, updated) VALUES(%d, %d, '%s', '%s', \
                '%s')""" % (row[0], langrow[0], playlistid, currtime, currtime)
            cur.execute(sql)
            db.commit()
            success_string = row[1] + ' - ' + langrow[1] + ' -- ' + playlistid
            success_log_file_head.write(success_string + '\n')
            print success_string
        else:
            error_string = row[1] + ' - ' + langrow[1] + ' -- FAILED'
            error_log_file_head.write(error_string + '\n')
            print error_string
error_log_file_head.close()
success_log_file_head.close()
