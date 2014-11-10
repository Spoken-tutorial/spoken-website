import os
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

scope_secret = settings.BASE_DIR + '/' + settings.YOUTUBE_SECRET_FILE

def get_storage_flow_secret(scope):
    flow = flow_from_clientsecrets(
        scope_secret,
        scope = scope_urls[scope],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + scope,
    )
    storage = Storage(CredentialsModel, 'id', scope_users[scope], 'credential')
    credential = storage.get()
    return flow, credential

def delete_video(service, video_id):
    try:
        result = service.videos().delete(id = video_id).execute()
        return result
    except Exception, e:
        print e
    return None

def delete_playlist(service, playlist_id):
    try:
        result = service.playlists().delete(id = playlist_id).execute()
        return playlist_delete_response
    except Exception, e:
        print e
    return None

def delete_playlistitem(service, playlist_item_id):
    try:
        result = service.playlistItems().delete(id = playlist_item_id).execute()
        return result
    except Exception, e:
        print e
    return None

@login_required
def home(request):
    return HttpResponse('YouTube API V3 Implementation')

@login_required
def delete_all_videos(request):
    flow, credential = get_storage_flow_secret('manage')
    if credential is None or credential.invalid == True:
        flow.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY, scope_users['manage'])
        authorize_url = flow.step1_get_authorize_url()
        return HttpResponseRedirect(authorize_url)
    http = httplib2.Http()
    http = credential.authorize(http)
    service = build(settings.YOUTUBE_API_SERVICE_NAME, settings.YOUTUBE_API_VERSION, http = http)
    rows = TutorialResource.objects.all().exclude(Q(video_id = None) | Q(video_id = ''))
    for row in rows:
        result = delete_video(service, row.video_id)
        if row.playlist_item_id != None and row.playlist_item_id != '':
            delete_playlistitem(service, row.playlist_item_id)
        if result != None:
            print row.video_id, 'deleted'
        else:
            print row.video_id, 'not deleted'
    return HttpResponse('Videos deletion process completed!!!')

@login_required
def auth_return(request, scope):
    if not scope in scope_urls:
        return  HttpResponseBadRequest()
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'], scope_users[scope]):
        return  HttpResponseBadRequest()
    flow = flow_from_clientsecrets(
        scope_secret,
        scope = scope_urls[scope],
        redirect_uri = settings.YOUTUBE_REDIRECT_URL + scope,
    )
    credential = flow.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'id', scope_users[scope], 'credential')
    storage.put(credential)
    return HttpResponseRedirect('/youtube/')
