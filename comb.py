import httplib
import httplib2
import os
import sys
import random
import time
import django



from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
from oauth2client.tools import argparser, run_flow


from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spoken.settings")
application = get_wsgi_application()

'''from spoken import settings
from django.core.management import setup_environ
setup_environ(settings)'''

from creation.models import *


httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
CLIENT_SECRETS_FILE = "/home/abhinav/Desktop/youtube_work/spoken-website/client_secret.json"
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_SCOPE=[YOUTUBE_READ_WRITE_SCOPE,YOUTUBE_UPLOAD_SCOPE]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
MISSING_CLIENT_SECRETS_MESSAGE = ""

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


video_id = "NULL"

def get_authenticated_service(args):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
        scope=YOUTUBE_SCOPE,
        message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body=dict(
        snippet=dict(
        title=options.title,
        description=options.description,
        tags=tags,
        categoryId=options.category
        ),
        status=dict(
        privacyStatus=options.privacyStatus
        )
    )
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

def resumable_upload(insert_request):
    global video_id
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print "Uploading file..."
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print "Video id '%s' was successfully uploaded." % response['id']
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError, e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                    e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS, e:
            error = "Error : A retriable error occurred: %s" % e

        if error is not None:
            print error
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print "Sleeping %f seconds and then retrying..." % sleep_seconds
        time.sleep(sleep_seconds)
    video_id = response['id']


def check_response(response,playlist):
    for i in range(0,len(response["items"])):
        if response["items"][i]["snippet"]["title"] == playlist:
            return response["items"][i]["id"], response["items"][i]["contentDetails"]["itemCount"]
    return "", 0

def check_playlist(youtube,playlist):
    maxResults = 50
    requests = youtube.playlists().list(
        part='snippet,contentDetails',
        channelId = 'UCg1uGZFAp-oW3RiSp5h9ZQw',
        maxResults = maxResults
    )
    while requests:
        response = requests.execute()
        playlist_id, position = check_response(response,playlist)
        if playlist_id:
            return playlist_id, position
        requests = youtube.playlistItems().list_next(requests, response)
    return "", 0


def add_playlist(youtube, playlist):
    print "adding playlist"
    playlist_id, position = check_playlist(youtube,playlist)
    print "playlist",playlist_id
    if playlist_id:
        print "playlist already exists"
        return playlist_id, position
    playlists_insert_response = youtube.playlists().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=playlist,
                description="A FOSS by Spoken-Tutorials"
            ),
            status=dict(
                privacyStatus="public"
            )
        )
    ).execute()
    return playlists_insert_response["id"], 0

def add_to_playlist(youtube,playlist_id,video_id,position):
    print "adding to playlist"
    response = youtube.playlistItems().insert(
        part="snippet",
        body=dict(
            snippet=dict(
                playlistId= playlist_id,
                resourceId={"kind":"youtube#video","videoId":video_id},
                position = position
            )
        )
    ).execute()
    print "playlistitemId",response['id']
    return response['id']

def delete_video(youtube,videoID,playlistitemID):
    print "deleting video"
    response = youtube.videos().delete(
        id=videoID
    ).execute()
    print "deleting from playlist"
    response_playlistitem = youtube.playlistItems().delete(
        id=playlistitemID
    ).execute()
    print "deleted"






if __name__ == '__main__':

    # Taking arguments as input: only trid, file is required. Rest optional.
    argparser.add_argument("--first", default="no")
    argparser.add_argument("--trid", default=1, help="Tutorial Id to upload")
    argparser.add_argument("--file", help="Video file to upload")
    argparser.add_argument("--delete", default="no")
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument("--description", help="Video description",default="Test Description")
    argparser.add_argument("--playlist", default="Extras")
    argparser.add_argument("--category", default="22",help="Numeric video category. " + "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated",default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    args = argparser.parse_args()
    tr_rec = TutorialResource.objects.get(pk = args.trid)
    youtube = get_authenticated_service(args)           # Gets authentication entity. Will create oAuth2.0 json credentials (if not present) using client secrets json
    if args.first == "yes":
        exit("Authentication done")
    try:
        #print "hi"
        if args.delete == "yes":
            if tr_rec.video_id:
                delete_video(youtube,tr_rec.video_id,tr_rec.playlist_item_id)
            else:
                exit("no video available")
        else:
            if not os.path.exists(args.file):
                exit("Error : Please specify a valid file using the --file= parameter.")
            
            initialize_upload(youtube, args)
            print "videoId",video_id
            if video_id != "NULL":
                tr_rec.video_id= video_id
                if args.playlist != "Extra":
                    playlist_id, position = add_playlist(youtube,args.playlist)
                    #print "playlistId",playlist_id
                    playlistitemId = add_to_playlist(youtube,playlist_id,video_id,position)
                    try:
                        pl = PlaylistInfo.objects.get(foss_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id)
                        pl.playlist_id = playlist_id
                        pl.save()
                    except PlaylistInfo.DoesNotExist:
                        pl = PlaylistInfo(foss_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, playlist_id = playlist_id)
                        pl.save()
                    tr_rec.playlist_item_id = playlistitemId
                    pl_item = PlaylistItem(playlist_id = pl.id , item_id = playlistitemId)
                    pl_item.save()
                tr_rec.save()
    except HttpError, e:
        print "Error : An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
