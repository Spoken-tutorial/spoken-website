# Standard Library
import csv
import hashlib
import random
import string

# Third Party Stuff
from django.core.mail import EmailMultiAlternatives
from models import MdlUser
from validate_email import validate_email

# Spoken Tutorial Stuff
from events.models import *


def update_participants_count(training):
    training.participant_count = TrainingAttendance.objects.filter(training=training, status__gte=1).count()
    training.save()


def _is_organiser(user):
    try:
        if user.groups.filter(name='Organiser').count() == 1 and user.organiser and user.organiser.status == 1:
            return True
    except:
        pass


def encript_password(password):
    password = hashlib.md5(password + 'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()
    return password


def create_account(w, firstname, lastname, gender, email, category):
    password_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    password_encript = encript_password(password_string)

    password = password_encript
    username = email
    mdluser = None
    try:
        mdluser = MdlUser.objects.filter(email=email).first()
        mdluser.institution = w.academic_id
        mdluser.firstname = firstname
        mdluser.lastname = lastname
        mdluser.gender = gender
        mdluser.save()
    except Exception:
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
        mdluser = MdlUser.objects.filter(email=email, firstname=firstname, username=username, password=password).first()

        # send password to email
        subject = "Spoken Tutorial Online Test password"
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
            to=to, bcc=[], cc=[],
            headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type": "text/html;charset=iso-8859-1"}
        )
        email.send(fail_silently=False)
    return mdluser


def get_or_create_participant(w, firstname, lastname, gender, email, category):
    mdluser = None
    # Added category check as zero. Means the call is coming from new student
    # batch upload interface. And category is/was not used.
    if category == 0:
        create_account(w, firstname, lastname, gender, email, category)
        return True
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
        if TrainingAttendance.objects.filter(training_id=w.id, mdluser_id=mdluser.id).exists():
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


def store_error(error_line_no, count, invalid_emails=None, email=None):
    if not email:
        if not error_line_no:
            error_line_no = error_line_no + str(count)
        else:
            error_line_no = error_line_no + ',' + str(count)
    else:
        if not invalid_emails:
            invalid_emails = invalid_emails + email
        else:
            invalid_emails = invalid_emails + ',<br>' + email
    csv_file_error = 1
    return csv_file_error, error_line_no, invalid_emails


def can_allow_participant_to_attend(more_then_two_per_day_list, tdate, email):
    """ restrict participating more then 2 training per day """
    if tdate:
        tdate = tdate.split(' ')[0]
        training_count = TrainingAttendance.objects.filter(
            email=email, training__tdate=tdate, training__status__lte=4, status=1).count()
        if training_count < 2:
            return more_then_two_per_day_list
        if not more_then_two_per_day_list:
            more_then_two_per_day_list = more_then_two_per_day_list + email
        else:
            more_then_two_per_day_list = more_then_two_per_day_list + ',<br>' + email
        return more_then_two_per_day_list


def is_new_participant(reattempt_list, foss, email):
    """  check weather already participated in particular software """
    training_count = TrainingAttendance.objects.filter(
        email=email, training__foss_id=foss, training__status__lte=4, status=1).count()
    if training_count == 0:
        return reattempt_list
    if not reattempt_list:
        reattempt_list = reattempt_list + email
    else:
        reattempt_list = reattempt_list + ',<br>' + email
    return reattempt_list


def check_csvfile(user, file_path, w=None, flag=0, **kwargs):
    tdate = None
    foss = None
    if w:
        try:
            tdate = w.tdate.strftime("%Y-%m-%d")
            foss = w.foss_id
        except:
            tdate = w.tdate
            foss = w.foss_id
    if kwargs and 'tdate' in kwargs['form_data'] and 'foss' in kwargs['form_data']:
        tdate = kwargs['form_data']['tdate']
        foss = kwargs['form_data']['foss']

    csv_file_error = 0
    error_line_no = ''
    invalid_emails = ''
    reattempt_list = ''
    more_then_two_per_day_list = ''
    with open(file_path, 'rbU') as csvfile:
        count = 0
        csvdata = csv.reader(csvfile, delimiter=',', quotechar='|')
        try:
            for row in csvdata:
                count = count + 1
                try:
                    row_length = len(row)
                    if row_length < 1:
                        continue
                    if row_length < 4:
                        csv_file_error, error_line_no, invalid_emails = store_error(
                            error_line_no, count, invalid_emails)
                        continue
                    firstname = row[0].strip().title()
                    lastname = row[1].strip().title()
                    gender = row[3].strip().title()
                    email = row[2].strip().lower()
                    if not firstname or not gender or row_length < 4 or ((user.organiser.academic.institution_type.name != 'School' or (w and w.organiser.academic.institution_type.name != 'School')) and not email):
                        csv_file_error, error_line_no, invalid_emails = store_error(
                            error_line_no, count, invalid_emails)
                        continue
                    if row_length > 3 and email:
                        if not flag:
                            # print "firstname => ", firstname
                            if not validate_email(email, verify=True):
                                csv_file_error, error_line_no, invalid_emails = store_error(
                                    error_line_no, count, invalid_emails, email)
                                continue
                        # restrict the participant
                        more_then_two_per_day_list = can_allow_participant_to_attend(
                            more_then_two_per_day_list, tdate, email)
                        reattempt_list = is_new_participant(reattempt_list, foss, email)
                    if flag and flag <= 2 and not csv_file_error:
                        if not w:
                            return 1, error_line_no
                        get_or_create_participant(w, firstname, lastname, gender, email, 2)
                except Exception, e:
                    print e
                    csv_file_error, error_line_no, invalid_emails = store_error(error_line_no, count, invalid_emails)
            if error_line_no:
                error_line_no = """
                <ul>
                    <li>
                        The Line numbers {0} in CSV file data is not in a proper format in the Participant list. The format should be First name, Last name, Email, Gender.</br>
                        For more details <a href={1} target='_blank'>Click here</a>.
                        <hr>
                    </li>
                </ul>
                """.format(error_line_no, "http://process.spoken-tutorial.org/images/c/c2/Participant_data.pdf")
        except Exception, e:
            csv_file_error = 1
            error_line_no = """
                <ul>
                    <li>
                        The Line numbers {0} in CSV file data is not in a proper format in the Participant list. The format should be First name, Last name, Email, Gender.</br>
                        For more details <a href={1} target='_blank'>Click here</a>.
                        <hr>
                    </li>
                </ul>
                """.format(error_line_no, "http://process.spoken-tutorial.org/images/c/c2/Participant_data.pdf")
        if invalid_emails:
            error_line_no += """
                <ul>
                    <li>
                        The participants listed below do not have valid email-ids.  Pls create valid email-ids and upload once again.
                        <br><b>{0}</b>
                        <hr>
                    </li>
                </ul>
            """.format(invalid_emails)
        if flag == 3 and int(w.participant_count < count):
            csv_file_error = 1
            error_line_no = """
            <ul>
                <li>
                    Training participant count less than {0}.
                </li>
            </ul>
            """.format(w.participant_count)
        if more_then_two_per_day_list:
            csv_file_error = 1
            error_line_no += """
            <ul>
                <li>
                    The participants listed below have already enrolled for 2 software training workshops on the given date.
                    <br>
                    <b>NOTE:</b> Participants cannot enroll for more than 2 workshops per day. <b>{0}</b>
                    <hr>
                </li>
            </ul>
            """.format(more_then_two_per_day_list)
        if reattempt_list:
            if w:
                tps = w.trainingattendance_set.values_list('email')
            for p in tps:
                email = str(p[0])
                reattempt_list = reattempt_list.replace(',' + email, '').replace(email + ',', '').replace(email, '')
            if reattempt_list:
                csv_file_error = 1
                error_line_no += """
                <ul>
                    <li>
                        The participants listed below have already attended this software training workshop before. <br> <b>{0}</b><hr>
                    </li>
                </ul>
                """.format(reattempt_list)
    return csv_file_error, error_line_no


def clone_participant(training, form_data):
    tdate = None
    foss = None
    if form_data and 'foss' in form_data:
        tdate = form_data['tdate']
        foss = form_data['foss']

    csv_file_error = 0
    error_line_no = ''
    # invalid_emails = ''
    reattempt_list = ''
    more_then_two_per_day_list = ''
    count = 0
    participants = TrainingAttendance.objects.filter(training=training)
    for row in participants:
        count = count + 1
        email = row.email
        try:
            # restrict the participant
            more_then_two_per_day_list = can_allow_participant_to_attend(more_then_two_per_day_list, tdate, email)
            reattempt_list = is_new_participant(reattempt_list, foss, email)
        except Exception, e:
            print e

    if more_then_two_per_day_list:
        csv_file_error = 1
        error_line_no += """
        <ul>
            <li>
                The participants listed below have already enrolled for 2 software training workshops on the given date.
                <br>
                <b>NOTE:</b> Participants cannot enroll for more than 2 workshops per day. <b>{0}</b>
                <hr>
            </li>
        </ul>
        """.format(more_then_two_per_day_list)
    if reattempt_list:
        csv_file_error = 1
        error_line_no += """
        <ul>
            <li>
                The participants listed below have already attended this software training workshop before. <br> <b>{0}</b><hr>
            </li>
        </ul>
        """.format(reattempt_list)
    return csv_file_error, error_line_no, reattempt_list, more_then_two_per_day_list
