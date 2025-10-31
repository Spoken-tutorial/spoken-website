
# Standard Library
from builtins import str
import os

# Third Party Stuff
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
#from oauth2client import xsrfutil

# Spoken Tutorial Stuff
from creation.models import *
from creation.views import is_administrator, is_qualityreviewer
from youtube.ajax import *
from youtube.core import *
from youtube.forms import *

YOUTUBE_UPLOAD_SCOPE = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]


@login_required
def home(request):
    return HttpResponse('YouTube API V3 Implementation')


def auth_return(request):
    # print request.REQUEST['state']
    # if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], 0):
    #     return HttpResponseForbidden('Access Denied!')

    code = request.GET.get('code', '')
    error = request.GET.get('error', 'Something went wrong!')

    if code:
        try:
            store_youtube_credential(code)
            return HttpResponse('Youtube auth token updated successfully!')
        except Exception as e:
            error = str(e)

    return HttpResponse(error)


@login_required
def delete_all_videos(request):
    service = get_youtube_credential()

    if service is None:
        return HttpResponse("Youtube auth token expired! We've sent an email with URL to update auth token.")

    rows = TutorialResource.objects.all().exclude(Q(video_id=None) | Q(video_id=''))
    for row in rows:
        result = delete_video(service, row.video_id)
        if row.playlist_item_id is not None and row.playlist_item_id != '':
            delete_playlistitem(service, row.playlist_item_id)
        if result is not None:
            print((row.video_id, 'deleted'))
        else:
            print((row.video_id, 'not deleted'))
    return HttpResponse('Videos deletion process completed!!!')


@login_required
def remove_youtube_video(request):
    if (not is_administrator(request.user)) and (not is_qualityreviewer(request.user)):
        raise PermissionDenied()
    form = YoutubeVideoSelectForm()
    if request.method == 'POST':
        form = YoutubeVideoSelectForm(request.POST)
        if form.is_valid():
            tdid = request.POST.get('tutorial_name', 0)
            lgid = request.POST.get('language', 0)
            if tdid and lgid:
                return HttpResponseRedirect('/youtube/remove-video-entry/' + str(tdid) + '/' + str(lgid) + '/')
            else:
                messages.error('Something went wrong!')
    context = {
        'form': form,
    }
    return render(request, 'youtube/templates/remove_youtube_video.html', context)


@login_required
def remove_video_entry(request, tdid, lgid):
    if (not is_administrator(request.user)) and (not is_qualityreviewer(request.user)):
        raise PermissionDenied()
    try:
        tr_rec = TutorialResource.objects.get(tutorial_detail_id=tdid, language_id=lgid)
        if tr_rec.video_id:
            service = get_youtube_credential()

            if service is None:
                messages.error(
                    "Youtube auth token expired! We've sent an email with URL to update auth token.")
                return HttpResponseRedirect('/youtube/remove-youtube-video/')

            result = delete_video(service, tr_rec.video_id)

            if result:
                tr_rec.video_id = None
                if tr_rec.playlist_item_id:
                    delete_playlistitem(service, tr_rec.playlist_item_id)
                    video_path, file_extension = os.path.splitext(tr_rec.video)
                    video_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/' + video_path + '.mp4'
                    if os.path.isfile(video_path):
                        os.remove(video_path)
                    try:
                        playlist_item = PlaylistItem.objects.get(item_id=tr_rec.playlist_item_id)
                        playlist_item.delete()
                        tr_rec.playlist_item_id = None
                    except:
                        pass
                tr_rec.save()
                messages.success(
                    request,
                    tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name + ' <b>video removed from youtube ...</b>'
                )
            else:
                messages.success(request, 'Something went wrong, please contact site administrator.')
        else:
            messages.error('Video ID missing!')
    except:
        messages.error(request, 'Invalid tutorial id ...')
    return HttpResponseRedirect('/youtube/remove-youtube-video/')
