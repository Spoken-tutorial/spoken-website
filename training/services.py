from __future__ import unicode_literals

import csv
import datetime as dt

from django.db.models import Q
from django.http import HttpResponse
from django.template.defaultfilters import slugify

from mdldjango.models import MdlQuizGrades, MdlUser

from .models import ILWFossMdlCourses, Participant


CSV_HEADERS = [
    'Sl.No',
    'Learner Email ID',
    'Learner Name',
    'Registered Date',
    'Course ID in SWAYAM Plus',
    'SWAYAM Plus Redirect Referal ID',
    'Course Name',
    'NCrF aligned course?',
    'Type of course',
    'Payment_Status',
    'Course Completion Status',
    'Course Completion Date',
    'Participation Certificate Status',
    'Assessment Certificate Status',
    'Assessment Certificate Issued Date',
]


def format_ddmmyyyy(value):
    if not value:
        return ''
    if hasattr(value, 'strftime'):
        return value.strftime('%d/%m/%Y')
    return ''


def get_swayam_participants(event):
    return (
        Participant.objects.filter(event=event)
        .select_related('payment_status', 'payment_status__transaction', 'user')
        .order_by('created', 'id')
    )


def resolve_moodle_quiz_id(event):
    course = getattr(event, 'course', None)
    if course:
        course_foss_ids = list(course.foss.all().values_list('id', flat=True))
        if course_foss_ids:
            quiz_id = (
                ILWFossMdlCourses.objects.filter(foss_id__in=course_foss_ids)
                .order_by('foss_id')
                .values_list('mdlquiz_id', flat=True)
                .first()
            )
            if quiz_id:
                return quiz_id

    if event.foss_id:
        quiz_id = (
            ILWFossMdlCourses.objects.filter(foss_id=event.foss_id)
            .values_list('mdlquiz_id', flat=True)
            .first()
        )
        if quiz_id:
            return quiz_id

    return None


def get_moodle_user_map(user_ids):
    normalized_user_ids = sorted({user_id for user_id in user_ids if user_id})
    if not normalized_user_ids:
        return {}

    users = (
        MdlUser.objects.using('moodle')
        .filter(id__in=normalized_user_ids)
        .only('id', 'email', 'username')
    )

    user_map = {}
    for user in users:
        user_map[user.id] = user
    return user_map


def get_moodle_grade_map(user_ids, quiz_id):
    if not user_ids or not quiz_id:
        return {}

    grade_map = {}
    grades = (
        MdlQuizGrades.objects.using('moodle')
        .filter(userid__in=user_ids, quiz=quiz_id)
        .order_by('userid', '-timemodified')
        .only('userid', 'quiz', 'timemodified')
    )

    for grade in grades:
        if grade.userid not in grade_map:
            grade_map[grade.userid] = grade
    return grade_map


def get_payment_status_label(participant, course_type):
    if course_type == 'Free':
        return 'NA'

    if participant.registartion_type in (1, 3):
        return 'Free for subscribed colleges'

    payment_status = participant.payment_status
    if payment_status and (payment_status.status == 1 or (payment_status.transaction and payment_status.transaction.order_status == 'CHARGED')):
        return 'Paid'

    return 'Not Paid'


def build_swayam_export_rows(event, metadata):
    participants = list(get_swayam_participants(event))
    quiz_id = resolve_moodle_quiz_id(event)

    moodle_user_map = get_moodle_user_map([participant.user_id for participant in participants])
    moodle_grade_map = get_moodle_grade_map(
        [user.id for user in moodle_user_map.values()],
        quiz_id,
    )

    rows = []
    for index, participant in enumerate(participants, start=1):
        email = (participant.email or '').strip()
        moodle_user = moodle_user_map.get(participant.user_id)
        moodle_grade = moodle_grade_map.get(moodle_user.id) if moodle_user else None

        rows.append([
            index,
            email,
            participant.name or (participant.user.get_full_name() if participant.user_id else ''),
            format_ddmmyyyy(participant.created),
            metadata['swayam_course_id'],
            metadata['swayam_plus_redirect_referal_id'],
            metadata['course_name'],
            metadata['ncrf_aligned_course'],
            metadata['course_type'],
            get_payment_status_label(participant, metadata['course_type']),
            metadata['course_completion_status'],
            format_ddmmyyyy(metadata['course_completion_date']),
            metadata['participation_certificate_status'],
            metadata['assessment_certificate_status'],
            format_ddmmyyyy(dt.datetime.utcfromtimestamp(moodle_grade.timemodified)) if moodle_grade and moodle_grade.timemodified else '',
        ])

    return rows, quiz_id


def build_swayam_csv_response(event, metadata):
    rows, quiz_id = build_swayam_export_rows(event, metadata)
    filename = slugify('%s-swayam-participant-data' % event.event_name) or 'swayam-participant-data'

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename

    writer = csv.writer(response)
    writer.writerow(CSV_HEADERS)
    for row in rows:
        writer.writerow(row)

    return response, quiz_id