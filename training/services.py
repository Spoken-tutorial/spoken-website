from __future__ import unicode_literals

import csv
import datetime as dt
import logging

logger = logging.getLogger(__name__)

from django.db.models import Q
from django.http import HttpResponse
from django.template.defaultfilters import slugify

from mdldjango.models import MdlQuizGrades, MdlUser
from events.models import Student, StudentMaster
from donate.subscription import has_active_subscription

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
                logger.warning(
                    "SWAYAM quiz resolved | event_id=%s | event_foss_id=%s | course_id=%s | quiz_id=%s",
                    event.id,
                    event.foss_id,
                    course.id if course else None,
                    quiz_id,
                )
                return quiz_id

    if event.foss_id:
        quiz_id = (
            ILWFossMdlCourses.objects.filter(foss_id=event.foss_id)
            .values_list('mdlquiz_id', flat=True)
            .first()
        )
        if quiz_id:
            logger.warning(
                "SWAYAM quiz resolved | event_id=%s | event_foss_id=%s | course_id=%s | quiz_id=%s",
                event.id,
                event.foss_id,
                course.id if course else None,
                quiz_id,
            )
            return quiz_id

    logger.warning(
        "SWAYAM quiz resolve failed | event_id=%s | event_foss_id=%s | course_id=%s",
        event.id,
        event.foss_id,
        course.id if course else None,
    )
    return None


def get_moodle_user_map(participants):
    emails = []
    for p in participants:
        if p.email:
            emails.append(p.email.strip())
        elif p.user and p.user.email:
            emails.append(p.user.email.strip())

    normalized_emails = sorted({email.lower() for email in emails if email})
    if not normalized_emails:
        logger.warning(
            "SWAYAM moodle user mapping skipped | participant_count=%s | normalized_email_count=0",
            len(participants),
        )
        return {}

    moodle_users = (
        MdlUser.objects.using('moodle')
        .filter(email__in=normalized_emails)
        .only('id', 'email', 'username')
    )

    email_to_moodle = {mu.email.lower(): mu for mu in moodle_users}

    user_map = {}
    for p in participants:
        p_email = (p.email or (p.user.email if p.user_id else '')).strip().lower()
        if p.user_id and p_email in email_to_moodle:
            user_map[p.user_id] = email_to_moodle[p_email]

    logger.warning(
        "SWAYAM moodle user mapping | participant_count=%s | normalized_email_count=%s | moodle_users_found=%s | mappings_created=%s",
        len(participants),
        len(normalized_emails),
        len(moodle_users),
        len(user_map),
    )
    return user_map


def get_moodle_grade_map(user_ids, quiz_id):
    if not user_ids or not quiz_id:
        logger.warning(
            "SWAYAM moodle grade mapping skipped | quiz_id=%s | user_ids_count=%s",
            quiz_id,
            len(user_ids) if user_ids else 0,
        )
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

    logger.warning(
        "SWAYAM moodle grade mapping | quiz_id=%s | user_ids_count=%s | grades_found=%s",
        quiz_id,
        len(user_ids),
        len(grade_map),
    )
    return grade_map


def get_payment_status_label(participant, course_type=None):
    is_subscribed = False
    if participant.user_id:
        try:
            student = Student.objects.get(user_id=participant.user_id)
            academic_ids = StudentMaster.objects.filter(student=student).values_list('batch__academic_id', flat=True)
            for academic_id in academic_ids:
                if academic_id and has_active_subscription(academic_id):
                    is_subscribed = True
                    break
        except Student.DoesNotExist:
            pass

    if is_subscribed:
        return 'Free for subscribed colleges'

    siblings = Participant.objects.filter(
        event=participant.event,
        user=participant.user
    ).select_related('payment_status', 'payment_status__transaction')

    for sibling in siblings:
        ps = sibling.payment_status
        if ps and (ps.status == 1 or (ps.transaction and ps.transaction.order_status == 'CHARGED')):
            return 'Paid'

    for sibling in siblings:
        ps = sibling.payment_status
        if ps and (ps.status == 1 or (ps.transaction and ps.transaction.order_status == 'CHARGED')):
            return 'Paid'

    # Step 3: Default
    return 'Not Paid'


def build_swayam_export_rows(event, metadata):
    participants = list(get_swayam_participants(event))
    participants.sort(key=lambda p: (p.email or (p.user.email if p.user_id else '')).strip().lower())
    quiz_id = resolve_moodle_quiz_id(event)

    moodle_user_map = get_moodle_user_map(participants)
    moodle_grade_map = get_moodle_grade_map(
        [user.id for user in moodle_user_map.values()],
        quiz_id,
    )

    rows = []
    for index, participant in enumerate(participants, start=1):
        email = (participant.email or '').strip()
        moodle_user = moodle_user_map.get(participant.user_id)
        moodle_grade = moodle_grade_map.get(moodle_user.id) if moodle_user else None
        final_val = format_ddmmyyyy(dt.datetime.utcfromtimestamp(moodle_grade.timemodified)) if moodle_grade and moodle_grade.timemodified else ''

        logger.warning(
            "SWAYAM participant export row | participant_id=%s | participant_email=%s | user_id=%s | moodle_user_found=%s | moodle_user_id=%s | moodle_grade_found=%s | timemodified=%s | final_val=%s",
            participant.id,
            email,
            participant.user_id,
            moodle_user is not None,
            moodle_user.id if moodle_user else None,
            moodle_grade is not None,
            moodle_grade.timemodified if moodle_grade else None,
            final_val,
        )

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
            final_val,
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