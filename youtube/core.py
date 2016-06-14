# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Third Party Stuff
from apiclient.http import MediaFileUpload
from django.conf import settings
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage

# Spoken Tutorial Stuff
from youtube.models import *

scope_urls = {
    'readonly': 'https://www.googleapis.com/auth/youtube.readonly',
    'manage': 'https://www.googleapis.com/auth/youtube',
    'upload': 'https://www.googleapis.com/auth/youtube.upload',
}

scope_users = {
    'readonly': User.objects.get(username='vishnukraj'),
    'manage': User.objects.get(username='sanmugam'),
    'upload': User.objects.get(username='nancy'),
}

scope_secret = settings.BASE_DIR + '/' + settings.YOUTUBE_SECRET_FILE


def get_storage_flow_secret(scope):
    flow = flow_from_clientsecrets(
        scope_secret,
        scope=scope_urls[scope],
        redirect_uri=settings.YOUTUBE_REDIRECT_URL + scope,
    )
    storage = Storage(CredentialsModel, 'id', scope_users[scope], 'credential')
    credential = storage.get()
    return flow, credential


def upload_video(service, options):
    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=options.tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(
            options.file,
            chunksize=-1,
            resumable=False
        )
    )
    response = None
    try:
        status, response = insert_request.next_chunk()
        if 'id' in response:
            return True, response
    except:
        pass
    return False, response


def delete_video(service, video_id):
    try:
        service.videos().delete(id=video_id).execute()
        return True
    except Exception as e:
        print(e)
    return None


def delete_playlist(service, playlist_id):
    try:
        service.playlists().delete(id=playlist_id).execute()
        return True
    except Exception as e:
        print(e)
    return None


def delete_playlistitem(service, playlist_item_id):
    try:
        service.playlistItems().delete(id=playlist_item_id).execute()
        return True
    except Exception as e:
        print(e)
    return None
