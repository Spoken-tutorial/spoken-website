import subprocess
import MySQLdb
import os
import time
from config import *

def convert_tmp_video(src_path, dst_path):
    stdout = None
    stderr = None
    """mffmpeg -i input-file.ogv -strict experimental -pix_fmt yuv420p -r 15 -f mp4 tmp.mp4"""
    print "/usr/bin/mffmpeg -i", src_path, "-strict experimental -pix_fmt yuv420p -r 15 -f mp4", dst_path
    process = subprocess.Popen(
        [
            '/usr/bin/mffmpeg',
            '-i', src_path,
            '-strict', 'experimental',
            '-pix_fmt', 'yuv420p',
            '-r', '15',
            '-f', 'mp4',
            dst_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, stderr = process.communicate()
    return stdout, stderr

def convert_video(src_path, dst_path):
    stdout = None
    stderr = None
    """ffmpeg -i Hardware-requirement-to-install-Blender-English.ogv -acodec libfaac -ac 2 -ab 160k -vcodec libx264 -vpre fast -f mp4 Hardware-requirement-to-install-Blender-English.mp4"""
    """ffmpeg -i Registration-of-an-account-for-online-train-ticket-booking-English.ogv -strict experimental -vcodec libx264 -acodec libfaac -vpre fast -f mp4 Registration-of-an-account-for-online-train-ticket-booking-English.mp4"""
    """ffmpeg -i tmp.mp4 -strict experimental -vcodec libx264 -vpre default -f mp4 output.mp4"""
    print "/usr/bin/ffmpeg -i", src_path, "-strict experimental -vcodec libx264 -vpre default -f mp4", dst_path
    process = subprocess.Popen(
        [
            '/usr/bin/ffmpeg',
            '-i', src_path,
            '-strict', 'experimental',
            '-vcodec', 'libx264',
            '-vpre', 'default',
            '-f', 'mp4',
            dst_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, stderr = process.communicate()
    return stdout, stderr


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
error_log_file_head1 = open(LOG_ROOT + 'create-missing-mp4-conversion-errors.txt',"w")
error_log_file_head2 = open(LOG_ROOT + 'create-missing-mp4-notfound-errors.txt',"w")
for row in rows:
    print row[5]
    ogv_video_path = MEDIA_ROOT + 'videos/' + str(row[8]) + '/' + str(row[1]) + '/' + row[5]
    mp4_video_path, file_extension = os.path.splitext(ogv_video_path)
    mp4_tmp_video_path = mp4_video_path + '-tmp.mp4'
    mp4_video_path = mp4_video_path + '.mp4'
    if os.path.isfile(mp4_video_path):
        if not os.path.getsize(mp4_video_path):
            print 'Converting video...'
            stdout, stderr = convert_tmp_video(ogv_video_path, mp4_tmp_video_path)
            print 'Stdout: ', stdout
            print 'Stderr: ', stderr
            stdout, stderr = convert_video(mp4_tmp_video_path, mp4_video_path)
            print 'Stdout: ', stdout
            print 'Stderr: ', stderr
            os.remove(mp4_tmp_video_path)
            error_log_file_head1.write(mp4_video_path + ', Conversion Error' + '\n')
    else:
        print 'Converting video...'
        stdout, stderr = convert_tmp_video(ogv_video_path, mp4_tmp_video_path)
        print 'Stdout: ', stdout
        print 'Stderr: ', stderr
        stdout, stderr = convert_video(mp4_tmp_video_path, mp4_video_path)
        print 'Stdout: ', stdout
        print 'Stderr: ', stderr
	try:
            os.remove(mp4_tmp_video_path)
	except:
            pass
        error_log_file_head2.write(mp4_video_path + ', File not found' + '\n')
error_log_file_head1.close()
error_log_file_head2.close()
