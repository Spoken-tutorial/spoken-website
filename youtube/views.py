
# Standard Library
from builtins import str
import os
import tempfile

# Third Party Stuff
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
#from oauth2client import xsrfutil

# Spoken Tutorial Stuff
from creation.models import *
from creation.views import is_administrator, is_qualityreviewer
from youtube.ajax import *
from youtube.core import *
from youtube.forms import *
from youtube.utils import user_can_upload_to_youtube

YOUTUBE_UPLOAD_SCOPE = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]


@login_required
def add_youtube_video(request):
    """View to upload videos to YouTube via cascading dropdowns."""
    if not user_can_upload_to_youtube(request.user):
        return HttpResponseForbidden("You are not authorized to upload videos.")

    context = {}
    template = 'youtube/templates/add_youtube_video.html'
    
    if request.method == 'GET':
        form = YouTubeUploadForm()
        context['form'] = form
        
    elif request.method == 'POST':
        form = YouTubeUploadForm(request.POST, request.FILES)
        context['form'] = form
        
        if form.is_valid():
            try:
                tutorial_resource_id = form.cleaned_data['tutorial'].id
                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                privacy = form.cleaned_data['privacy_status']
                thumbnail = form.cleaned_data.get('thumbnail')
                playlist_id = form.cleaned_data.get('playlist')
                playlist_position = form.cleaned_data.get('playlist_position')

                # Get Resource and File Path
                resource = TutorialResource.objects.select_related('tutorial_detail__foss').get(id=tutorial_resource_id)
                foss_id = resource.tutorial_detail.foss.id
                detail_id = resource.tutorial_detail.id
                video_dir = os.path.join(settings.MEDIA_ROOT, 'videos', str(foss_id), str(detail_id))
                
                if not os.path.isdir(video_dir):
                    raise Exception("Video directory not found: {}".format(video_dir))

                # Find valid video file
                video_file = None
                for f in os.listdir(video_dir):
                    if f.lower().endswith(('.mp4', '.ogv', '.mov', '.avi')):
                        video_file = os.path.join(video_dir, f)
                        break
                
                if not video_file:
                    raise Exception("No video file found in {}".format(video_dir))

                # Authenticate
                service = get_youtube_credential()
                if not service:
                     redirect_uri = request.build_absolute_uri(reverse('youtube:auth_return'))
                     auth_url = get_auth_url(redirect_uri)
                     messages.error(request, mark_safe(f'YouTube credentials not found. <a href="{auth_url}">Click here to authorize</a>.'))
                     return render(request, template, context)

                # Upload
                options = {
                    'file': video_file,
                    'title': title,
                    'description': description,
                    'privacyStatus': privacy,
                    'tags': []
                }

                result = upload_video(service, options)

                if not result:
                    raise Exception("Upload failed: No response from upload service.")

                if 'error' in result:
                    raise Exception(f"YouTube API Error: {result['error']}")

                if 'id' not in result:
                    if isinstance(result, str):
                         video_id = result
                    else:
                         raise Exception(f"Unexpected API response: {result}")
                else:
                    video_id = result['id']

                # Handle thumbnail upload if provided
                if thumbnail:
                    thumbnail_path = None
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                            for chunk in thumbnail.chunks():
                                tmp.write(chunk)
                            thumbnail_path = tmp.name
                        
                        if set_video_thumbnail(service, video_id, thumbnail_path):
                            messages.info(request, "Thumbnail uploaded successfully.")
                        else:
                            messages.warning(request, "Failed to upload thumbnail.")
                    except Exception as e:
                        messages.warning(request, f"Thumbnail upload skipped: {str(e)}")
                    finally:
                        if thumbnail_path and os.path.exists(thumbnail_path):
                            os.remove(thumbnail_path)

                # Add video to playlist if selected
                if playlist_id:
                    try:
                        playlists = fetch_playlists(service)
                        playlist_ids = [p['id'] for p in playlists]
                        
                        if playlist_id in playlist_ids:
                            playlist_item_id = add_video_to_playlist(service, video_id, playlist_id, playlist_position)
                            if playlist_item_id:
                                resource.playlist_item_id = playlist_item_id
                                position_msg = f" at position {playlist_position}" if playlist_position is not None else " at the end"
                                messages.info(request, f"Video added to playlist{position_msg}.")
                            else:
                                messages.warning(request, "Failed to add video to playlist.")
                        else:
                            messages.warning(request, "Selected playlist not found.")
                    except Exception as e:
                        messages.warning(request, f"Playlist addition failed: {str(e)}")

                # Success
                resource.video_id = video_id
                resource.is_on_youtube = True
                resource.save()

                messages.success(request, f"Successfully uploaded '{title}' to YouTube! (Video ID: {video_id})")
                return HttpResponseRedirect('/software-training/')

            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(request, f"Upload Failed: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    
    return render(request, template, context)

def home(request):
    return HttpResponse('YouTube API V3 Implementation')


def auth_return(request):
    """Callback for Google OAuth2."""
    code = request.GET.get('code', '')
    error = request.GET.get('error', 'Something went wrong!')

    if code:
        try:
            redirect_uri = request.build_absolute_uri(reverse('youtube:auth_return'))
            store_youtube_credential(code, redirect_uri)
            messages.success(request, 'YouTube credentials saved successfully!')
            return HttpResponseRedirect(reverse('youtube:add_youtube_video'))
        except Exception as e:
            error = str(e)
            messages.error(request, 'Failed to save credentials: ' + error)
            return HttpResponseRedirect(reverse('youtube:add_youtube_video'))

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

