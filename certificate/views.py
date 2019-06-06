# Standard Library
from builtins import hex
import hashlib
import os
import subprocess
from collections import OrderedDict
from string import Template

# Third Party Stuff
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext

# Spoken Tutorial Stuff
from certificate.forms import FeedBackForm
from certificate.models import *


def index(request):
    return render_to_response('index.html')


def verification(serial, _type):
    context = {}
    if _type == 'key':
        try:
            certificate = Certificate.objects.get(short_key=serial)
            name = certificate.name.title()
            paper = certificate.paper
            workshop = certificate.workshop
            serial_no = certificate.serial_no
            certificate.verified += 1
            certificate.save()
            purpose, year, type = _get_detail(serial_no)
            if type == 'P':
                if purpose == 'Drupal Workshop':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', '28 August'), ('Year', year)])
                elif purpose == 'FrontAccounting Workshop':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', '12 August'), ('Year', year)])
                elif purpose == 'Koha Workshop':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', '4 August'), ('Year', year)])
                elif purpose == 'Koha Coordinators Workshop':
                    if year == '2018':
                        detail = OrderedDict([('Name', name), ('Event', purpose), 
                            ('Days', '29 September'), ('Year', year)])
                    if year == '2019':
                        detail = OrderedDict([('Name', name), ('Event', purpose), 
                            ('Days', '8 February'), ('Year', year)])
                elif purpose == 'Koha Remote Workshop':
                    if year == '2018':
                        detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', '12 October'), ('Year', year)])
                    if year == '2019':
                        detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', '9 March'), ('Year', year)])
                elif purpose == 'Koha Remote Center':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', '12 October'), ('Year', year)])
                elif purpose == 'Moodle Coordinators Workshop':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', '1 March'), ('Year', year)])

                elif purpose == 'Induction Training Programme':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', ' 28 November 2017 to 20 December'), ('Year', year)])
                
                elif purpose == 'Moodle Main Workshop':
                    detail = OrderedDict([('Name', name), ('Event', purpose),
                                          ('Days', '15 March'), ('Year', year)])

                elif purpose == 'DrupalCamp Mumbai':
                    drupal_user = Drupal_camp.objects.get(email=certificate.email)
                    DAY = drupal_user.attendance
                    if DAY == 1:
                        day = 'Day 1'
                    elif DAY == 2:
                        day = 'Day 2'
                    elif DAY == 3:
                        day = 'Day 1 and Day 2'
                    detail = OrderedDict([('Name', name), ('Attended', day),
                                          ('Event', purpose), ('Year', year)])
                else:
                    detail = '{0} had attended {1} {2}'.format(name, purpose, year)
            elif type == 'A':
                detail = '{0} had presented paper on {3} in the {1} {2}'.format(name, purpose, year, paper)
            elif type == 'W':
                detail = '{0} had attended workshop on {3} in the {1} {2}'.format(name, purpose, year, workshop)
            context['serial_key'] = True

        except Certificate.DoesNotExist:
            detail = 'User does not exist'
            context["invalidserial"] = 1
        context['detail'] = detail
        return context
    if _type == 'number':
        try:
            certificate = Certificate.objects.get(serial_no=serial)
            name = certificate.name.title()
            paper = certificate.paper
            workshop = certificate.workshop
            certificate.verified += 1
            certificate.save()
            purpose, year, type = _get_detail(serial)
            if type == 'P':
                if purpose == 'DrupalCamp Mumbai':
                    drupal_user = Drupal_camp.objects.get(email=certificate.email)
                    DAY = drupal_user.attendance
                    if DAY == 1:
                        day = 'Day 1'
                    elif DAY == 2:
                        day = 'Day 2'
                    elif DAY == 3:
                        day = 'Day 1 and Day 2'
                    detail = {}
                    detail['Name'] = name
                    detail['Attended'] = day
                    detail['Event'] = purpose
                    detail['Year'] = year
                else:
                    detail = '{0} had attended {1} {2}'.format(name, purpose, year)
            elif type == 'A':
                detail = '{0} had presented paper on {3} in the {1} {2}'.format(name, purpose, year, paper)
            elif type == 'W':
                detail = '{0} had attended workshop on {3} in the {1} {2}'.format(name, purpose, year, workshop)
            context['detail'] = detail
        except Certificate.DoesNotExist:
            context["invalidserial"] = 1
        return context


def verify(request, serial_key=None):
    context = {}
    ci = RequestContext(request)
    if serial_key is not None:
        context = verification(serial_key, 'key')
        return render_to_response('verify.html', context, ci)
    if request.method == 'POST':
        serial_no = request.POST.get('serial_no').strip()
        context = verification(serial_no, 'number')
        if 'invalidserial' in context:
            context = verification(serial_no, 'key')
        return render_to_response('verify.html', context, ci)
    return render_to_response('verify.html', {}, ci)


def _get_detail(serial_no):
    purpose = None
    if serial_no[0:3] == 'DCM':
        purpose = 'DrupalCamp Mumbai'
    elif serial_no[0:3] == 'DRP':
        purpose = 'Drupal Workshop'
    elif serial_no[0:3] == 'FAW':
        purpose = 'FrontAccounting Workshop'
    elif serial_no[0:3] == 'KHW':
        purpose = 'Koha Workshop'
    elif serial_no[0:3] == 'KCW':
        purpose = 'Koha Coordinators Workshop'
    elif serial_no[0:3] == 'KMW':
        purpose = 'Koha Remote Workshop'
    elif serial_no[0:3] == 'KRC':
        purpose = 'Koha Remote Center'
    elif serial_no[0:3] == 'MCW':
        purpose = 'Moodle Coordinators Workshop'
    elif serial_no[0:3] == 'ITP':
        purpose = 'Induction Training Programme'
    elif serial_no[0:3] == 'MMW':
        purpose = 'Moodle Main Workshop'

    if serial_no[3:5] == '14':
        year = '2014'
    elif serial_no[3:5] == '15':
        year = '2015'
    elif serial_no[3:5] == '16':
        year = '2016'
    elif serial_no[3:5] == '17':
        year = '2017'
    elif serial_no[3:5] == '18':
        year = '2018'
    elif serial_no[3:5] == '19':
        year = '2019'
    return purpose, year, serial_no[-1]


def _clean_certificate_certificate(path, file_name):
    clean_process = subprocess.Popen('make -C {0} clean file_name={1}'.format(path, file_name),
                                     shell=True)
    clean_process.wait()


def _make_certificate_certificate(path, type, file_name):
    if type == 'P':
        command = 'participant_cert'
    elif type == 'A':
        command = 'paper_cert'
    elif type == 'W':
        command = 'workshop_cert'
    process = subprocess.Popen('timeout 15 make -C {0} {1} file_name={2}'.format(path, command, file_name),
                               stderr=subprocess.PIPE, shell=True)
    err = process.communicate()[1]
    return process.returncode, err


def drupal_feedback(request):
    context = {}
    ci = RequestContext(request)
    form = FeedBackForm()
    questions = Question.objects.filter(purpose='DMC')
    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                FeedBack.objects.get(email=data['email'].strip(), purpose='DMC')
                context['message'] = 'You have already submitted the feedback. You can download your certificate.'
                return render_to_response('drupal_download.html', context, ci)
            except FeedBack.DoesNotExist:
                feedback = FeedBack()
                feedback.name = data['name'].strip()
                feedback.email = data['email'].strip()
                feedback.purpose = 'DMC'
                feedback.submitted = True
                feedback.save()
                for question in questions:
                    answered = request.POST.get('{0}'.format(question.id), None)
                    answer = Answer()
                    answer.question = question
                    answer.answer = answered.strip()
                    answer.save()
                    feedback.answer.add(answer)
                    feedback.save()
                context['message'] = ''
                return render_to_response('drupal_download.html', context, ci)

    context['form'] = form
    context['questions'] = questions

    return render_to_response('drupal_feedback.html', context, ci)


def drupal_download(request):
    context = {}
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/drupal_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Drupal_camp.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('drupal_download.html',
                                          context, context_instance=ci)
            else:
                user = user[0]
        fname = user.firstname
        lname = user.lastname
        name = '{0} {1}'.format(fname, lname)
        purpose = user.purpose
        DAY = user.attendance
        if DAY == 1:
            day = 'Day 1'
        elif DAY == 2:
            day = 'Day 2'
        elif DAY == 3:
            day = 'Day 1 and Day 2'
        else:
            context['notregistered'] = 2
            return render_to_response('drupal_download.html', context,
                                      context_instance=ci)
        year = '15'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: https://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'day': day, 'serial_key': old_user.short_key}
            certificate = create_drupal_certificate(certificate_path, details,
                                                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: https://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'day': day, 'serial_key': short_key}
            certificate = create_drupal_certificate(certificate_path, details,
                                                    qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            return render_to_response('drupal_download.html', context, ci)
    context['message'] = ''
    return render_to_response('drupal_download.html', context, ci)


def create_drupal_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    try:
        download_file_name = None
        template = 'template_DCM2015Pcertificate'
        download_file_name = 'DCM2015Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              day=name['day'], serial_key=name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception:
        error = True
    return [None, error]


def drupal_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/drupal_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Drupal_WS.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('drupal_workshop_download.html',
                                          context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '16'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: https://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_drupal_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: https://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'serial_key': short_key}
            certificate = create_drupal_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render_to_response('drupal_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('drupal_workshop_download.html', context, ci)


def create_drupal_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_DRP2016Pcertificate'
        download_file_name = 'DRP2016Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              serial_key=name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]

def fa_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/fa_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = FA_WS.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('fa_workshop_download.html',
                                          context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        purpose = user.purpose
        year = '17'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: https://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key}
            certificate = create_fa_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: https://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'serial_key': short_key}
            certificate = create_fa_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render_to_response('fa_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('fa_workshop_download.html', context, ci)

def create_fa_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_FAW2017Pcertificate'
        download_file_name = 'FAW2017Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              serial_key=name['serial_key'], qr_code=qrcode)
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]

def itp_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/itp_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = ITP_WS.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('itp_workshop_download.html',
                                          context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        college = user.college
        purpose = user.purpose
        year = '17'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'https://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'college':college}
            certificate = create_itp_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'https://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'serial_key': short_key, 'college': college}
            certificate = create_itp_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render_to_response('itp_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('itp_workshop_download.html', context, ci)

def create_itp_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_ITPW2017Pcertificate'
        download_file_name = 'ITPW2017Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              serial_key=name['serial_key'], qr_code=qrcode, college=name['college'])
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]

def koha_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/koha_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Koha_WS.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('koha_workshop_download.html',
                                          context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        college = user.college
        purpose = user.purpose
        year = '18'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: https://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'college':college}
            certificate = create_koha_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: https://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'serial_key': short_key, 'college': college}
            certificate = create_koha_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render_to_response('koha_workshop_download.html', context, ci)
    context['message'] = ''
    return render_to_response('koha_workshop_download.html', context, ci)

def create_koha_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_KHW2018Pcertificate'
        download_file_name = 'KHW2018Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              serial_key=name['serial_key'], qr_code=qrcode, college=name['college'])
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]



def koha_coordinators_workshop_download(request):
    context = {}
    err = ""
    email = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/koha_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        sep29email = request.POST.get('email').strip()
        feb8email = request.POST.get('email2').strip()

        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if feb8email:
            email = feb8email
            user = Koha_WS_8feb2019.objects.filter(email=email)
            year = '19'
            workshop = '8feb2019'
        elif sep29email:
            email = sep29email
            user = Koha_WS_29Sep2018.objects.filter(email=email)
            year = '18'
            workshop = '29sep2018'
        if not user:
            context["notregistered"] = 1
            return render_to_response('koha_workshop29sep_download.html',
                                      context, context_instance=ci)
        else:
            user = user[0]
        name = user.name
        college = user.college
        purpose = user.purpose
        # year = '19'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'college':college}
            certificate = create_koha_coordinators_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(short_key) 
            details = {'name': name, 'serial_key': short_key, 'college': college}
            certificate = create_koha_coordinators_workshop_certificate(certificate_path, 
                details, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render_to_response('koha_workshop29sep_download.html', context, ci)
    context['message'] = ''
    return render_to_response('koha_workshop29sep_download.html', context, ci)


def create_koha_coordinators_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        if workshop == '8feb2019':
            template = 'template_KCW822019Pcertificate'
            download_file_name = 'KCW822019Pcertificate.pdf'
        if workshop == '29sep2018':
            template = 'template_KCW2992018Pcertificate'
            download_file_name = 'KCW2992018Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              serial_key=name['serial_key'], qr_code=qrcode, college=name['college'])
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]


def koha_massive_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/koha_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Koha_WS_12oct2018.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('koha_workshop12oct_download.html',
                                          context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        college = user.college
        remote = user.remote
        purpose = user.purpose
        year = '18'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'college': college, 'remote': remote}
            certificate = create_koha_massive_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'serial_key': short_key, 'college': college, 'remote': remote}
            certificate = create_koha_massive_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render_to_response('koha_workshop12oct_download.html', context, ci)
    context['message'] = ''
    return render_to_response('koha_workshop12oct_download.html', context, ci)

def create_koha_massive_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_KMW12102018Pcertificate'
        download_file_name = 'KMW12102018Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
            serial_key=name['serial_key'], qr_code=qrcode, college=name['college'], remote=name['remote'])
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]


def koha_main_workshop9march_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/koha_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Koha_WS_9march2019.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('koha_workshop9march_download.html',
                                          context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        college = user.college
        remote = user.remote
        purpose = user.purpose
        year = '19'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'college': college, 'remote': remote}
            certificate = create_koha_main_workshop9march_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'serial_key': short_key, 'college': college, 'remote': remote}
            certificate = create_koha_main_workshop9march_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render_to_response('koha_workshop9march_download.html', context, ci)
    context['message'] = ''
    return render_to_response('koha_workshop9march_download.html', context, ci)

def create_koha_main_workshop9march_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_KMW932019Pcertificate'
        download_file_name = 'KMW932019Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
            serial_key=name['serial_key'], qr_code=qrcode, college=name['college'], remote=name['remote'])
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]



def koha_rc_certificate_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/koha_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Koha_RC_12oct2018.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render_to_response('koha_12oct_rc_download.html',
                                          context, context_instance=ci)
            else:
                user = user[0]
        name = user.name
        rcid = user.rcid
        remote = user.remote
        purpose = user.purpose
        year = '18'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no)).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'rcid': rcid, 'remote': remote}
            certificate = create_koha_12oct_rc_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'serial_key': short_key, 'rcid': rcid, 'remote': remote}
            certificate = create_koha_12oct_rc_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render_to_response('koha_12oct_rc_download.html', context, ci)
    context['message'] = ''
    return render_to_response('koha_12oct_rc_download.html', context, ci)

def create_koha_12oct_rc_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_KMW12102018RCcertificate'
        download_file_name = 'KMW12102018RCcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
            serial_key=name['serial_key'], qr_code=qrcode, rcid=name['rcid'], remote=name['remote'])
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]


def moodle_coordinators_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/moodle_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Moodle_WS_1march2019.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render(request,'moodle_workshop1march_download.html',
                                          context)
            else:
                user = user[0]
        name = user.name
        college = user.college
        purpose = user.purpose
        year = '19'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no.encode('utf-8'))).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'college': college}
            certificate = create_moodle_coordinators_workshop_certificate(certificate_path, details, 
                qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(short_key) 
            details = {'name': name, 'serial_key': short_key, 'college': college}
            certificate = create_moodle_coordinators_workshop_certificate(certificate_path, 
                details, qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render(request,'moodle_workshop1march_download.html', context)
    context['message'] = ''
    return render(request,'moodle_workshop1march_download.html', context)


def create_moodle_coordinators_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_MCW132019Pcertificate'
        download_file_name = 'MCW132019Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
                                              serial_key=name['serial_key'], qr_code=qrcode, college=name['college'])
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]


def moodle_massive_workshop_download(request):
    context = {}
    err = ""
    ci = RequestContext(request)
    cur_path = os.path.dirname(os.path.realpath(__file__))
    certificate_path = '{0}/moodle_workshop_template/'.format(cur_path)

    if request.method == 'POST':
        email = request.POST.get('email').strip()
        type = request.POST.get('type', 'P')
        paper = None
        workshop = None
        if type == 'P':
            user = Moodle_WS_15mar2019.objects.filter(email=email)
            if not user:
                context["notregistered"] = 1
                return render(request,'moodle_workshop15mar_download.html',
                                          context)
            else:
                user = user[0]
        name = user.name
        college = user.college
        remote = user.remote
        purpose = user.purpose
        year = '19'
        id = int(user.id)
        hexa = hex(id).replace('0x', '').zfill(6).upper()
        serial_no = '{0}{1}{2}{3}'.format(purpose, year, hexa, type)
        serial_key = (hashlib.sha1(serial_no.encode('utf-8'))).hexdigest()
        file_name = '{0}{1}'.format(email, id)
        file_name = file_name.replace('.', '')
        try:
            old_user = Certificate.objects.get(email=email, serial_no=serial_no)
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(old_user.short_key)
            details = {'name': name, 'serial_key': old_user.short_key, 'college': college, 'remote': remote}
            certificate = create_moodle_massive_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                old_user.counter = old_user.counter + 1
                old_user.save()
                return certificate[0]
        except Certificate.DoesNotExist:
            uniqueness = False
            num = 5
            while not uniqueness:
                present = Certificate.objects.filter(short_key__startswith=serial_key[0:num])
                if not present:
                    short_key = serial_key[0:num]
                    uniqueness = True
                else:
                    num += 1
            qrcode = 'Verify at: http://spoken-tutorial.org/certificate/verify/{0} '.format(short_key)
            details = {'name': name, 'serial_key': short_key, 'college': college, 'remote': remote}
            certificate = create_moodle_massive_workshop_certificate(certificate_path, details,
                                                             qrcode, type, paper, workshop, file_name)
            if not certificate[1]:
                certi_obj = Certificate(name=name, email=email,
                                        serial_no=serial_no, counter=1, workshop=workshop,
                                        paper=paper, serial_key=serial_key, short_key=short_key)
                certi_obj.save()
                return certificate[0]

        if certificate[1]:
            _clean_certificate_certificate(certificate_path, file_name)
            context['error'] = True
            context['err'] = err
            return render(request,'moodle_workshop15mar_download.html', context)
    context['message'] = ''
    return render(request,'moodle_workshop15mar_download.html', context)

def create_moodle_massive_workshop_certificate(certificate_path, name, qrcode, type, paper, workshop, file_name):
    error = False
    err = None
    try:
        download_file_name = None
        template = 'template_MMW15032019Pcertificate'
        download_file_name = 'MMW15032019Pcertificate.pdf'

        template_file = open('{0}{1}'.format
                             (certificate_path, template), 'r')
        content = Template(template_file.read())
        template_file.close()

        content_tex = content.safe_substitute(name=name['name'].title(),
            serial_key=name['serial_key'], qr_code=qrcode, college=name['college'], remote=name['remote'])
        create_tex = open('{0}{1}.tex'.format
                          (certificate_path, file_name), 'w')
        create_tex.write(content_tex)
        create_tex.close()
        return_value, err = _make_certificate_certificate(certificate_path,
                                                          type, file_name)
        if return_value == 0:
            pdf = open('{0}{1}.pdf'.format(certificate_path, file_name), 'r')
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; \
                    filename=%s' % (download_file_name)
            response.write(pdf.read())
            _clean_certificate_certificate(certificate_path, file_name)
            return [response, False]
        else:
            error = True
    except Exception as e:
        error = True
        err = e
    return [err, error]
