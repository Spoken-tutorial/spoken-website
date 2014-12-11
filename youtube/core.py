import os
import httplib2

from oauth2client import xsrfutil
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.django_orm import Storage
from oauth2client.client import flow_from_clientsecrets
from django.conf import settings

from youtube.models import *

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
        service.videos().delete(id = video_id).execute()
        return True
    except Exception, e:
        print e
    return None

def delete_playlist(service, playlist_id):
    try:
        service.playlists().delete(id = playlist_id).execute()
        return True
    except Exception, e:
        print e
    return None

def delete_playlistitem(service, playlist_item_id):
    try:
        service.playlistItems().delete(id = playlist_item_id).execute()
        return True
    except Exception, e:
        print e
    return None
