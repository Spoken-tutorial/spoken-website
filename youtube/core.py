import httplib2
import oauth2client
import googleapiclient.discovery

from apiclient.http import MediaFileUpload
from django.conf import settings

# Spoken Tutorial Stuff
from youtube.models import *

youtube_scope_urls = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]
client_secrets_file = os.path.join(settings.BASE_DIR, 'youtube', '.client_secrets.json')
credentials_file = os.path.join(settings.BASE_DIR, 'youtube', '.youtube-upload-credentials.json')


def to_utf8(s):
    """Re-encode string from the default system encoding to UTF-8."""
    current = locale.getpreferredencoding()
    return (s.decode(current).encode("UTF-8") if s and current != "UTF-8" else s)


def get_flow():
    flow = oauth2client.client.flow_from_clientsecrets(client_secrets_file, scope=youtube_scope_urls)
    flow.redirect_uri = settings.YOUTUBE_REDIRECT_URL
    flow.params['state'] = oauth2client.xsrfutil.generate_token(settings.SECRET_KEY, 1)
    return flow


def get_storage():
    return oauth2client.file.Storage(credentials_file)


def get_youtube_credential():
    storage = get_storage()
    credential = storage.get()

    if credential and not credential.invalid:
        try:
            http = credential.authorize(httplib2.Http())
            return googleapiclient.discovery.build("youtube", "v3", http=http)
        except Exception as e:
            print e
            return None

    return None


def get_auth_url()
    flow = get_flow()
    return flow.step1_get_authorize_url()


def store_youtube_credential(code):
    flow = get_flow()
    storage = get_storage()
    credential = flow.step2_exchange(code, http=None)
    storage.put(credential)
    # credential.set_store(storage)


def upload_video(service, options):
    body = dict(
        snippet=dict(
            title=to_utf8(options.get('title')),
            description=to_utf8(options.get('description') or "").decode("string-escape"),
            tags=options.get('tags'),
            categoryId=27
        ),
        status=dict(
            privacyStatus='public'
        )
    )
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(
            options.get('file'),
            chunksize=-1,
            resumable=False
        )
    )
    response = None

    try:
        status, response = insert_request.next_chunk()
        if 'id' in response:
            return response['id']
    except Exception as e:
        print e

    return None


def create_playlist(service, title, description):
    try:
        body = dict(
            snippet=dict(
                title=to_utf8(title),
                description=to_utf8(description)
            ),
            status=dict(
                privacyStatus="private"
            )
        )
        playlist = youtube.playlists().insert(
            part=",".join(body.keys()),
            body=body
        ).execute()

        if playlist and 'id' in playlist:
            return playlist['id']
    except Exception as e:
        print e

    return None


def add_to_playlist(service, video_id, playlist_id, position=0):
    try:
        body = dict(
            snippet=dict(
                playlistId=playlist_id,
                resourceId=video_id
            )
        )

        if position:
            body['snippet']['position'] = position

        playlist_item = youtube.playlistItems().insert(
            part=",".join(body.keys()),
            body=body
        ).execute()

        if playlist_item and 'id' in playlist_item:
            return playlist_item['id']
    except Exception as e:
        print e

    return None


def delete_video(service, video_id):
    try:
        service.videos().delete(id=video_id).execute()
        return True
    except Exception, e:
        print e
    return None


def delete_playlist(service, playlist_id):
    try:
        service.playlists().delete(id=playlist_id).execute()
        return True
    except Exception, e:
        print e
    return None


def delete_playlistitem(service, playlist_item_id):
    try:
        service.playlistItems().delete(id=playlist_item_id).execute()
        return True
    except Exception, e:
        print e
    return None
