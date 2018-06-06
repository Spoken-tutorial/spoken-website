# Standard Library
import cookielib
import datetime
from HTMLParser import HTMLParser

# Third Party Stuff
import mechanize
from BeautifulSoup import BeautifulSoup


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
    s.feed(html)
    return str(s.get_data())

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
                        srt_data += previous_time + '.000' + ' --> ' + formatted_time + '.001\n'
                        counter += 1
                        previous_time = formatted_time
                    else:
                        time_error = 1
                #print col.text
        duration_info = get_duration_info(rreplace(srt_file_path, 'vtt', 'ogv', 1))
        if srt_data:
            if previous_script_data:
                srt_data += str(counter) + '\n'
                if duration_info:
                    srt_data += previous_time + '.000' + ' --> ' + duration_info + '.001\n'
                else:
                    srt_data += previous_time + '.000' + ' --> ' + str((datetime.datetime.strptime(\
                        previous_time, "%H:%M:%S") + datetime.timedelta(seconds = 5)).time()) + '.001\n'
                srt_data += previous_script_data
            file_head = open(srt_file_path,"w")
            file_head.write(srt_data.encode("utf-8"))
            file_head.close()
           #print srt_data
    except Exception, e:
        #print e
        return False
    return True

def get_formatted_time(raw_time_string):
    raw_time_parts = raw_time_string.split(':')
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

# returns video duration info using ffmpeg
def get_duration_info(path):
    """Uses ffmpeg to determine information about a video."""
    info_m = {}
    try:
        process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        duration_m = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?)", stdout, re.DOTALL).groupdict()

        seconds = Decimal(duration_m['seconds'])
        tmp_seconds = str(int(seconds))
        if seconds < 10:
            tmp_seconds = "0" + tmp_seconds

        duration =  duration_m['hours'] + ':' + duration_m['minutes'] + ":" + tmp_seconds
    except:
        duration = None
    return duration
