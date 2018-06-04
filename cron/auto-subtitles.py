from HTMLParser import HTMLParser
import time, mechanize, cookielib, datetime
from BeautifulSoup import BeautifulSoup
from urllib import urlopen, quote
import MySQLdb
import sys
import os
#sys.path.insert(0, '../spoken')
#sys.path.insert(0, '../../spoken')
from config import *


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    try:
        s.feed(html)
        return str(s.get_data())
    except:
        pass
    return html


def readUrl(url):
    # print "Reading :", url
    b = getNewBrowser()
    b.open(url, timeout = 30.0)
    return BeautifulSoup(b.response())


def getNewBrowser():
    # create browser instance
    b = mechanize.Browser()

    # create a cookiejar for cookies
    jar = cookielib.LWPCookieJar()
    b.set_cookiejar(jar)

    # prevent mechanize from simulating a 403 disallow
    b.set_handle_robots(False)

    # handle some other stuff
    b.set_handle_equiv(True)
    #b.set_handle_gzip(True)
    b.set_handle_redirect(True)
    b.set_handle_referer(True)

    # follows refresh 0 but not hangs on refresh >0
    b.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # want debugging messages?
    #b.set_debug_http(True)
    #b.set_debug_redirects(True)
    #b.set_debug_responses(True)

    # User-Agent
    b.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/31.0')]
    return b


def generate_subtitle(srt_url, srt_file_path):
    soup = readUrl(srt_url)
    table = soup.findAll("table")
    if not table:
        print 'table not found'
        return False
    try:
        rows = table[0].findAll("tr")
        counter = 1
        srt_data = 'WEBVTT\n\n'
        previous_time = None
        previous_script_data = None
        for row in rows:
            cols = row.findAll("td")
            flag = 0
            time_error = 0
            for col in cols:
                if col.text.lower() == 'time':
                    break
                if flag:
                    flag = 0
                    if previous_script_data == None:
                        previous_script_data = get_formatted_script(col)
                        continue
                    if time_error:
                        time_error = 0
                        continue
                    srt_data += previous_script_data
                    previous_script_data = get_formatted_script(col)
                else:
                    flag = 1
                    formatted_time = get_formatted_time(col.text.replace('.', ':').replace('-', ':').replace('/', ':'))
                    if formatted_time:
                        if previous_time == None:
                            previous_time = formatted_time
                            continue
                        srt_data += str(counter) + '\n'
                        srt_data += previous_time + '.000' + ' --> ' + str((datetime.datetime.strptime(\
                                                formatted_time, "%H:%M:%S") - datetime.timedelta(seconds = 1)).time()) + '.001\n'
                        counter += 1
                        previous_time = formatted_time
                    else:
                        time_error = 1
                #print col.text
        video_info = get_video_info(rreplace(srt_file_path, 'vtt', 'ogv', 1))
        if srt_data:
            if previous_script_data:
                srt_data += str(counter) + '\n'
                if video_info['duration']:
                    srt_data += previous_time + '.000' + ' --> ' + video_info['duration'] + '.001\n'
                else:
                    srt_data += previous_time + '.000' + ' --> ' + str((datetime.datetime.strptime(\
                        previous_time, "%H:%M:%S") + datetime.timedelta(seconds = 5)).time()) + '.001\n'
                srt_data += previous_script_data
            file_head = open(srt_file_path,"w")
            file_head.write(srt_data.encode("utf-8"))
            file_head.close()
    except Exception, e:
        print e
        return False
    return True


# returns video meta info using ffmpeg
def get_video_info(path):
    """Uses ffmpeg to determine information about a video."""
    info_m = {}
    try:
        process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        duration_m = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?)", stdout, re.DOTALL).groupdict()
        info_m = re.search(r": Video: (?P<codec>.*?), (?P<profile>.*?), (?P<width>.*?)x(?P<height>.*?), ", stdout, re.DOTALL).groupdict()

        hours = Decimal(duration_m['hours'])
        minutes = Decimal(duration_m['minutes'])
        seconds = Decimal(duration_m['seconds'])

        total = 0
        total += 60 * 60 * hours
        total += 60 * minutes
        total += seconds

        info_m['hours'] = hours
        info_m['minutes'] = minutes
        info_m['seconds'] = seconds
        tmp_seconds = str(int(seconds))
        if seconds < 10:
            tmp_seconds = "0" + tmp_seconds
        info_m['duration'] = duration_m['hours'] + ':' + duration_m['minutes'] + ":" + tmp_seconds
        info_m['total'] = int(total)
        info_m['width'] = int(info_m['width'])
        # [PAR 1i:1 DAR 3:2] error in height
        info_m['height'] = int(info_m['height'].split()[0])
        info_m['size'] = get_filesize(path)
    except:
        info_m['codec'] = ''
        info_m['profile'] = ''
        info_m['hours'] = 0
        info_m['minutes'] = 0
        info_m['seconds'] = 0
        info_m['duration'] = 0
        info_m['total'] = 0
        info_m['width'] = 0
        info_m['height'] = 0
        info_m['size'] = 0
    return info_m


def get_formatted_script(script):
    if script.string:
        return script.text.strip('\n').strip() + '\n\n'
    else:
        return strip_tags(str(script.renderContents())\
        .replace('&amp;', '&').replace('&quot;', '"')\
        .replace('&gt;', '>').replace('&lt;', '<')).decode('utf-8').strip('\n').strip() + '\n\n'


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def get_digits(raw_string):
    return ''.join(digit for digit in raw_string if digit.isdigit())


def get_formatted_time(raw_time_string):
    raw_time_parts_tmp = raw_time_string.strip().strip(':').split(':')
    raw_time_parts = []
    for time_part in raw_time_parts_tmp:
        time_part = get_digits(time_part)
        if time_part.strip():
            raw_time_parts.append(time_part)
    if(len(raw_time_parts) == 2):
        minutes = int(raw_time_parts[0])
        seconds = int(raw_time_parts[1])
        raw_time_parts[0] = str(minutes)
        raw_time_parts[1] = str(seconds)
        if minutes < 10:
            raw_time_parts[0] = '0' + raw_time_parts[0]
        if seconds < 10:
            raw_time_parts[1] = '0' + raw_time_parts[1]
        return '00:' + raw_time_parts[0] + ':' + raw_time_parts[1]
    elif(len(raw_time_parts) == 3):
        hours = int(raw_time_parts[0])
        minutes = int(raw_time_parts[1])
        seconds = int(raw_time_parts[2])
        raw_time_parts[0] = str(hours)
        raw_time_parts[1] = str(minutes)
        raw_time_parts[2] = str(seconds)
        if hours < 10:
            raw_time_parts[0] = '0' + raw_time_parts[0]
        if minutes < 10:
            raw_time_parts[1] = '0' + raw_time_parts[1]
        if seconds < 10:
            raw_time_parts[2] = '0' + raw_time_parts[2]
        return raw_time_parts[0] + ':' + raw_time_parts[1] + ':' + raw_time_parts[2]
    return None


db = MySQLdb.connect(host = DB_HOST, user = DB_USER, passwd = DB_PASS, db = DB_NAME)
cur = db.cursor()
cur.execute("SELECT * FROM creation_tutorialresource where status = 1 or status = 2 order by updated desc")
rows = cur.fetchall()
overwrite = False
if 'replace' in sys.argv:
    overwrite = True
error_log_file_head = open(LOG_ROOT + 'srt-error-log.txt',"w")
success_log_file_head = open(LOG_ROOT + 'srt-success-log.txt',"w")
for row in rows:
    code = 0
    cur.execute('select * from creation_tutorialdetail where id = ' + str(row[1]))
    tutorial_detail = cur.fetchone()
    cur.execute('select * from creation_language where id = ' + str(row[3]))
    language = cur.fetchone()
    cur.execute('select * from creation_fosscategory where id = ' + str(tutorial_detail[1]))
    foss = cur.fetchone()
    if language[1] == 'English':
        if row[10] and row[10] != 'pending':
            script_path = SCRIPT_URL.strip('/') + '?title=' + quote(row[10]) + '&printable=yes'
        elif row[7] and row[7] != 'pending':
            script_path = SCRIPT_URL.strip('/') + '?title=' + quote(row[7] + '-timed') + '&printable=yes'
        else:
            continue
    else:
        if row[7] and row[7] != 'pending':
            script_path = SCRIPT_URL.strip('/') + '?title=' + quote(row[7]) + '&printable=yes'
        else:
            continue
    srt_file_path = MEDIA_ROOT + 'videos/' + str(tutorial_detail[1]) + '/' + str(tutorial_detail[0]) + '/'
    srt_file_name = tutorial_detail[2].replace(' ', '-') + '-' + language[1] + '.vtt'

    if not overwrite and os.path.isfile(srt_file_path + srt_file_name):
        continue
    try:
        code = urlopen(script_path).code
    except Exception, e:
        code = e.code
    result = ''
    if(int(code) == 200):
        if overwrite and os.path.isfile(srt_file_path + srt_file_name):
            os.remove(srt_file_path + srt_file_name)
        if generate_subtitle(script_path, srt_file_path + srt_file_name):
            success_string = 'Success: ' + str(foss[1]) + ', ' + srt_file_name + '\n'
            success_log_file_head.write(success_string)
            print success_string
        else:
            error_string = 'Failed: ' + str(foss[1]) + ', ' + srt_file_name + '\n'
            error_log_file_head.write(error_string)
            print error_string
error_log_file_head.close()
success_log_file_head.close()
