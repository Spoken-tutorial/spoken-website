import random, string, hashlib, csv
from models import MdlUser
from events.models import TrainingAttendance
from django.core.mail import EmailMultiAlternatives
from validate_email import validate_email

def encript_password(password):
    password = hashlib.md5(password+'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()
    return password
    
def get_or_create_participant(w, firstname, lastname, gender, email, category):
    password_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    password_encript = encript_password(password_string)

    password = password_encript
    username = email
    try:
        mdluser = MdlUser.objects.filter(email = email).first()
        mdluser.institution = w.academic_id
        mdluser.firstname = firstname
        mdluser.lastname = lastname
        mdluser.gender = gender
        mdluser.save()
    except Exception, e:
        mdluser = MdlUser()
        mdluser.auth = 'manual'
        mdluser.firstname = firstname
        mdluser.username = username
        mdluser.lastname = lastname
        mdluser.password = password
        mdluser.institution = w.academic_id
        mdluser.email = email.lower()
        mdluser.confirmed = 1
        mdluser.mnethostid = 1
        mdluser.gender = gender
        mdluser.save()
        mdluser = MdlUser.objects.filter(email = email, firstname= firstname, username=username, password=password).first()
        
        # send password to email
        subject  = "Spoken Tutorial Online Test password"
        to = [mdluser.email]
        message = '''Hi {0},

Your account password at 'Spoken Tutorials Online Test as follows'

Your current login information is now:
username: {1}
password: {2}

Please go to this page to change your password:
{3}

In most mail programs, this should appear as a blue link
which you can just click on.  If that doesn't work,
then cut and paste the address into the address
line at the top of your web browser window.

Cheers from the 'Spoken Tutorials Online Test Center' administrator,

Admin Spoken Tutorials
'''.format(mdluser.firstname, mdluser.username, password_string, 'http://onlinetest.spoken-tutorial.org/login/change_password.php')

        # send email
        email = EmailMultiAlternatives(
            subject, message, 'administrator@spoken-tutorial.org',
            to = to, bcc = [], cc = [],
            headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
        )

        result = email.send(fail_silently=False)
        #print "-----------------------------------------"
        #print message
        #print "-----------------------------------------"
    if category == 2:
        try:
            wa = TrainingAttendance.objects.get(training_id = w.id, mdluser_id = mdluser.id)
        except Exception, e:
            #print e
            wa = TrainingAttendance()
            wa.training_id = w.id
            wa.status = 1
            wa.mdluser_id = mdluser.id
            wa.save()
            
def check_csvfile(file_path, w=None, flag=0):
    print w, "####################"
    csv_file_error = 0
    error_line_no = ''
    with open(file_path, 'rbU') as csvfile:
        count  = 0
        csvdata = csv.reader(csvfile, delimiter=',', quotechar='|')
        try:
            for row in csvdata:
                count = count + 1
                try:
                    firstname = row[0].strip().title()
                    lastname = row[1].strip().title()
                    email = row[2].strip()
                    gender = row[3].strip().title()
                    if not validate_email(email):
                        if email in ['Email', 'email', 'mail']:
                            continue
                        if not error_line_no:
                            error_line_no = error_line_no + str(count)
                        else:
                            error_line_no = error_line_no + ', ' + str(count)
                        csv_file_error = 1
                        continue
                    if flag:
                        if not w:
                            return 1, error_line_no
                        get_or_create_participant(w, firstname, lastname, gender, email, 2)
                except Exception, e:
                    print e
                    csv_file_error = 1
                    if not error_line_no:
                        error_line_no = error_line_no + str(count)
                    else:
                        error_line_no = error_line_no + ', ' + str(count)
        except:
            csv_file_error = 1
            error_line_no = '1'
    return csv_file_error, error_line_no
