# Youtube-upload is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Youtube-upload is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Youtube-upload. If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import time
import string
import locale
import urllib
import socket
import getpass
import StringIO
import optparse
import itertools
# python >= 2.6
from xml.etree import ElementTree

# python-gdata (>= 1.2.4)
import gdata.media
import gdata.service
import gdata.geo
import gdata.youtube
import gdata.youtube.service
from gdata.media import YOUTUBE_NAMESPACE
from atom import ExtensionElement

# http://pycurl.sourceforge.net/
#try:
import pycurl
#except ImportError:
#pycurl = None

# http://code.google.com/p/python-progressbar (>= 2.3)
try:
    import progressbar
except ImportError:
    progressbar = None

class InvalidCategory(Exception): pass
class VideoArgumentMissing(Exception): pass
class OptionsMissing(Exception): pass
class BadAuthentication(Exception): pass
class ParseError(Exception): pass
class VideoNotFound(Exception): pass
class UnsuccessfulHTTPResponseCode(Exception): pass

def to_utf8(s):
    """Re-encode string from the default system encoding to UTF-8."""
    current = locale.getpreferredencoding()
    return (s.decode(current).encode("UTF-8") if s and current != "UTF-8" else s)

def debug(obj, fd=sys.stderr):
    """Write obj to standard error."""
    string = str(obj.encode(get_encoding(fd), "backslashreplace")
        if isinstance(obj, unicode) else obj)
    fd.write(string + "\n")

def get_encoding(fd):
    """Guess terminal encoding."""
    return fd.encoding or locale.getpreferredencoding()

def compact(it):
    """Filter false (in the truth sense) elements in iterator."""
    return filter(bool, it)

def first(it):
    """Return first element in iterable."""
    return it.next()

def post(url, files_params, extra_params, show_progressbar=True):
    """Post files to a given URL."""
    def progress(bar, maxval, download_t, download_d, upload_t, upload_d):
        bar.update(min(maxval, upload_d))
    c = pycurl.Curl()
    file_params2 = [(key, (pycurl.FORM_FILE, path)) for (key, path) in files_params.items()]
    items = extra_params.items() + file_params2
    c.setopt(c.URL, url + "?nexturl=http://code.google.com/p/youtube-upload")
    c.setopt(c.HTTPPOST, items)
    if show_progressbar and progressbar:
        widgets = [
            progressbar.Percentage(), ' ',
            progressbar.Bar(), ' ',
            progressbar.ETA(), ' ',
            progressbar.FileTransferSpeed(),
        ]
        total_filesize = sum(os.path.getsize(path) for path in files_params.values())
        bar = progressbar.ProgressBar(widgets=widgets, maxval=total_filesize)
        bar.start()
        c.setopt(c.NOPROGRESS, 0)
        c.setopt(c.PROGRESSFUNCTION, lambda *args: progress(bar, total_filesize, *args))
    elif show_progressbar:
        debug("Install python-progressbar to see a nice progress bar")
        bar = None
    else:
        bar = None

    body_container = StringIO.StringIO()
    headers_container = StringIO.StringIO()
    c.setopt(c.WRITEFUNCTION, body_container.write)
    c.setopt(c.HEADERFUNCTION, headers_container.write)
    c.perform()
    http_code = c.getinfo(pycurl.HTTP_CODE)
    c.close()

    if bar:
        bar.finish()
    headers = dict([s.strip() for s in line.split(":", 1)] for line in
      headers_container.getvalue().splitlines() if ":" in line)
    return http_code, headers, body_container.getvalue()

class Youtube:
    """Interface the Youtube API."""
    CATEGORIES_SCHEME = "http://gdata.youtube.com/schemas/2007/categories.cat"

    def __init__(self, developer_key, source="spoken-youtube_upload",
            client_id="spoken-youtube_upload"):
        """Login and preload available categories."""
        service = gdata.youtube.service.YouTubeService()
        service.ssl = False # SSL is not yet supported by the API
        service.source = source
        service.developer_key = developer_key
        service.client_id = client_id
        self.service = service

    def login(self, email, password, captcha_token=None, captcha_response=None):
        """Login into youtube."""
        self.service.email = email
        self.service.password = password
        self.service.ProgrammaticLogin(captcha_token, captcha_response)

    def get_upload_form_data(self, path, *args, **kwargs):
        """Return dict with keys 'post_url' and 'token' with upload info."""
        entry = self._create_video_entry(*args, **kwargs)
        post_url, token = self.service.GetFormUploadToken(entry)
        return dict(entry=entry, post_url=post_url, token=token)

    def create_playlist(self, title, description, private=False):
        """Create a new playlist and return its uri."""
        playlist = self.service.AddPlaylist(title, description, private)
        playlistid = None
        try:
            playlistid = first(el.text for el in playlist._ToElementTree() \
                if "playlistId" in el.tag)
        except:
            pass
        return playlistid

    def add_video_to_playlist(self, video_id, playlist_id, title=None, \
        description=None):
        """Add video to playlist."""
        expected = r"http://gdata.youtube.com/feeds/api/playlists/"
        playlist_uri = expected + playlist_id
        playlist_video_entry = self.service.AddPlaylistVideoEntryToPlaylist(
            playlist_uri, video_id, title, description)
        try:
            playlist_video_entry = str(first(el.text for el in \
                playlist_video_entry._ToElementTree() if "id" in el.tag))
            playlist_video_entry = playlist_video_entry\
                .replace(playlist_uri, '').strip('/')
        except:
            playlist_video_entry = None
            pass
        return playlist_video_entry

    def update_metadata(self, video_id, title, description):
        """Change metadata of a video."""
        entry = self._get_feed_from_video_id(video_id)
        if title:
            entry.media.title = gdata.media.Title(text=title)
        if description:
            entry.media.description = \
                gdata.media.Description(description_type='plain', \
                    text=description)
        return self.service.UpdateVideoEntry(entry)

    def delete_video_from_playlist(self, video_id, playlist_id):
        """Delete video from playlist."""
        expected = r"http://gdata.youtube.com/feeds/api/playlists/"
        playlist_uri = expected + playlist_id
        entries = self.service.GetYouTubePlaylistVideoFeed(playlist_uri).entry

        for entry in entries:
            url, entry_id = get_entry_info(entry)
            if video_id == entry_id:
                playlist_video_entry_id = entry.id.text.split('/')[-1]
                self.service.DeletePlaylistVideoEntry(playlist_uri, \
                    playlist_video_entry_id)
                break
        else:
            raise VideoNotFound("Video %s not found in playlist %s" % \
                (video_id, playlist_uri))

    def check_upload_status(self, video_id):
        """
        Check upload status of a video.

        Return None if video is processed, and a pair (status, message) otherwise.
        """
        return self.service.CheckUploadStatus(video_id=video_id)

    def _get_feed_from_video_id(self, video_id):
        template = 'http://gdata.youtube.com/feeds/api/users/default/uploads/%s'
        return self.service.GetYouTubeVideoEntry(template % video_id)

    def get_feed_from_video_id(self, video_id):
        template = 'http://gdata.youtube.com/feeds/api/users/default/uploads/%s'
        return self.service.GetYouTubeVideoEntry(template % video_id)

    def _create_video_entry(self, title, description, category, keywords=None,
            location=None, private=False, unlisted=False):
        self.categories = self.get_categories()
        if category not in self.categories:
            valid = " ".join(self.categories.keys())
            raise InvalidCategory("Invalid category '%s' (valid: %s)" % \
                (category, valid))
        media_group = gdata.media.Group(
            title=gdata.media.Title(text=title),
            description=gdata.media.Description(description_type='plain', \
                text=description),
            keywords=gdata.media.Keywords(text=keywords),
            category=gdata.media.Category(
                text=category,
                label=self.categories[category],
                scheme=self.CATEGORIES_SCHEME),
            private=(gdata.media.Private() if private else None),
            player=None)
        if location:
            where = gdata.geo.Where()
            where.set_location(location)
        else:
            where = None
        kwargs = {
            "namespace": YOUTUBE_NAMESPACE,
            "attributes": {'action': 'list', 'permission': 'denied'},
        }
        extension = ([ExtensionElement('accessControl', **kwargs)] \
            if unlisted else None)
        return gdata.youtube.YouTubeVideoEntry(media=media_group, geo=where,
            extension_elements=extension)

    @classmethod
    def get_categories(cls):
        """Return categories dictionary with pairs (term, label)."""
        def get_pair(element):
            """Return pair (term, label) for a (non-deprecated) XML element."""
            if all(not(str(x.tag).endswith("deprecated")) for x in \
                element.getchildren()):
                return (element.get("term"), element.get("label"))
        xmldata = str(urllib.urlopen(cls.CATEGORIES_SCHEME).read())
        xml = ElementTree.XML(xmldata)
        return dict(compact(map(get_pair, xml)))


def get_video_id_from_url(url):
    """Return video ID from a Youtube URL."""
    match = re.search("v=(.*)$", url)
    if not match:
        raise ParseError("expecting a video URL (http://www.youtube.com?v=ID)\
            , but got '%s'" % url)
    return match.group(1)

def get_entry_info(entry):
    """Return pair (url, id) for video entry."""
    url = entry.GetHtmlLink().href.replace("&feature=youtube_gdata", "")
    video_id = get_video_id_from_url(url)
    return url, video_id

def parse_location(string):
    """Return tuple (long, latitude) from string with coordinates."""
    if string and string.strip():
        return map(float, string.split(",", 1))

def wait_processing(youtube_obj, video_id):
    """Wait until a video id recently uploaded has been procesed."""
    debug("waiting until video is processed")
    while 1:
        try:
          response = youtube_obj.check_upload_status(video_id)
        except socket.gaierror as msg:
          debug("non-fatal network error: %s" % msg)
          continue
        if not response:
            debug("video is processed")
            break
        status, message = response
        debug("check_upload_status: %s" % " - ".join(compact(response)))
        if status != "processing":
            break
        time.sleep(5)

def upload_video(youtube, options, video_path):
    """Upload video with index (for split videos)."""
    title = to_utf8(options['title'])
    description = to_utf8(options['description'] or "").decode("string-escape")
    args = [video_path, title, description,
            options['category'], options['keywords']]
    kwargs = {
      "private": options['private'],
      "location": parse_location(options['location']),
      "unlisted": options['unlisted'],
    }

    # upload with curl
    video_id = None
    try:
        data = youtube.get_upload_form_data(*args, **kwargs)
        entry = data["entry"]
        #debug("Start upload using a HTTP post: %s -> %s" % (video_path, \
            #data["post_url"]))
        http_code, headers, body = post(data["post_url"],
            {"file": video_path}, {"token": data["token"]},
            show_progressbar = True)
        if http_code != 302:
            raise UnsuccessfulHTTPResponseCode(
                "HTTP code on upload: %d (expected 302)" % http_code)
        params = dict(s.split("=", 1) for s in headers["Location"]\
            .split("?", 1)[1].split("&"))
        if params["status"] !=  "200":
            raise UnsuccessfulHTTPResponseCode(
                "HTTP status on upload link: %s (expected 200)" % params["status"])
        video_id = params["id"]
        #url = "http://www.youtube.com/watch?v=%s" % video_id
        """if options.wait_processing:
            wait_processing(youtube, video_id)"""
    except Exception, e:
        print e
        pass
    return video_id
