import httplib2
import MySQLdb
import json
import os
import sys
import time
import config

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run


class Error(Exception):
    """Custom Exception subclass."""
    pass


class YoutubeCaption(object):

    OAUTH_SCOPE = "https://gdata.youtube.com"
    CAPTIONS_URL_FORMAT = ("http://gdata.youtube.com/feeds/api/videos/%s/" \
        "captions?alt=json")
    CAPTIONS_CONTENT_TYPE = "application/vnd.youtube.timedtext; charset=UTF-8"
    CAPTIONS_LANGUAGE_CODE = "en"
    CAPTIONS_TITLE = ""


    def __init__(self, developer_key, client_id, client_secret):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.DEVELOPER_KEY = developer_key


    def authenticate(self):
        storage = Storage('youtube-oauth.storage')
        self.credentials = storage.get()
        if self.credentials is None or self.credentials.invalid:
            flow = OAuth2WebServerFlow(
                client_id = self.CLIENT_ID,
                client_secret = self.CLIENT_SECRET,
                scope = self.OAUTH_SCOPE,
                user_agent = 'Mozilla/5.0 (X11; Linux x86_64) \
                    Gecko/20100101 Firefox/31.0'
            )
            self.credentials = run(flow, storage)


    def setup_http_request_object(self):
        self.headers = {
            "GData-Version": "2",
            "X-GData-Key": "key=%s" % self.DEVELOPER_KEY
        }
        self.http = self.credentials.authorize(httplib2.Http())


    def upload_translated_captions(self, srt_file_path, video_id):
        try:
            self.authenticate()
            self.setup_http_request_object()
        except Exception, e:
             raise Error("Error while authenticating: %s" % str(e))
        self.headers["Content-Type"] = self.CAPTIONS_CONTENT_TYPE
        self.headers["Content-Language"] = self.CAPTIONS_LANGUAGE_CODE
        self.headers["Slug"] = self.CAPTIONS_TITLE
        srt_file = open(srt_file_path)
        self.translated_captions_body = srt_file.read()
        url = self.CAPTIONS_URL_FORMAT % video_id
        response_headers, body = self.http.request (
            url,
            "POST",
            body = self.translated_captions_body,
            headers = self.headers
        )
        if response_headers["status"] != "201":
            return "Received HTTP response %s when uploading captions \
                to %s." % (response_headers["status"], url), False

        return '%s - %s %s - caption updated' % (video_id, \
            self.CAPTIONS_LANGUAGE_CODE, self.CAPTIONS_TITLE), True


    def set_caption_language_title(self, language='', title=''):
        self.CAPTIONS_LANGUAGE_CODE = language
        self.CAPTIONS_TITLE = title


if __name__ == "__main__":
    caption = YoutubeCaption(config.DEVELOPER_KEY, config.CLIENT_ID, \
        config.CLIENT_SECRET)
    db = MySQLdb.connect(host = config.DB_HOST, user = config.DB_USER, \
        passwd = config.DB_PASS, db = config.DB_NAME)

    ldb = MySQLdb.connect(host = config.DB_HOST, user = config.DB_USER, \
        passwd = config.DB_PASS, db = 'cron_logs')
    db_cursor = db.cursor()
    db_cursor.execute("select ctr.id, ctr.language_id, ctr.video, \
        ctr.tutorial_detail_id, ctr.video_id, ctd.foss_id, ctd.tutorial from \
        creation_tutorialresource ctr INNER JOIN creation_tutorialdetail ctd \
        ON ( ctr.tutorial_detail_id = ctd.id ) WHERE ((ctr.status = 1  OR \
        ctr.status = 2 ) AND ctr.video_id IS NOT NULL AND ctr.id NOT IN \
        (select distinct trid from cron_logs.srt_uploads)) ORDER BY \
        ctd.foss_id, ctd.level_id, ctd.order ASC")
    rows = db_cursor.fetchall()

    ldb = MySQLdb.connect(host = config.DB_HOST, user = config.DB_USER, \
        passwd = config.DB_PASS, db = 'cron_logs')
    ldb_cursor = ldb.cursor()

    for row in rows:
        overall_status = 0
        db_cursor.execute("select id, name, code from creation_language \
            where id = %s", [str(row[1]),])
        language = db_cursor.fetchone()
        video_title = str(row[6].replace(' ', '-'))
        video_path = config.MEDIA_ROOT + 'videos/' + str(row[5]) + '/' + \
            str(row[3]) + '/'
        english_srt = video_path + video_title + '-English.vtt'
        status_flag = False
        file_missing = False
        print ''
        print 'FOSS Id:', row[5]
        print 'Tutorial:', row[6]
        print 'Language:', language[1]
        if os.path.isfile(english_srt):
            file_missing = False
            ldb_cursor.execute("select * from srt_pending_uploads where trid=" \
                + str(row[0]) + " and native_or_english=0")
            esrt_row = ldb_cursor.fetchone()

            if esrt_row is None:
                caption.set_caption_language_title('en')
                message, status_flag = caption.upload_translated_captions(\
                    english_srt, row[4])
                if status_flag:
                    ldb_cursor.execute("insert into srt_pending_uploads \
                        (trid,native_or_english) values(%s, 0)", \
                        [str(row[0]),])
                    ldb.commit()
                    overall_status = 1
                print message
            else:
                print row[4], '- English - Already Exist'
                overall_status = 1
        else:
            file_missing = True
            print row[4], '- English -', 'VTT File Missing'
        if language[1] != 'English':
            native_srt = video_path + video_title + '-' + language[1] + '.vtt'
            if os.path.isfile(native_srt):
                ldb_cursor.execute("select * from srt_pending_uploads where \
                trid=" + str(row[0]) + " and native_or_english=1")
                nsrt_row = ldb_cursor.fetchone()
                
                if nsrt_row is None:
                    file_missing = False
                    language_title = ''
                    if language[2] == 'en':
                        language_title = language[1]
                    caption.set_caption_language_title(language[2], \
                        language_title)
                    message, status_flag = caption.upload_translated_captions(\
                        native_srt, row[4])
                    if status_flag:
                        ldb_cursor.execute("insert into srt_pending_uploads \
                            (trid,native_or_english) values(%s, 1)", \
                            [str(row[0]),])
                        ldb.commit()
                    print message
                else:
                    print row[4], '-', language[1], '- Already Exist'
                    status_flag = True
            else:
                file_missing = True
                print row[4], '-', language[1], '-', 'VTT File Missing'
                status_flag = False
        if status_flag and overall_status:
            ldb_cursor.execute("insert into srt_uploads (trid) values(%s)", \
                [str(row[0]),])
            ldb.commit()
        elif file_missing:
            continue
        else:
            time.sleep(1)
        time.sleep(1)
