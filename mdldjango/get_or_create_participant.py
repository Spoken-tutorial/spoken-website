import random, string, hashlib, csv
from models import MdlUser
from events.models import *
from django.core.mail import EmailMultiAlternatives
from validate_email import validate_email

def update_participants_count(training):
    #if training.organiser.academic.institution_type.name == "School":
    #    training.participant_counts = SchoolTrainingAttendance.objects.filter(training = training, status__gte = 1).count()
    #else:
    training.participant_counts = TrainingAttendance.objects.filter(training = training, status__gte = 1).count()
    training.save()

def _is_organiser(user):
    try:
        if user.groups.filter(name='Organiser').count() == 1 and user.organiser and user.organiser.status == 1:
            return True
    except:
        pass
def encript_password(password):
    password = hashlib.md5(password+'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()
    return password

def create_account(w, firstname, lastname, gender, email, category):
    password_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    password_encript = encript_password(password_string)

    password = password_encript
    username = email
    mdluser = None
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
        mdluser.email = email
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
    return mdluser

def get_or_create_participant(w, firstname, lastname, gender, email, category):
    mdluser = None
    if w and w.organiser.academic.institution_type.name == 'School' and not email:
        ta = TrainingAttendance()
        ta.status = 1
        ta.training_id = w.id
        ta.firstname = firstname
        ta.lastname = lastname
        ta.gender = gender
        ta.email = email
        ta.save()
        return True
    else:
        mdluser = create_account(w, firstname, lastname, gender, email, category)
        if TrainingAttendance.objects.filter(training_id=w.id, mdluser_id = mdluser.id).exists():
            return True
        ta = TrainingAttendance()
        ta.mdluser_id = mdluser.id
        ta.status = 1
        ta.training_id = w.id
        ta.firstname = mdluser.firstname
        ta.lastname = mdluser.lastname
        ta.gender = mdluser.gender
        ta.email = mdluser.email
        ta.save()
        return True
    return False
    #if category == 2:
    #    try:
    #        wa = TrainingAttendance.objects.get(training_id = w.id, mdluser_id = mdluser.id)
    #    except Exception, e:
    #        wa = TrainingAttendance()
    #        wa.training_id = w.id
    #        wa.status = 1
    #        wa.mdluser_id = mdluser.id
    #        wa.save()
            
def check_csvfile(user, file_path, w=None, flag=0):
    csv_file_error = 0
    error_line_no = ''
    with open(file_path, 'rbU') as csvfile:
        count  = 0
        csvdata = csv.reader(csvfile, delimiter=',', quotechar='|')
        try:
            for row in csvdata:
                count = count + 1
                try:
                    row_length = len(row)
                    if row_length < 3:
                        continue
                    firstname = row[0].strip().title()
                    lastname = row[1].strip().title()
                    gender = None
                    email = None
                    
                    if row_length == 3:
                        if _is_organiser(user) and (user.organiser.academic.institution_type.name == 'School' or (w and w.organiser.academic.institution_type.name == 'School')):
                            gender = row[2].strip().title()
                            if '@' in gender:
                                if not error_line_no:
                                    error_line_no = error_line_no + str(count)
                                else:
                                    error_line_no = error_line_no + ', ' + str(count)
                                csv_file_error = 1
                                continue
                        else:
                            if not error_line_no:
                                error_line_no = error_line_no + str(count)
                            else:
                                error_line_no = error_line_no + ', ' + str(count)
                            csv_file_error = 1
                            continue
                    if row_length > 3:
                        email = row[2].strip().lower()
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
                    if flag and flag <= 2:
                        if not w:
                            return 1, error_line_no
                        get_or_create_participant(w, firstname, lastname, gender, email, 2)
                except Exception, e:
                    csv_file_error = 1
                    if not error_line_no:
                        error_line_no = error_line_no + str(count)
                    else:
                        error_line_no = error_line_no + ', ' + str(count)
            if error_line_no:
                error_line_no = "<b>Error: Line number "+ error_line_no + " in CSV file data is not in a proper format in the Participant list. The format should be First name, Last name, Email, Gender. For more details <a href='http://process.spoken-tutorial.org/images/c/c2/Participant_data.pdf' target='_blank'>Click here</a></b>"
        except Exception, e:
            csv_file_error = 1
            error_line_no = "<b>Error: CSV file data is not in a proper format in the Participant list. The format should be First name, Last name, Email, Gender. For more details <a href='http://process.spoken-tutorial.org/images/c/c2/Participant_data.pdf' target='_blank'>Click here</a></b>"
        if flag == 3 and int(w.participant_count < count):
            csv_file_error = 1
            error_line_no = "Training participant count less than {0}.".format(w.participant_count)
    return csv_file_error, error_line_no
