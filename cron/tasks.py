from __future__ import absolute_import, unicode_literals
import csv
from builtins import str
import time
import os, sys
# setting django environment
from django.core.wsgi import get_wsgi_application
from config import *
sys.path.append(SPOKEN_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from .models import AsyncCronMail, CertificateBatch
from datetime import datetime, date  
from django.utils import timezone
from django.conf import settings
import uuid
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from smtplib import SMTPException, SMTPServerDisconnected
from django.core.mail import BadHeaderError
from rq.decorators import job
from cron import REDIS_CLIENT, DEFAULT_QUEUE, TOPPER_QUEUE, CERTIFICATE_QUEUE
from rq import Retry
import time
from rq import get_current_job
from django.core.cache import caches
from mdldjango.models import MdlUser, MdlQuizGrades
from events.models import FossMdlCourses, TestAttendance, State, City, InstituteType
from creation.models import FossCategory

from django.db import transaction
from training.models import TrainingAttend
from events.models import Test, TestAttendance
from mdldjango.helper import get_moodle_user
from events.helpers import get_fossmdlcourse
from django.db import close_old_connections
# from events.views import update_events_log, update_events_notification
import logging
import traceback
from io import BytesIO
from datetime import timedelta
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from PyPDF2 import PdfFileWriter, PdfFileReader
from events import certificates as certs
from events.certificates import (
    get_test_certificate,
    get_training_certificate,
    get_signature,
    get_test_cert_text,
    get_training_cert_text,
)
import random
import string

logger = logging.getLogger(__name__)


def _id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def _custom_strftime(format, t):
    return t.strftime(format)


def _ensure_certificate_date():
    if isinstance(certs.EDUPYRAMIDS_CERTIFICATE_DATE, date):
        return
    if not certs.EDUPYRAMIDS_CERTIFICATE_DATE:
        certs.EDUPYRAMIDS_CERTIFICATE_DATE = date.max
        return
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            certs.EDUPYRAMIDS_CERTIFICATE_DATE = datetime.strptime(
                certs.EDUPYRAMIDS_CERTIFICATE_DATE, fmt
            ).date()
            return
        except ValueError:
            continue
    certs.EDUPYRAMIDS_CERTIFICATE_DATE = date.max



def bulk_email(taskid, *args, **kwargs):
    task = AsyncCronMail.objects.get(pk=taskid)
    if  task.log_file.name == "":
        log_file_name = 'log_email_'+uuid.uuid4().hex+".csv"
        task.log_file.name = 'emails/' + log_file_name
        task.save()
    with open(settings.MEDIA_ROOT + task.log_file.name, "a") as log_file:
        with open(task.csvfile.path, newline='') as csvfile:
            csvreader = list(csv.reader(csvfile, delimiter=' ', quotechar='|'))
            job = get_current_job()
            try:
                row_id=int(job.meta['row_id'])
            except:
                row_id =0
            try:
                sent=int(job.meta['sent'])
            except:
                sent=0
            try:
                errors=int(job.meta['errors'])
            except:
                errors=0
            for i,row in enumerate(csvreader[row_id:], row_id):
                job.meta['row_id'] = i
                job.save_meta()
                if len(row) < 1:
                    continue
                if i%10 == 0:
                        print('Total ran: ',i)
                        time.sleep(5)
                email = EmailMultiAlternatives(
                            task.subject, task.message, task.sender,
                            to = [row[0]],
                            headers = {
                                        "Content-type" : "text/html"
                                    }
                        )
                try:
                    validate_email(row[0])
                    email.attach_alternative(task.message, "text/html")
                    email.send()
                    sent += 1
                    job.meta['sent'] = sent
                    job.save_meta()
                    log_file.write(str(row[0])+','+str(1)+'\n')
                except ValidationError as mail_error:
                    log_file.write(str(row[0])+','+str(0)+','+str(mail_error)+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()
                except SMTPException as send_error:
                    log_file.write(str(row[0])+','+str(0)+','+str('SMTP mail send error.')+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()
                except BadHeaderError as header_error:
                    log_file.write(str(row[0])+','+str(0)+','+str(header_error)+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()
                except ConnectionRefusedError as refused:
                    log_file.write(str(row[0])+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
                    errors+=1
                except SMTPServerDisconnected as disconnect:
                    log_file.write(str(row[0])+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()
                except OSError as e:
                    log_file.write(str(row[0])+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()

            task.completed_at = timezone.now()
            task.report = "Total: "+ str(sent+errors)+"\n"+ "Sent: "\
                    +str(sent)+"\n"+"Errors: "+ str(errors)
            task.status=True
            task.save()

def async_bulk_email(task, *args, **kwargs):
    DEFAULT_QUEUE.enqueue(bulk_email, task.pk, job_id=task.job_id, job_timeout='72h')


def filter_student_grades(key=None):
  key_array=key.split(':')
  foss=FossCategory.objects.filter(pk__in=[int(f) for f in key_array[0].split(';')])
  state=State.objects.filter(pk__in=[int(s) if s != '' else None  for s in key_array[1].split(';')])
  city=City.objects.filter(pk__in=[int(c) if c != '' else None for c in key_array[2].split(';')])
  institution_type=InstituteType.objects.filter(pk__in=[int(i) if i != '' else None for i in key_array[4].split(';')])
  grade=int(key_array[3])
  activation_status=int(key_array[5]) if key_array[5]!= '' else None
  from_date= key_array[6] if key_array[6] != 'None' else None
  to_date= key_array[7] if key_array[7] != 'None' else None
  if grade:
    #get the moodle id for the foss
    try:
      fossmdl=FossMdlCourses.objects.filter(foss__in=foss)
      #get moodle user grade for a specific foss quiz id having certain grade
      if from_date and to_date:
        user_grade=MdlQuizGrades.objects.using('moodle').values_list('userid', 'quiz', 'grade').filter(quiz__in=[f.mdlquiz_id for f in fossmdl], grade__gte=int(grade), timemodified__range=[datetime.strptime(from_date,"%Y-%m-%d").timestamp(), datetime.strptime(to_date,"%Y-%m-%d").timestamp()])
      elif from_date:
        user_grade=MdlQuizGrades.objects.using('moodle').values_list('userid', 'quiz', 'grade').filter(quiz__in=[f.mdlquiz_id for f in fossmdl], grade__gte=int(grade), timemodified__gte=datetime.strptime(from_date,"%Y-%m-%d").timestamp())

      #convert moodle user and grades as key value pairs
      dictgrade = {i[0]:{i[1]:[i[2],False]} for i in user_grade}
      #get all test attendance for moodle user ids and for a specific moodle quiz ids
      test_attendance=TestAttendance.objects.filter(
                                mdluser_id__in=list(dictgrade.keys()), 
                                mdlquiz_id__in=[f.mdlquiz_id for f in fossmdl], 
                                test__academic__state__in=state if state else State.objects.all(),
                                test__academic__city__in=city if city else City.objects.all(), 
                                status__gte=3, 
                                test__academic__institution_type__in=institution_type if institution_type else InstituteType.objects.all(), 
                                test__academic__status__in=[activation_status] if activation_status else [1,3]
                              )
        
      filter_ta=[]
      for i in range(test_attendance.count()):
        key_quiz = dictgrade.get(test_attendance[i].mdluser_id).get(test_attendance[i].mdlquiz_id)
        if key_quiz:
          if not key_quiz[1]:
            dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1] = True
            filter_ta.append(test_attendance[i])
          
      #return the result as dict
      result= {'mdl_user_grade': dictgrade, 'test_attendance': filter_ta, "count":len(filter_ta)}
      caches['file_cache'].set(key,result)
      if not TOPPER_WORKER_STATUS:
          return result
    except FossMdlCourses.DoesNotExist:
      return None
  return None


def async_filter_student_grades(key):
    TOPPER_QUEUE.enqueue(filter_student_grades, key, job_id=key, job_timeout='72h')



def process_test_attendance(test_id, user_id, message, academic_id):
    from events.views import (
        update_events_log,
        update_events_notification
    )
    """
    Background task:
    - Create TestAttendance
    - Sync Moodle users
    """
    close_old_connections()
    job = get_current_job()

    print(f"\033[92m job ****** {job} \033[0m")
    def meta_update(**updates):
        """Update RQ job meta safely"""
        if not job:
            return
        job.meta.update(updates)
        job.save_meta()

    meta_update(
        test_id=test_id,
        status="starting",
        started_at=int(time.time()),
        progress_total=0,
        progress_processed=0,
        progress_pct=0,
        stats_created_attendance=0,
        stats_skipped_existing=0,
        stats_missing_moodle=0,
        message="Starting attendance processing.."
    )

    try:
        test = Test.objects.select_related('training', 'foss').get(pk=test_id)
    except Test.DoesNotExist:
        meta_update(status="done", message="Test not found. Exiting")
        return

    if not test.training_id:
        meta_update(status="done", message="No training attached to test. Exiting.")
        return

    meta_update(status="running", message="Loading training attendees...")

    tras = TrainingAttend.objects.select_related(
        'student__user',
        'training__training_planner'
    ).filter(training=test.training)

    fossmdlcourse = get_fossmdlcourse(
        test.foss_id,
        fossmdlmap_id=test.training.fossmdlmap_id
    )

    # total count for progress (1 extra query; useful for dashboard)
    total = tras.count()
    meta_update(progress_total=total, progress_processed=0, progress_pct=0)

    existing = set(
        TestAttendance.objects.filter(test=test)
        .values_list("student_id", "mdluser_id")
    )

    mdluser_cache = {}
    new_rows = []

    processed = 0
    skipped_existing = 0
    missing_moodle = 0

    # Update job meta every N rows to avoid excessive Redis writes
    UPDATE_EVERY = 10
    meta_update(message=f"Processing {total} attendees...")
    
    for tra in tras.iterator():
        user = tra.student.user

        key = (
            tra.training.training_planner.academic_id,
            user.first_name,
            user.last_name,
            tra.student.gender,
            user.email
        )

        if key not in mdluser_cache:
            mdluser_cache[key] = get_moodle_user(*key)

        mdluser = mdluser_cache[key]
        if not mdluser:
            missing_moodle += 1
            processed += 1
            # progress update
            if (processed % UPDATE_EVERY == 0) or (processed == total):
                pct = int((processed * 100) / total) if total else 100
                meta_update(
                    progress_processed=processed,
                    progress_pct=pct,
                    stats_created_attendance=len(new_rows),
                    stats_skipped_existing=skipped_existing,
                    stats_missing_moodle=missing_moodle,
                    message=f"Processing... ({processed}/{total})",
                )
            continue

        pair = (tra.student.id, mdluser.id)
        if pair in existing:
            skipped_existing += 1
            processed += 1
            if (processed % UPDATE_EVERY == 0) or (processed == total):
                pct = int((processed * 100) / total) if total else 100
                meta_update(
                    progress_processed=processed,
                    progress_pct=pct,
                    stats_created_attendance=len(new_rows),
                    stats_skipped_existing=skipped_existing,
                    stats_missing_moodle=missing_moodle,
                    message=f"Processing... ({processed}/{total})",
                )
            continue

        new_rows.append(
            TestAttendance(
                student_id=tra.student.id,
                test=test,
                mdluser_id=mdluser.id,
                mdlcourse_id=fossmdlcourse.mdlcourse_id,
                mdlquiz_id=fossmdlcourse.mdlquiz_id,
                mdlattempt_id=0,
                status=0
            )
        )
    processed += 1

    if (processed % UPDATE_EVERY == 0) or (processed == total):
            pct = int((processed * 100) / total) if total else 100
            meta_update(
                progress_processed=processed,
                progress_pct=pct,
                stats_created_attendance=len(new_rows),
                stats_skipped_existing=skipped_existing,
                stats_missing_moodle=missing_moodle,
                message=f"Processing... ({processed}/{total})",
        )

    # --- write phase ---
    meta_update(status="writing", message=f"Writing {len(new_rows)} new TestAttendance rows...")

    if new_rows:
        close_old_connections()
        with transaction.atomic():
            TestAttendance.objects.bulk_create(new_rows)

    update_events_log(user_id=user_id, role=0, category=1, category_id=test_id, academic=academic_id,status=0)

    update_events_notification(user_id=user_id, role=0, category=1, category_id=test_id, academic=academic_id, status=0,message=message)
    meta_update(
        status="done",
        finished_at=int(time.time()),
        stats_created_attendance=len(new_rows),
        stats_skipped_existing=skipped_existing,
        stats_missing_moodle=missing_moodle,
        progress_processed=total,
        progress_pct=100,
        message="Done.",
    )


def process_test_post_save(test_id, user_id, message,academic_id):
    """
    Background task:
    - Event log
    - Notifications
    """
    close_old_connections()
    from events.views import (
        update_events_log,
        update_events_notification
    )

    update_events_log(
        user_id=user_id,
        role=0,
        category=1,
        category_id=test_id,
        academic=academic_id,
        status=0
    )

    update_events_notification(
        user_id=user_id,
        role=0,
        category=1,
        category_id=test_id,
        academic=academic_id,
        status=0,
        message=message
    )


def async_process_test_attendance(test, user, message):
    print(f"\033[92m Adding task to process_test_attendance \033[0m")
    print(f"\033[93m test.pk : {test.pk} \033[0m")
    DEFAULT_QUEUE.enqueue(
        process_test_attendance,
        test.pk,
        user.pk,
        message,
        test.academic_id,
        job_id="test_attendance_%s" % test.pk,
        job_timeout='72h'
    )
    print(f"\033[92m Added test attendance job successfully \033[0m")


def async_test_post_save(test, user, message):
    DEFAULT_QUEUE.enqueue(
        process_test_post_save,
        test.pk,
        user.pk,
        message,
        test.academic_id,
        job_id="test_post_save_%s" % test.pk,
        job_timeout='24h'
    )
    print(f"\033[92m Added async_test_post_save job successfully \033[0m")


def _merge_overlay_page(output, template_path, overlay_buffer):
    # Merge overlay onto template and add to output
    with open(template_path, "rb") as template_file:
        template_bytes = template_file.read()
    page = PdfFileReader(BytesIO(template_bytes)).getPage(0)
    overlay = PdfFileReader(BytesIO(overlay_buffer.getvalue())).getPage(0)
    if hasattr(page, "merge_page"):
        page.merge_page(overlay)
    else:
        page.mergePage(overlay)
    output.addPage(page)


def _build_test_overlay(ta, test, mdluser, mdlgrade):
    _ensure_certificate_date()
    img_temp = BytesIO()
    img_doc = canvas.Canvas(img_temp)

    if ta.test.training.department.id != 169:
        img_doc.setFont('Helvetica', 18, leading=None)
        img_doc.drawCentredString(211, 115, _custom_strftime('%d %B %Y', test.tdate))

    img_doc.setFillColorRGB(0, 0, 0)
    img_doc.setFont('Helvetica', 10, leading=None)
    img_doc.drawString(10, 6, ta.password)

    img_path = get_signature(ta.test.tdate)
    img_doc.drawImage(img_path, 600, 95, 150, 76)

    credits = "<p><b>Credits:</b> " + str(test.foss.credits) + "&nbsp&nbsp&nbsp<b>Score:</b> " + str('{:.2f}'.format(mdlgrade.grade)) + "%</p>"
    text = get_test_cert_text(ta.test, mdluser, credits=credits)
    centered = ParagraphStyle(
        name='centered',
        fontSize=15,
        leading=24,
        alignment=1,
        spaceAfter=20
    )
    p = Paragraph(text, centered)
    p.wrap(700, 200)
    p.drawOn(img_doc, 3 * cm, 6.5 * cm)

    text = "Certificate for Completion of <br/>" + test.foss.foss + " Training"
    centered = ParagraphStyle(
        name='centered',
        fontSize=25,
        leading=25,
        alignment=1,
        spaceAfter=15
    )
    p = Paragraph(text, centered)
    p.wrap(500, 20)
    p.drawOn(img_doc, 6.2 * cm, 17 * cm)

    img_doc.save()
    return img_temp


def _build_training_overlay(ta, training_end):
    _ensure_certificate_date()
    img_temp = BytesIO()
    img_doc = canvas.Canvas(img_temp)

    img_doc.setFont('Helvetica', 35, leading=None)
    img_doc.drawCentredString(405, 480, "Certificate of Participation")

    if ta.training.department.id != 169:
        img_doc.setFont('Helvetica', 18, leading=None)
        img_doc.drawCentredString(211, 115, _custom_strftime('%d %B %Y', training_end))

    img_doc.setFillColorRGB(211, 211, 211)
    img_doc.setFont('Helvetica', 10, leading=None)
    img_doc.drawString(10, 6, "")

    img_path = get_signature(ta.training.training_start_date)
    img_doc.drawImage(img_path, 600, 100, 150, 76)

    text = get_training_cert_text(ta)
    centered = ParagraphStyle(
        name='centered',
        fontSize=16,
        leading=30,
        alignment=0,
        spaceAfter=20
    )
    p = Paragraph(text, centered)
    p.wrap(630, 200)
    p.drawOn(img_doc, 4.2 * cm, 7 * cm)
    img_doc.save()
    return img_temp


def _generate_test_certificates(batch):
    if not batch.test_id:
        raise ValueError("Test batch is missing test")

    test = Test.objects.select_related(
        'training',
        'training__department',
        'academic',
        'foss',
        'organiser__user',
        'invigilator__user'
    ).get(pk=batch.test_id)

    test_attendances = TestAttendance.objects.select_related(
        'test',
        'test__training',
        'test__training__department',
        'test__academic',
        'test__foss',
        'test__organiser__user',
        'test__invigilator__user'
    ).filter(test_id=batch.test_id)

    quiz_ids = {ta.mdlquiz_id for ta in test_attendances}
    user_ids = {ta.mdluser_id for ta in test_attendances}
    grades = MdlQuizGrades.objects.using('moodle').filter(quiz__in=quiz_ids, userid__in=user_ids)
    grades_by_key = {(g.quiz, g.userid): g for g in grades}
    users_by_id = MdlUser.objects.using('moodle').in_bulk(user_ids)

    output = PdfFileWriter()

    for ta in test_attendances:
        mdlgrade = grades_by_key.get((ta.mdlquiz_id, ta.mdluser_id))
        mdluser = users_by_id.get(ta.mdluser_id)
        if not mdlgrade or not mdluser:
            continue
        if ta.status < 1 or round(mdlgrade.grade, 1) < 40:
            continue

        if ta.password:
            certificate_pass = ta.password
        else:
            pad_len = max(0, 10 - len(str(ta.mdluser_id)))
            certificate_pass = str(ta.mdluser_id) + _id_generator(pad_len)
            ta.password = certificate_pass

        ta.count += 1
        ta.status = 4
        ta.save(update_fields=["password", "count", "status", "updated"])

        overlay = _build_test_overlay(ta, test, mdluser, mdlgrade)
        template_path = get_test_certificate(ta)
        _merge_overlay_page(output, template_path, overlay)

    return output


def _generate_training_certificates(batch):
    if not batch.training_id:
        raise ValueError("Training batch is missing training")

    ta_list = TrainingAttend.objects.select_related(
        'student__user',
        'training',
        'training__department',
        'training__course__foss',
        'training__training_planner__academic',
        'training__training_planner__organiser__user'
    ).filter(training_id=batch.training_id)

    output = PdfFileWriter()

    for ta in ta_list:
        training_end = ta.training.sem_start_date + timedelta(days=60)
        overlay = _build_training_overlay(ta, training_end)
        template_path = get_training_certificate(ta)
        _merge_overlay_page(output, template_path, overlay)

    return output


def _get_certificate_output_path(batch):
    cert_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
    os.makedirs(cert_dir, exist_ok=True)
    type_label = 'test' if batch.batch_type == 1 else 'training'
    filename = "certificate_batch_%s_%s.pdf" % (batch.id, type_label)
    rel_path = os.path.join('certificates', filename)
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    return rel_path, abs_path


def generate_certificate_batch(batch_id):
    # Generate merged certificates 
    close_old_connections()
    _ensure_certificate_date()
    batch = CertificateBatch.objects.select_related('test', 'training').get(pk=batch_id)
    logger.info("Starting certificate batch %s", batch.id)

    batch.status = 1
    batch.started_at = timezone.now()
    batch.error = None
    batch.save(update_fields=["status", "started_at", "error"])

    try:
        if batch.batch_type == 1:
            output = _generate_test_certificates(batch)
        elif batch.batch_type == 2:
            output = _generate_training_certificates(batch)
        else:
            raise ValueError("Unsupported certificate batch type: %s" % batch.batch_type)

        rel_path, abs_path = _get_certificate_output_path(batch)
        with open(abs_path, "wb") as output_file:
            output.write(output_file)

        batch.output_path = rel_path
        batch.status = 2
        batch.completed_at = timezone.now()
        batch.save(update_fields=["output_path", "status", "completed_at"])
        logger.info("Completed certificate batch %s", batch.id)
    except Exception:
        batch.status = 3
        batch.error = traceback.format_exc()
        batch.completed_at = timezone.now()
        batch.save(update_fields=["status", "error", "completed_at"])
        logger.exception("Certificate batch %s failed", batch.id)
        raise


def async_generate_certificate_batch(batch):
    job = CERTIFICATE_QUEUE.enqueue(
        generate_certificate_batch,
        batch.pk,
        job_timeout='72h'
    )
    batch.rq_job_id = job.id
    batch.status = 0
    batch.save(update_fields=["rq_job_id", "status"])
