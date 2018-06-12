import MySQLdb
import time
import sys
#sys.path.insert(0, '../spoken')
#sys.path.insert(0, '../../spoken')
from youtube_upload import *
from config import *

def convert_video(path):
    file_name, file_extension = os.path.splitext(path)
    try:
        """ffmpeg -i Hardware-requirement-to-install-Blender-English.ogv -acodec libfaac -ac 2 -ab 160k -vcodec libx264 -vpre fast -f mp4 Hardware-requirement-to-install-Blender-English.mp4"""
        new_path, extension = os.path.splitext(path)
        new_path = new_path + '.mp4'
        process = subprocess.Popen(
            [
                '/usr/bin/ffmpeg',
                '-i', path,
                '-acodec', 'libfaac',
                '-ac', '2',
                '-ab', '160k',
                '-vcodec', 'libx264',
                '-vpre', 'fast',
                '-f', 'mp4',
                new_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
        return new_path
    except:
        pass
    return False

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
    ((ctr.status = 1 OR ctr.status = 2) AND ctr.video_id IS NULL) ORDER BY \
    cfc.foss, ctd.level_id, ctd.order ASC")
rows = cur.fetchall()
error_log_file_head = open(LOG_ROOT + 'video-error-log.txt',"w")
success_log_file_head = open(LOG_ROOT + 'video-success-log.txt',"w")
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
    video_path = MEDIA_ROOT + 'videos/' + str(row[8]) + '/' + str(row[1]) + '/' + row[5]
    video_path = convert_video(video_path)
    if not os.path.isfile(video_path):
        error_string = row[9] + ' - ' + row[13] + ' -- Conversion Error'
        error_log_file_head.write(error_string + '\n')
        continue
    options = {
        'title': row[9] + ' - ' + row[13],
        'description': to_utf8(row[4]),
        'keywords': row[12],
        'category': 'Education',
        'private': False,
        'location': None,
        'unlisted': False
    }
    video_id = upload_video(youtube, options, video_path)
    if video_id:
        cur.execute("UPDATE creation_tutorialresource SET video_id='%s' WHERE id=%s" % (video_id, row[0]))
        item_id = youtube.add_video_to_playlist(video_id, playlist[3])
        if item_id:
            currtime = time.strftime('%Y-%m-%d %H:%M:%S')
            cur.execute("UPDATE creation_tutorialresource SET playlist_item_id='%s' WHERE id=%s" % (item_id, row[0]))
            cur.execute("INSERT INTO creation_playlistitem (playlist_id, item_id, created, updated) VALUES('%s', '%s', '%s', '%s')" % (playlist[0], item_id, currtime, currtime))
        else:
            print 'Playlist item missing...'
        db.commit()
        success_string = row[9] + ' - ' + row[13] + ' -- ' + video_id
        success_log_file_head.write(success_string + '\n')
        print success_string
    else:
        error_string = row[9] + ' - ' + row[13] + ' -- Failed'
        error_log_file_head.write(error_string + '\n')
        print error_string
error_log_file_head.close()
success_log_file_head.close()
