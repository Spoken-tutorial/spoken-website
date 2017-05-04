import os
import time

from django.db.models import Q
from django.conf import settings

from creation.models import *
from youtube.core import *
from youtube.utils import *


def upload_videos():
    service = get_youtube_credential()

    if service is None:
        return

    tresource_list = TutorialResource.objects.filter(Q(status=1) | Q(status=2), video_id=None).select_related()
    error_log_file_head = open('{}logs/youtube-error.log'.format(settings.BASE_DIR),"w")
    success_log_file_head = open('{}logs/youtube-success.log'.format(settings.BASE_DIR),"w")

    for tresource in tresource_list:
        try:
            ogv_video_path =  + '{}videos/{}/{}/{}'.format(
                settings.MEDIA_ROOT, tresource.tutorial_detail.foss_id, tresource.tutorial_detail_id, tresource.video)
            mp4_video_path, file_extn = os.path.splitext(ogv_video_path)
            mp4_tmp_video_path = mp4_video_path + '-tmp.mp4'
            mp4_video_path = mp4_video_path + '.mp4'
            title_string = '{} - {}'.format(tresource.tutorial_detail.tutorial, tresource.language.name)

            if not os.path.isfile(mp4_video_path):
                convert_tmp_video(ogv_video_path, mp4_tmp_video_path)
                convert_video(mp4_tmp_video_path, mp4_video_path)
                if not os.path.isfile(mp4_video_path) or not os.path.getsize(mp4_video_path):
                    print tresource.tutorial_detail.tutorial, '-', tresource.language.name, '-- MP4 video missing'
                    continue

            options = {
                'title': title_string,
                'description': tresource.outline,
                'tags': tresource.common_content.keyword.split(','),
                'file': mp4_video_path
            }

            try:
                video_id = upload_video(service, options)
            except:
                video_id = None

            if video_id:
                tresource.video_id = video_id
                tresource.save()
                success_log_file_head.write('upload_video, {}, {}, {}\n'.format(tresource.id, title_string, video_id))
            else:
                error_log_file_head.write('upload_video, {}, {}\n'.format(tresource.id, title_string))

            time.sleep(1)
        except Exception as e:
            error_log_file_head.write('upload_video, {}, {}\n'.format(tresource.id, str(e)))


def create_playlists():
    service = get_youtube_credential()

    if service is None:
        return

    foss_list = FossCategory.objects.all()

    for foss_obj in foss_list:
        tr_lang_list = TutorialResource.objects.filter(
            Q(status=1) | Q(status=2),
            tutorial_detail.foss_id=foss_obj.id).values_list('language_id').distinct()
        lang_list = Language.objects.filter(id__in=tr_lang_list).exclude(
            id__in=PlaylistInfo.objects.filter(foss_id=foss_obj.id))

        for lang_obj in lang_list:
            title = '{} - {}'.format(foss_obj.foss, lang_obj.name)
            playlist_id = create_playlist(service, title, foss_obj.description)

            if playlist_id:
                playlist_obj = PlaylistInfo.objects.create(
                    foss=foss_obj, language=lang_obj, playlist_id=playlist_id)
