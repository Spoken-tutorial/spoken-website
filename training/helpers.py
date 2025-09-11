from events.models import *
from training.models import *
from donate.models import *
from datetime import datetime,date
from certificate.views import _clean_certificate_certificate
from django.http import HttpResponse
import os
from string import Template
import subprocess
from django.db.models import Count
from django.conf import settings
from spoken.config import EDUPYRAMIDS_CERTIFICATE_DATE
from events.certificates import get_organization


EVENT_AMOUNT = {
     'FDP': '500', 'Workshop': '1000'
    }

REGISTRATION_TYPE_CHOICES =(
    ('', '-----'),  (1, 'Subscribed College'),(2, 'Manual Registration')
    )

def is_user_paid(academic_id):
    idcase = AcademicKey.objects.filter(academic_id=academic_id).order_by('-expiry_date').first()
    return (idcase and (idcase.expiry_date >= date.today()))

def user_college(user_obj):
    college = ''
    try:
        college = user_obj.organiser.academic
    except Exception as e1:
        try:
             college = user_obj.invigilator.academic
        except Exception as e2:
             #try:
             #      studentbatch_id = user_obj.student.studentmaster_set.values('batch_id')
             #      batch = StudentBatch.objects.get(id=studentbatch_id)
             #      college = batch.academic
             #except:
             #      #user is not associated with any college
             pass
    return college

def handle_uploaded_file(request):
    return "successfull"


def is_college_paid(college_id):
    try:
        idcase = AcademicKey.objects.filter(academic_id=college_id).order_by('-expiry_date').first()
        college_paid = True if (idcase.expiry_date >= date.today()) else False
        return college_paid
    except Exception as e:
        college_paid = False
    return college_paid

def create_certificate(eventid,pname):
    response = HttpResponse(content_type='application/pdf')
    event = TrainingEvents.objects.get(id=eventid)
    try:        
        file_name = pname
        template = 'fdp_cert_template/training_certificate_template'
        download_file_name = "ST_"+event.event_name+'.pdf'
        certificate_path = os.path.dirname(os.path.realpath(__file__))+"/certificate/"
        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()
        foss = format_foss_list([x.foss for x in event.course.foss.all()])
        content_tex = content.safe_substitute(
            name = pname,
            event_name = event.event_name,
            college = event.host_college.institution_name,
            host_college = event.host_college.institution_name,
            foss = foss,
            event_start_date = event.event_start_date
            )
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        out = certificate_path
        
        subprocess.run(['pdflatex','--output-directory',certificate_path,certificate_path+file_name+'.tex'])
        pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'rb')
        response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
        response.write(pdf.read())
        _clean_certificate_certificate(certificate_path, file_name)
        return response
    except Exception as e:
        print("error is ",e)


def get_transaction_details(request, purpose):
    user = User.objects.get(id=request.user.id)
    rp_states = ResourcePerson.objects.filter(status=1,user=user)
    state = State.objects.filter(id__in=rp_states.values('state')).values('name')

    get_state = ''
    allpaydetails = ''

    if purpose == 'cdcontent':
        allpaydetails = PaymentTransaction.objects.filter(paymentdetail__purpose='cdcontent', paymentdetail__state__in=state).order_by('-created').select_related('paymentdetail', 'paymentdetail__user')
        
    else:
        rp_events = TrainingEvents.objects.filter(state__name__in = state)
        allpaydetails = PaymentTransaction.objects.filter(paymentdetail__purpose__in=rp_events).exclude(paymentdetail__purpose='cdcontent').order_by('-created').select_related('paymentdetail', 'paymentdetail__user')

    selected_state = request.GET.get('state')
    academic_center = request.GET.get('college')
    selected_event = request.GET.get('events')
    status = request.GET.get('status')
    request_type = request.GET.get('request_type')
    email=request.GET.get('user_email')
    userid=request.GET.get('userid')
    fdate = request.GET.get('fdate')
    tdate = request.GET.get('tdate')

    if selected_state:
        get_state = State.objects.filter(id=selected_state).values('name')

    if academic_center in ('None','0',0):
        academic_center = False
    else:
        academic_center = request.GET.get('college')

    if selected_event in ('None','0',0):
        selected_event = False

    else:
        selected_event = request.GET.get('events')
    

    if purpose == 'cdcontent':
        if get_state:
            paymentdetails=allpaydetails.filter(paymentdetail__state=get_state)
        else:
            paymentdetails=allpaydetails.filter(paymentdetail__state__in=state)
        if request.GET.get('user_email'):
            email=request.GET.get('user_email')
            paymentdetails = paymentdetails.filter(paymentdetail__email=email).order_by('-created')
        if request.GET.get('userid'):
            userid=request.GET.get('userid')
            paymentdetails = paymentdetails.filter(paymentdetail__user_id=userid).order_by('-created')

    else:#purpose event
        # allpaydetails = PaymentTransaction.objects.filter().exclude(paymentdetail__purpose='cdcontent').order_by('-created')

        if get_state:
            academic_centers = AcademicCenter.objects.filter(state__name=get_state)

            if academic_center:
                events = TrainingEvents.objects.filter(host_college = academic_center)
                if selected_event:
                    e = TrainingEvents.objects.get(id=selected_event)
                    paymentdetails = allpaydetails.filter(paymentdetail__purpose=e.id)
                else:
                    paymentdetails = allpaydetails.filter(paymentdetail__purpose__in=events)

            else:
                events = TrainingEvents.objects.filter(host_college__in = academic_centers)
                paymentdetails = allpaydetails.filter(paymentdetail__purpose__in=events)
        else:
            academic_centers = AcademicCenter.objects.filter(state__name__in=state)
            events = TrainingEvents.objects.filter(host_college__in = academic_centers)
            
            paymentdetails = allpaydetails.filter(paymentdetail__purpose__in=events)
        if request.GET.get('user_email'):
            email=request.GET.get('user_email')
            paymentdetails = paymentdetails.filter(paymentdetail__email=email).order_by('-created')
        if request.GET.get('userid'):
            userid=request.GET.get('userid')
            paymentdetails = paymentdetails.filter(paymentdetail__user_id=userid).order_by('-created')
            


    allpaydetails = paymentdetails

    if status and status in ('S','F','X'):
        
        allpaydetails = allpaydetails.filter(status=status)

    if request_type:
        if request_type == 'R':
            allpaydetails = allpaydetails.filter(requestType='R')
        elif request_type == 'I':
            allpaydetails = allpaydetails.filter(requestType='I')

    if request.GET.get('fdate'):
        if request.GET.get('tdate'):
            allpaydetails = allpaydetails.filter(Q(created__gt=request.GET.get('fdate')) & Q(created__lt= request.GET.get('tdate')))
        else:
            allpaydetails = allpaydetails.filter(created__gt=request.GET.get('fdate'))

    return allpaydetails

def get_all_events_detail(queryset, status, event_type=None):   
    if event_type:
        queryset = queryset.filter(event_type=event_type)

    pcount = 0
    mcount = 0
    fcount = 0
    event_ids = queryset.values_list('id', flat=True)
    if status in ['ongoing', 'completed', 'expired']:
        participants = Participant.objects.filter(event_id__in=event_ids,  reg_approval_status=1).values('gender').annotate(count=Count('id'))
    elif status == 'closed':
        participants = EventAttendance.objects.filter(event_id__in=event_ids).values('participant__gender').annotate(count=Count('id'))
        
    for item in participants:
        key = 'participant__gender' if 'participant__gender' in item else 'gender'
        pcount += item['count']
        if item[key] in ['M','m','Male','male']:
            mcount += item['count']
        elif item[key] in ['F', 'f','Female','female']:
            fcount += item['count']
    return pcount, mcount, fcount


def get_ilw_certificate(event, cert_type):
    if event.event_type == "INTERN":
        return os.path.join(settings.MEDIA_ROOT, "internship-certificate.pdf")
    if event.event_start_date < EDUPYRAMIDS_CERTIFICATE_DATE:
        template = "fdptr-certificate.pdf" if cert_type == "training" else "tr-certificate.pdf"
    else:
        template = "fdptr-certificate_edupyramids.pdf" if cert_type == "training" else "Blank-Certificate_edupyramids.pdf"
    return os.path.join(settings.MEDIA_ROOT, template)




def get_training_certi_text(event, user):
    training_start = event.event_start_date
    training_end = event.event_end_date
    formatted_start_date = training_start.strftime("%d-%m-%Y")
    formatted_end_date = training_end.strftime("%d-%m-%Y")
    organization = get_organization(training_start)
    
    participant = Participant.objects.filter(
        user=user, event=event, reg_approval_status=1
        ).order_by('-created').first()
    
    participantname = f"{user.first_name} {user.last_name}"
    text = ""
    if event.event_type == "INTERN": # For internship
        course_name_text = ""
        if event.is_course:
            label = "topic" if event.event_type == "HN" else "FOSS"
            course_name_text = f" the course <b>{event.course.name}</b> which includes the following {label}:"
        text = f"""
            This is to certify that <b>{participantname}</b> of <b>{participant.college.institution_name}</b>, has successfully 
            completed an Internship Programme conducted by EduPyramids, SINE, IIT Bombay from
            <b>{formatted_start_date} to {formatted_end_date}</b>. During this internship, the student completed
            self-paced training on{course_name_text} <b>{format_foss_list([foss.foss for foss in event.course.foss.all()])}</b>
            under the supervision of <b>{event.instructor_name}</b>.<br />

            This internship is officially approved and recognized by the receiving institution, 
            ensuring compliance with institutional norms and standards.
        """
    else: # For other events
        line1 = f"""
            This is to certify that <b>{participantname}</b> has participated in 
            <b>{event.get_event_type_display()}</b> from <b>{formatted_start_date}</b> to <b>{formatted_end_date}</b> 
        """
        line2 = f"""
            organized by <b>{event.host_college.institution_name}</b> 
            with course material provided by {organization}.
            <br /><br /> This training is offered by {organization}.
        """
        label = "topic" if event.event_type == "HN" else "FOSS"
        # Insert course name if it is a course
        if event.is_course:
            text = f"""
            {line1}
            on the course <b>{event.course.name}</b>, which includes the following {label}: 
            <b>{format_foss_list([foss.foss for foss in event.course.foss.all()])}</b>, 
            {line2}
            """
        else:
            foss = format_foss_list([x.foss for x in event.course.foss.all()])
            text = f"""{line1}
            on <b>{foss}</b> {line2}"""

    return text


def get_test_certi_text(event, user, teststatus):
    participantname = f"{user.first_name} {user.last_name}"
    training_start = event.event_start_date
    training_end = event.event_end_date
    formatted_start_date = training_start.strftime("%d-%m-%Y")
    formatted_end_date = training_end.strftime("%d-%m-%Y")
    organization = get_organization(training_start)
    participant = Participant.objects.filter(
        user=user, event=event, reg_approval_status=1
        ).order_by('-created').first()
    
    text = ""
    if event.event_type == "HN":
        text = f"This is to certify that <b>{participantname}</b> successfully passed the course: \
        <b>{event.course.name}</b> test, remotely conducted by {organization}, under an honour invigilation system.\
        <br /> Self learning through {organization} and passing an online test completes the training programme.<br />"
    elif event.event_type == "INTERN":

        text = f"""
            This is to certify that <b>{participantname}</b> of <b>{participant.college.institution_name}</b>, has successfully \
            completed an Internship Programme conducted by EduPyramids, SINE, IIT Bombay \
            from <b>{formatted_start_date} to {formatted_end_date}</b>. During this internship, the student completed \
            self-paced training on <b>{teststatus.fossid.foss}</b> under the supervision of <b>{event.instructor_name}</b>. <br/>
            This internship is officially approved and recognized by the receiving institution, \
            ensuring compliance with institutional norms and standards. <br/>
            <b>Grade</b> : {str('{:.2f}'.format(teststatus.mdlgrade))}%
            """
    else:
        credits = "<p><b>Credits:</b> "+str(teststatus.fossid.credits)+"&nbsp&nbsp&nbsp<b>Score:</b> "+str('{:.2f}'.format(teststatus.mdlgrade))+"%</p>"
        text = f"This is to certify that <b>{participantname}</b> successfully passed a \
        <b>{teststatus.fossid.foss}</b> test, remotely conducted by {organization}, under an honour invigilation system.\
        <br /> Self learning through {organization} and passing an online test completes the training programme.<br />{credits}"
    return text


def format_foss_list(foss_list):
    if not foss_list:
        return ''
    if len(foss_list) == 1:
        return foss_list[0]
    return ', '.join(foss_list[:-1]) + " and " + foss_list[-1]