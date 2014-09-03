from HTMLParser import HTMLParser
import time, mechanize, cookielib
from BeautifulSoup import BeautifulSoup
from urllib import urlopen, quote
import MySQLdb

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
    table = soup.findAll("table", attrs={'border':'1'})
    
    #try:
    rows = table[0].findAll("tr")
    counter = 1
    srt_data = ''
    previous_time = '00:00:00'
    for row in rows:
        cols = row.findAll("td")
        flag = 0
        time_error = 0
        for col in cols:
            if col.text.lower() == 'time':
                break
            if flag:
                flag = 0
                if time_error:
                    time_error = 0
                    continue
                if col.string:
                    srt_data += col.text.strip('\n').strip() + '\n\n'
                else:
                    srt_data += strip_tags(str(col.renderContents())\
                    .replace('&amp;', '&').replace('&quot;', '"')\
                    .replace('&gt;', '>').replace('&lt;', '<')).decode('utf-8').strip('\n').strip() + '\n\n'
            else:
                flag = 1
                formatted_time = get_formatted_time(col.text.replace('.', ':').replace('-', ':').replace('/', ':'))
                if formatted_time:
                    srt_data += str(counter) + '\n'
                    srt_data += previous_time + ' --> ' + formatted_time + '\n'
                    counter += 1
                    previous_time = formatted_time
                else:
                    time_error = 1
            #print col.text
    if srt_data:
        file_head = open(srt_file_path,"w")
        file_head.write(srt_data.encode("utf-8"))
        file_head.close()
        #print srt_data
    """except Exception, e:
        print e
        return False"""
    return True


def get_formatted_time(raw_time_string):
    raw_time_parts_tmp = raw_time_string.strip().strip(':').split(':')
    raw_time_parts = []
    for time_part in raw_time_parts_tmp:
        if time_part and time_part != ' ':
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
        print raw_time_parts
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


db = MySQLdb.connect(host = 'localhost', user = 'root', passwd = 'shiva', db = 'spoken')
cur = db.cursor()
cur.execute("SELECT * FROM creation_tutorialresource where status = 1 or status = 2")
rows = cur.fetchall()
SCRIPT_URL = 'http://script.spoken-tutorial.org'
MEDIA_ROOT = '/home/vishnu/devil/spoken/media/'
overwrite = True
for row in rows:
    code = 0
    cur.execute('select * from creation_tutorialdetail where id = ' + str(row[1]))
    tutorial_detail = cur.fetchone()
    cur.execute('select * from creation_language where id = ' + str(row[3]))
    language = cur.fetchone()
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
    srt_file_name = tutorial_detail[2].replace(' ', '-') + '-' + language[1] + '.srt'
    # print srt_file_name
    if not overwrite and os.path.isfile(srt_file_path + srt_file_name):
        continue
    try:
        code = urlopen(script_path).code
    except Exception, e:
        code = e.code
    result = ''
    if(int(code) == 200):
        if generate_subtitle(script_path, srt_file_path + srt_file_name):
            print 'Success: ', str(tutorial_detail[1]) + ',', srt_file_name
        else:
            print 'Failed: ', str(tutorial_detail[1]) + ',', srt_file_name
