
# Standard Library
import os
import subprocess


def convert_tmp_video(src_path, dst_path):
    stdout = None
    stderr = None
    """ffmpeg -i input-file.webm -strict experimental -pix_fmt yuv420p -r 15 -f mp4 tmp.mp4"""
    print(("/usr/bin/ffmpeg -i", src_path, "-strict experimental -pix_fmt yuv420p -r 15 -f mp4", dst_path))
    process = subprocess.Popen(
        [
            '/usr/bin/ffmpeg',
            '-nostdin', '-hide_banner', '-nostats', '-y',
            '-i', src_path,
            '-strict', 'experimental',
            '-pix_fmt', 'yuv420p',
            '-r', '15',
            '-f', 'mp4',
            dst_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr

def convert_video(src_path, dst_path):
    stdout = None
    stderr = None
    """ffmpeg -i Hardware-requirement-to-install-Blender-English.webm -acodec libfaac -ac 2 -ab 160k -vcodec libx264 -vpre fast -f mp4 Hardware-requirement-to-install-Blender-English.mp4"""
    """ffmpeg -i Registration-of-an-account-for-online-train-ticket-booking-English.webm -strict experimental -vcodec libx264 -acodec libfaac -vpre fast -f mp4 Registration-of-an-account-for-online-train-ticket-booking-English.mp4"""
    """ffmpeg -i tmp.mp4 -strict experimental -vcodec libx264 -vpre default -f mp4 output.mp4"""
    print(("/usr/bin/ffmpeg -i", src_path, "-max_muxing_queue_size 512 -strict experimental -vcodec libx264 -vpre default -f mp4", dst_path))
    process = subprocess.Popen(
        [
            '/usr/bin/ffmpeg',
            '-nostdin', '-hide_banner', '-nostats', '-y',
            '-i', src_path,
            '-max_muxing_queue_size', '512',
            '-strict', 'experimental',
            '-vcodec', 'libx264',
            '-f', 'mp4',
            dst_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    stdout, stderr = process.communicate()

    try:
        os.remove(src_path)
    except:
        pass

    return stdout, stderr
