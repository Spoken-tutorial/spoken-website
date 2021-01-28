from events.models import *
from training.models import *
from donate.models import *
from datetime import datetime,date
from certificate.views import _clean_certificate_certificate
from django.http import HttpResponse
import os
from string import Template
import subprocess

EVENT_TYPE_CHOICES =(
	('', '-----'), ('FDP', 'Paid FDP'), ('Workshop', 'Blended Mode Workshop'),('sdp', 'Student Training Programme'),('TPDP', 'Teachers Professional Development Program'
), ('SSDP', 'School Students  Development Program')
	)

EVENT_AMOUNT = {
     'FDP': '500', 'Workshop': '1000'
    }

REGISTRATION_TYPE_CHOICES =(
    ('', '-----'),  (1, 'Subscribed College'),(2, 'Manual Registration')
    )

def is_user_paid(user_obj, academic_id):
    try:
        idcase = AcademicKey.objects.get(academic_id=academic_id)
        user_paid = [True, user_obj.organiser.academic] if (idcase.expiry_date >= date.today()) else [False]
        return user_paid
    except:
        user_paid = [False]
    try:
        idcase = AcademicKey.objects.get(academic_id=academic_id)
        user_paid = [True, user_obj.invigilator.academic] if (idcase.expiry_date >= date.today()) else [False]
        return user_paid
    except:
        user_paid = [False]
    return user_paid

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
        idcase = AcademicKey.objects.get(academic_id=college_id)
        college_paid = True if (idcase.expiry_date >= date.today()) else False
        return college_paid
    except:
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

        content_tex = content.safe_substitute(
            name = pname,
            event_name = event.event_name,
            college = event.host_college.institution_name,
            host_college = event.host_college.institution_name,
            foss = event.foss.foss,
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
        allpaydetails = PaymentTransaction.objects.filter(paymentdetail__purpose='cdcontent', paymentdetail__state__in=state).order_by('-created')
        
    else:
        rp_events = TrainingEvents.objects.filter(state__name__in = state)
        allpaydetails = PaymentTransaction.objects.filter(paymentdetail__purpose__in=rp_events).exclude(paymentdetail__purpose='cdcontent').order_by('-created')

    
    
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

def get_all_events_detail(queryset, event_type=None):
    pcount = 0
    mcount = 0
    fcount = 0
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    for event in queryset:
        if event.training_status <= 1 :
            #completed state
            pcount += Participant.objects.filter(event=event,  reg_approval_status=1).count()
            mcount += Participant.objects.filter(event=event, gender__in=['M','m','Male','male'], reg_approval_status=1).count()
            fcount += Participant.objects.filter(event=event, gender__in=['F', 'f','Female','female'], reg_approval_status=1).count()
        elif event.training_status == 2:
            #closed
            pcount += EventAttendance.objects.filter(event=event).count()
            mcount += EventAttendance.objects.filter(event=event, participant__gender__in =['M','m','Male','male']).count()
            fcount += EventAttendance.objects.filter(event=event, participant__gender__in =['F', 'f','Female','female']).count()
    
    return pcount, mcount, fcount