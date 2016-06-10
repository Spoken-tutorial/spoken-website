# Standard Library
import datetime
import os
import os.path

# Third Party Stuff
from dateutil.relativedelta import relativedelta
from django import template
from django.conf import settings

# Spoken Tutorial Stuff
from events.models import *
from events.views import (
    can_clone_training,
    is_administrator,
    is_event_manager,
    is_invigilator,
    is_organiser,
    is_resource_person
)

register = template.Library()


def participant_picture(user_id):
    if hasattr(settings, 'ONLINE_TEST_URL'):
        return settings.ONLINE_TEST_URL + "get_profile_picture.php?id=" + str(user_id)
    return None


def get_trainingstatus(key, training):
    wa = None
    try:
        wa = TrainingAttendance.objects.get(id=key, training=training)
    except TrainingAttendance.DoesNotExist:
        return ''

    if wa.status == 1:
        return 'checked'

    if wa.status > 1:
        return 'disabled=disabled checked'

    return ''


def get_trainingparticipant_status(key, wcode):
    status_list = ['Waiting for Attendance', 'Completed', 'Got certificate', 'Got certificate']
    try:
        wa = TrainingAttendance.objects.get(id=key, training_id=wcode)
    except:
        return 'error'
    return status_list[wa.status]


def participant_count(objects, category):
    if category == 'Training':
        try:
            return objects.trainingattendance_set.all().count()
        except Exception:
            return 0
    elif category == 'Test':
        try:
            count = objects.testattendance_set.all().count()
            if not count:
                return objects.training.participant_count
            return count
        except Exception:
            return 0


def can_close_test(testcode):
    # TODO: Probably a bad as the try block is never going to fail. try understand and fix it up.
    try:
        TestAttendance.objects.filter(test_id=testcode, status__range=(0, 3)).first()
    except:
        return True
    return False


def get_status(key, testcode):
    try:
        ta = TestAttendance.objects.get(mdluser_id=key, test_id=testcode)
    except:
        return 'error'

    if ta.status == 1:
        return 'checked'

    if ta.status > 1:
        return 'disabled=disabled checked'

    return ''


def get_participant_status(key, testcode):
    status_list = ['Waiting for Attendance', 'Ready for test', 'Ongoing Test', 'Test Completed', 'Certificate Issued']
    try:
        ta = TestAttendance.objects.get(mdluser_id=key, test_id=testcode)
    except:
        return 'Add'
    return status_list[ta.status]


def can_upload_final_training_list(tdate):
    try:
        date_after_one_month = tdate + relativedelta(days=30)
        if datetime.date.today() >= date_after_one_month:
            return True
        return False
    except Exception:
        return False


def can_download_workshop_certificate(key, training):
    try:
        wa = TrainingAttendance.objects.get(mdluser_id=key, training=training)
        if wa.status > 0:
            return wa.id
        return False
    except:
        return 'errors'


def can_enter_test(key, testcode):
    try:
        ta = TestAttendance.objects.get(mdluser_id=key, test_id=testcode)
    except:
        return None
    if ta.status >= 0:
        return ta.status
    return None


def training_file_exits(wid):
    file_path = settings.MEDIA_ROOT + 'training/' + str(wid) + '/' + str(wid) + '.pdf'
    if os.path.isfile(file_path):
        return True
    return False


def is_feedback_exits(w, record):
    return TrainingFeedback.objects.filter(training_id=w.id, mdluser_id=record.mdluser_id).exists()


def feedback_status_good(status):
    status_dict = {0: 'Very Bad', 1: 'Very Bad', 2: 'Bad', 3: 'Fair', 4: 'Good', 5: 'Very Good'}
    return status_dict[status]


def feedback_status_moderately(status):
    status_dict = {0: 'Not at All', 1: 'Not at All', 2: 'Slightly', 3: 'Moderately', 4: 'Very Good', 5: 'Extremely'}
    return status_dict[status]


def feedback_status_appropriate(status):
    status_dict = {0: 'Slow', 1: 'Slow', 2: 'Appropriate', 3: 'Fast'}
    return status_dict[status]


def feedback_status_satisfactory(status):
    status_dict = {0: 'Very Bad', 0: 'Very Bad', 1: 'Very Bad', 2: 'Bad', 3: 'Satisfactory', 4: 'Good', 5: 'Excellent'}
    return status_dict[status]


def feedback_status_somewhat(status):
    status_dict = {0: 'Very Bad', 0: 'Very Bad', 1: 'Very Bad',
                   2: 'A little bit', 3: 'Somewhat', 4: 'Quite a bit', 5: 'A lot'}
    return status_dict[status]


def feedback_status_average(status):
    status_dict = {0: 'Very Low', 1: 'Very Low', 2: 'Below average', 3: 'Average', 4: 'Above average', 5: 'Very High'}
    return status_dict[status]


def feedback_status_neutral(status):
    status_dict = {0: 'Strongly Disagree', 1: 'Strongly Disagree',
                   2: 'Disagree', 3: 'Likely', 4: 'Agree', 5: 'Strongly Agree'}
    return status_dict[status]


def feedback_status_likely(status):
    status_dict = {0: 'Not at All', 1: 'Not at All', 2: 'Maybe', 3: 'Likely', 4: 'Quite likely', 5: 'Definitely'}
    return status_dict[status]

register.filter('participant_picture', participant_picture)
register.filter('get_trainingstatus', get_trainingstatus)
register.filter('get_trainingparticipant_status', get_trainingparticipant_status)
register.filter('participant_count', participant_count)
register.filter('can_close_test', can_close_test)
register.filter('get_status', get_status)
register.filter('get_participant_status', get_participant_status)
register.filter('can_upload_final_training_list', can_upload_final_training_list)
register.filter('can_enter_test', can_enter_test)

register.filter('is_administrator', is_administrator)
register.filter('is_organiser', is_organiser)
register.filter('is_invigilator', is_invigilator)
register.filter('is_resource_person', is_resource_person)
register.filter('is_event_manager', is_event_manager)
register.filter('can_download_workshop_certificate', can_download_workshop_certificate)
register.filter('training_file_exits', training_file_exits)
register.filter('is_feedback_exits', is_feedback_exits)
register.filter('feedback_status_good', feedback_status_good)
register.filter('feedback_status_moderately', feedback_status_moderately)
register.filter('feedback_status_appropriate', feedback_status_appropriate)
register.filter('feedback_status_satisfactory', feedback_status_satisfactory)
register.filter('feedback_status_somewhat', feedback_status_somewhat)
register.filter('feedback_status_average', feedback_status_average)
register.filter('feedback_status_neutral', feedback_status_neutral)
register.filter('feedback_status_likely', feedback_status_likely)
register.filter('can_clone_training', can_clone_training)
