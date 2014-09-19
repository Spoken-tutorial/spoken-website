import os
import sys
import logging
import httplib2

from oauth2client import xsrfutil
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.django_orm import Storage
from oauth2client.client import flow_from_clientsecrets

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from youtube.models import *
from creation.models import *
from django.db.models import Q

scope_urls = {
    'readonly': 'https://www.googleapis.com/auth/youtube.readonly',
    'manage': 'https://www.googleapis.com/auth/youtube',
    'upload': 'https://www.googleapis.com/auth/youtube.upload',
}
scope_users = {
    'readonly': User.objects.get(username = 'vishnukraj'),
    'manage': User.objects.get(username = 'sanmugam'),
    'upload': User.objects.get(username = 'nancy'),
}
scope_secrets = {
    'readonly': settings.BASE_DIR + '/' + settings.YOUTUBE_SECRET_FILE_READONLY,
    'manage': settings.BASE_DIR + '/' + settings.YOUTUBE_SECRET_FILE_MANAGE,
    'upload': settings.BASE_DIR + '/' + settings.YOUTUBE_SECRET_FILE_UPLOAD,
}

scope_redirects = {
    'readonly': "/youtube/",
    'manage': "/youtube/",
    'upload': "/youtube/",
}

def test_playlist_add(request):
    flow = flow_from_clientsecrets(
        scope_secrets['manage'],
        scope = scope_urls['manage'],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + 'manage',
    )
    storage = Storage(CredentialsModel, 'id', scope_users['manage'], 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['manage'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
        rows = FossCategory.objects.all()
        for row in rows:
            body = dict(
                snippet = dict(
                    title = row.foss + ' - English',
                    description = row.description
                ),
                status = dict(
                    privacyStatus = 'public'
                )
            )
            playlist_data = create_playlist(service, body)
            if playlist_data:
                print row.foss, '-', playlist_data
            else:
                print row.foss, '- failed'
    return HttpResponse('success')

def test_playlist_delete(request):
    flow = flow_from_clientsecrets(
        scope_secrets['readonly'],
        scope = scope_urls['readonly'],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + 'readonly',
    )
    playlists = []
    storage = Storage(CredentialsModel, 'id', scope_users['readonly'], 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['readonly'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
        activities = service.playlists().list(part = 'snippet', channelId = 'UCHVThOYFWQe_swXqctwYDSg', maxResults = 50).execute()
        
        DEL_flow = flow_from_clientsecrets(
            scope_secrets['manage'],
            scope = scope_urls['manage'],
            redirect_uri = settings.YOUTUBE_REDIRECT_URL + 'manage',
        )
        del_storage = Storage(CredentialsModel, 'id', scope_users['manage'], 'credential')
        del_credential = del_storage.get()
        if del_credential is None or del_credential.invalid == True:
            DEL_flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['manage'])
            del_authorize_url = DEL_flow.step1_get_authorize_url()
            return HttpResponseRedirect(del_authorize_url)
        else:
            del_http = httplib2.Http()
            del_http = del_credential.authorize(del_http)
            del_service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = del_http)
            for playlist in activities['items']:
                print playlist['id']
                delete_playlist(del_service, playlist['id'])
    return HttpResponse('success')

def test_upload_video(request):
    flow = flow_from_clientsecrets(
        scope_secrets['upload'],
        scope = scope_urls['upload'],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + 'upload',
    )
    storage = Storage(CredentialsModel, 'id', scope_users['upload'], 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['upload'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
        tr_rows = TutorialResource.objects.filter(Q(status = 1) | Q(status = 2), tutorial_detail__foss__foss = 'KiCad', language__name = 'English')
        for row in tr_rows:
            body=dict(
                snippet=dict(
                    title = row.tutorial_detail.tutorial + ' - English',
                    description = row.outline,
                    tags = row.common_content.keyword.split(','),
                    categoryId = 27
                ),
                status = dict(
                    privacyStatus = 'unlisted',
                    license = 'creativeCommon',
                    embeddable = True
                )
            )
            file_path = settings.MEDIA_ROOT + 'videos/' + str(row.tutorial_detail.foss_id) + '/' + str(row.tutorial_detail_id) + '/' + row.video
            result = upload_video(service, body, file_path)
            if result:
                print row.tutorial_detail.tutorial, ' - Success - ', result['id']
            else:
                print row.tutorial_detail.tutorial, ' - Failed'
    return HttpResponse('Success')

def test_delete_video(request):
    flow = flow_from_clientsecrets(
        scope_secrets['manage'],
        scope = scope_urls['manage'],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + 'manage',
    )
    storage = Storage(CredentialsModel, 'id', scope_users['manage'], 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['manage'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
        result = delete_video(service, '0zwJgYLSQjU')
        if result:
            return HttpResponse('Success')
    return HttpResponse('Failed')

def test_add_playlist_item(request):
    flow = flow_from_clientsecrets(
        scope_secrets['manage'],
        scope = scope_urls['manage'],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + 'manage',
    )
    storage = Storage(CredentialsModel, 'id', scope_users['manage'], 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['manage'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
        body = dict(
            snippet = dict(
                playlistId = 'PLbNvy7cG5Yt5v8Na9z3cF3wUfiAb18GWn',
                position = 1,
                resourceId = dict(
                    kind = 'youtube#video',
                    videoId = 'tk69JFcNhJA'
                )
            )
        )
        if not get_playlistitem(service, 'PLbNvy7cG5Yt5v8Na9z3cF3wUfiAb18GWn', 'tk69JFcNhJA'):
            result = add_playlistitem(service, body)
        else:
            return HttpResponse('Video already available in playlist...')
        if result:
            return HttpResponse('success')
    return HttpResponse('failed')

def test_list_videos(request):
    flow = flow_from_clientsecrets(
        scope_secrets['readonly'],
        scope = scope_urls['readonly'],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + 'readonly',
    )
    playlists = []
    storage = Storage(CredentialsModel, 'id', scope_users['readonly'], 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['readonly'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
        activities = service.channels()
        activitylist = activities.list(mine = True, part = "contentDetails").execute()
        logging.info(activitylist)
        for channel in activitylist["items"]:
            uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
            print "Videos in list %s" % uploads_list_id
            playlistitems_list_request = service.playlistItems().list(
                playlistId = uploads_list_id,
                part = "snippet",
                maxResults = 50
            ).execute()
            playlists.append(playlistitems_list_request)
    context = {
        'playlists': playlists
    }
    return render(request, 'youtube/templates/home.html', context)

def get_storage_flow_secret(scope):
    flow = flow_from_clientsecrets(
        scope_secrets[scope],
        scope = scope_urls[scope],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + scope,
    )
    storage = Storage(CredentialsModel, 'id', scope_users[scope], 'credential')
    credential = storage.get()
    return flow, credential

def home(request):
    # readonly authentication part
    flow, credential = get_storage_flow_secret('readonly')
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['readonly'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)

    # manage authentication part
    flow, credential = get_storage_flow_secret('manage')
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['manage'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)

    # upload authentication part
    flow, credential = get_storage_flow_secret('upload')
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['upload'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)

    return HttpResponse('Authentication process completed successfully!')

def cron_foss_playlist(request):
    # manage authentication part
    flow, credential = get_storage_flow_secret('manage')
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['manage'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
        foss_rows = FossCategory.objects.filter(foss = 'KiCad')
        for foss_row in foss_rows:
            lang_rows = Language.objects.filter(id__in = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss_id = foss_row.id).values_list('language_id').distinct()).exclude(id__in = PlaylistInfo.objects.filter(foss_id = foss_row.id).values_list('language_id'))
            for lang_row in lang_rows:
                body = dict(
                    snippet = dict(
                        title = foss_row.foss + ' - ' + lang_row.name,
                        description = foss_row.description
                    ),
                    status = dict(
                        privacyStatus = 'public'
                    )
                )
                result = create_playlist(service, body)
                if result and ('id' in result) and result['id']:
                    PlaylistInfo.objects.create(foss_id = foss_row.id, language_id = lang_row.id, playlist_id = result['id'])
                    print foss_row.foss, lang_row.name, '-', result['id']
                else:
                    print foss_row.foss, lang_row.name, '- Failed'
    return HttpResponse('success')

def cron_add_video(request):
    # manage authentication part
    manage_flow, manage_credential = get_storage_flow_secret('manage')
    if manage_credential is None or manage_credential.invalid == True:
        manage_flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['manage'])
        authorize_url = manage_flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        manage_http = httplib2.Http()
        manage_http = manage_credential.authorize(manage_http)
        manage_service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = manage_http)

    # upload authentication part
    flow, credential = get_storage_flow_secret('upload')
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['upload'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    else:
        http = httplib2.Http()
        http = credential.authorize(http)
        service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
        rows = TutorialResource.objects.filter(Q(status = 1)|Q(status = 2), tutorial_detail__foss__foss = 'KiCad', video_id=None).order_by('tutorial_detail__foss__foss', 'tutorial_detail__level', 'tutorial_detail__order')
        for row in rows:
            try:
                playlist = PlaylistInfo.objects.get(foss_id = row.tutorial_detail.foss_id, language_id = row.language_id)
            except Exception, e:
                print row.tutorial_detail.foss, ':', row.tutorial_detail.tutorial, row.language.name, ' - Playlist Missing'
                continue
            body=dict(
                snippet=dict(
                    title = row.tutorial_detail.tutorial + ' - ' + row.language.name,
                    description = row.outline,
                    tags = row.common_content.keyword.split(','),
                    categoryId = 27
                ),
                status = dict(
                    privacyStatus = 'unlisted',
                    license = 'creativeCommon',
                    embeddable = True
                )
            )
            file_path = settings.MEDIA_ROOT + 'videos/' + str(row.tutorial_detail.foss_id) + '/' + str(row.tutorial_detail_id) + '/' + row.video
            result = upload_video(service, body, file_path)
            if result and ('id' in result) and result['id']:
                row.video_id = result['id']
                body = dict(
                    snippet = dict(
                        playlistId = playlist.playlist_id,
                        resourceId = dict(
                            kind = 'youtube#video',
                            videoId = result['id']
                        )
                    )
                )
                item_result = add_playlistitem(manage_service, body)
                if item_result and ('id' in item_result) and item_result['id']:
                    try:
                        row.playlist_item_id = item_result['id']
                        PlaylistItem.objects.create(playlist_id = playlist.id, item_id = item_result['id'])
                    except:
                        print row.tutorial_detail.foss, ':', row.tutorial_detail.tutorial, row.language.name, ' - Failed save item'
                        pass
                    row.playlist_item_id = item_result['id']
                else:
                    print row.tutorial_detail.foss, ':', row.tutorial_detail.tutorial, row.language.name, ' - Failed add item'
                row.save()
                print row.tutorial_detail.foss, ':', row.tutorial_detail.tutorial, row.language.name, result['id']
            else:
                print row.tutorial_detail.foss, ':', row.tutorial_detail.tutorial, row.language.name, ' - Failed'
    return HttpResponse('success')

def create_playlist(service, body):
    try:
        playlist_insert_response = service.playlists().insert(
            part = ",".join(body.keys()),
            body = body
        ).execute()
        return playlist_insert_response
    except Exception, e:
        pass
    return None

def delete_playlist(service, playlist_id):
    try:
        playlist_delete_response = service.playlists().delete(id = playlist_id).execute()
        return playlist_delete_response
    except Exception, e:
        pass
    return None

def update_playlist(service, body):
    try:
        playlist_update_response = service.playlists().update(
            part = ",".join(body.keys()),
            body = body
        ).execute()
        return playlist_update_response
    except Exception, e:
        pass
    return None

def resumable_upload(insert_request):
    response = None
    while response is None:
        try:
            print "Uploading file..."
            status, response = insert_request.next_chunk()
            if 'id' in response:
                # print "Video id '%s' was successfully uploaded." % response['id']
                return response
        except Exception, e:
            return False
    return False

def upload_video(service, body, file_path):
    insert_request = service.videos().insert(
        part = ",".join(body.keys()),
        body = body,
        media_body = MediaFileUpload(file_path, chunksize = -1, resumable = True)
    )
    return resumable_upload(insert_request)

def delete_video(service, video_id):
    try:
        result = service.videos().delete(id = video_id).execute()
        return True
    except Exception, e:
        pass
    return False

def update_video_info(service, body):
    try:
        update_request = service.videos().update(
            part = ",".join(body.keys()),
            body = body
        ).execute()
        if update_request:
            return update_request
    except Exception, e:
        pass
    return False

def add_playlistitem(service, body):
    try:
        result = service.playlistItems().insert(
            part = ",".join(body.keys()),
            body = body
        ).execute()
        if result:
            return result
    except Exception, e:
        print e
        pass
    return False

def update_playlistitem(service, body):
    try:
        result = service.playlistItems().update(
            part = ",".join(body.keys()),
            body = body
        ).execute()
        if result:
            return result
    except Exception, e:
        print e
        pass
    return False

def delete_playlistitem(service, item_id):
    try:
        result = service.playlistItems().delete(id = item_id).execute()
        return True
    except Exception, e:
        pass
    return False

def get_playlistitem(service, playlist_id, video_id):
    try:
        playlistitems = service.playlistItems().list(
            playlistId = playlist_id,
            videoId = video_id,
            part = "snippet"
        ).execute()
        if playlistitems['pageInfo']['totalResults']:
            return playlistitems
    except Exception, e:
        print e
        pass
    return False

def auth_return(request, scope):
    if not scope in scope_urls:
        return  HttpResponseBadRequest()
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], scope_users[scope]):
        return  HttpResponseBadRequest()
    flow = flow_from_clientsecrets(
        scope_secrets[scope],
        scope = scope_urls[scope],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + scope,
    )
    credential = flow.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'id', scope_users[scope], 'credential')
    storage.put(credential)
    return HttpResponseRedirect(scope_redirects[scope])
