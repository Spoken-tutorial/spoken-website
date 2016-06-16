# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Standard Library
import csv
from datetime import datetime, timedelta
from StringIO import StringIO

# Third Party Stuff
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.middleware import csrf
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

# Spoken Tutorial Stuff
from base.views import JSONResponseMixin
from cms.sortable import *
from creation.models import FossAvailableForWorkshop
from mdldjango.get_or_create_participant import get_or_create_participant

from .decorators import group_required
from .filters import TrainingRequestFilter
from .forms import (
    CourseMapForm,
    LatexWorkshopFileUploadForm,
    OrganiserFeedbackForm,
    SingleTrainingEditForm,
    SingleTrainingForm,
    TrainingRequestEditForm,
    TrainingRequestForm,
    UserForm
)
from .models import *
from .views import is_administrator, is_organiser, is_resource_person


class TrainingPlannerListView(ListView):
    """Display the taining planner details of that organiser on main page of STP.
    """
    queryset = None
    paginate_by = 20
    user = None
    template_name = None

    @method_decorator(group_required("Organiser"))
    # following function is only applicable to organiser login
    def dispatch(self, *args, **kwargs):
        self.user = self.request.user
        self.get_current_planner()
        self.queryset = TrainingPlanner.objects.filter(
            organiser_id=self.request.user.organiser.id,
            academic_id=self.request.user.organiser.academic.id,
        ).order_by('-year')
        return super(TrainingPlannerListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TrainingPlannerListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['current_planner'] = self.get_current_planner()
        context['next_planner'] = self.get_next_planner(context['current_planner'])
        return context

    # def get(self, request):
    #  return render(request, self.template_name)

    def post(self, request):
        return HttpResponse('Post')

    def is_even_sem(self, month):
        # 0 => odd sem, 1 => even sem
        if month > 6 and month < 13:
            return 0
        return 1

    def get_year(self, sem, year):
        if sem:
            return year - 1
        return year

    def get_semester(self, sem):
        return Semester.objects.get(even=sem)

    def get_current_planner(self):
        now = datetime.now()
        sem = self.is_even_sem(now.month)
        year = self.get_year(sem, now.year)
        try:
            return TrainingPlanner.objects.get(year=year, semester__even=sem,
                                               academic=self.user.organiser.academic, organiser=self.user.organiser)
        except ObjectDoesNotExist:
            return TrainingPlanner.objects.create(year=year,
                                                  semester=self.get_semester(sem),
                                                  academic=self.user.organiser.academic,
                                                  organiser=self.user.organiser)
        except Exception as e:
            print(e)
        return False

    def get_next_planner(self, current_planner):
        year = int(current_planner.year)
        even = True
        if current_planner.semester.even:
            year = year + 1
            even = False
        sem = self.get_semester(even)
        try:
            next_planner = TrainingPlanner.objects.get(year=year, semester=sem,
                                                       academic=self.user.organiser.academic,
                                                       organiser=self.user.organiser)
            return next_planner
        except ObjectDoesNotExist:
            return TrainingPlanner.objects.create(year=year,
                                                  semester=sem, academic=self.user.organiser.academic,
                                                  organiser=self.user.organiser)
        except Exception as e:
            print(e)
        return False


class StudentBatchCreateView(CreateView):
    form_class = None
    template_name = None
    user = None
    batch = None
    organiser = None

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        if 'bid' in kwargs:
            sb = StudentBatch.objects.filter(pk=kwargs['bid'])
            if sb.exists():
                self.batch = sb.first()
        return super(StudentBatchCreateView, self).dispatch(*args, **kwargs)

    # def get_form_kwargs(self):
    #  kwargs = super(StudentBatchCreateView, self).get_form_kwargs()
    #  kwargs.update({'user' : self.request.user})
    #  return kwargs

    def get_context_data(self, **kwargs):
        context = super(StudentBatchCreateView, self).get_context_data(**kwargs)
        if self.batch:
            existing_student = Student.objects.filter(
                id__in=StudentMaster.objects.filter(batch_id=self.batch.id, moved=False).values_list('student_id')
            )
            context['batch'] = self.batch
            context['existing_student'] = existing_student
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        self.user = request.user
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, **kwargs):
        form_data = form.save(commit=False)
        form_data.academic = self.user.organiser.academic
        self.organiser = self.user.organiser
        form_data.organiser = self.user.organiser
        try:
            if 'bid' in self.kwargs:
                form_data = StudentBatch.objects.get(pk=self.kwargs['bid'])
            else:
                form_data = StudentBatch.objects.get(year=form_data.year,
                                                     academic=form_data.academic,
                                                     department=form_data.department)
        except ObjectDoesNotExist:
            form_data.save()
        except Exception as e:
            print(e)
            return HttpResponseRedirect("/software-training/student-batch/")
        skipped, error, warning, write_flag = self.csv_email_validate(self.request.FILES['csv_file'], form_data.id)
        context = {'error': error, 'warning': warning, 'batch': form_data}

        if error or warning:
            return render(request, self.template_name, context)
        #    messages.success(self.request, "Student Batch added successfully.")
        return HttpResponseRedirect('/software-training/student-batch/%s/new/' % (str(form_data.id)))

#  def get(self, request, *args, **kwargs):
#    self.user = request.user
#    form_class = self.get_form_class()
#    form = self.get_form(form_class)
#    context = {}
#    context['form'] = form
#    return self.render_to_response(context)

    def email_validator(self, email):
        if email and email.strip():
            email = email.strip().lower()
            try:
                validate_email(email)
                return True
            except:
                pass
        return False

    def get_student(self, email):
        if email and email.strip():
            email = email.strip().lower()
            try:
                student = Student.objects.get(user__email=email)
                return student
            except ObjectDoesNotExist:
                pass
        return False

    def create_student(self, fname, lname, email, gender):
        # check params for empty/None
        if not fname or not lname or not email or not gender:
            return False
        user = None
        fname = fname.strip().upper()
        lname = lname.strip().upper()
        email = email.strip().lower()
        gender = gender.strip().lower()
        # check stripped params for non-empty
        if fname and lname and email and gender:
            if gender == 'male' or gender == 'm':
                gender = 'Male'
            else:
                gender = 'Female'
            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                user = User.objects.create_user(email, email, fname)
                user.is_active = False
            if user:
                user.first_name = fname
                user.last_name = lname
                user.save()
                try:
                    student_group = Group.objects.get(name='Student')
                    user.groups.add(student_group)
                except:
                    pass
                student = Student.objects.create(user=user, gender=gender)
                get_or_create_participant(self.organiser, fname, lname, gender, email, 0)
                return student
        return False

    def csv_email_validate(self, file_path, batch_id):
        skipped = []
        error = []
        warning = []
        write_flag = False
        try:
            csvdata = csv.reader(file_path, delimiter=',', quotechar='|')
            for row in csvdata:
                if len(row) < 4:
                    skipped.append(row)
                    continue
                if not self.email_validator(row[2]):
                    error.append(row)
                    continue
                student = self.get_student(row[2])
                if not student:
                    student = self.create_student(row[0], row[1], row[2], row[3])
                if student:
                    try:
                        smrec = StudentMaster.objects.get(student=student, moved=False)
                        if int(batch_id) == int(smrec.batch_id):
                            row.append(1)
                        else:
                            row.append(0)
                        warning.append(row)
                        continue
                    except ObjectDoesNotExist:
                        StudentMaster.objects.create(student=student, batch_id=batch_id)
                        write_flag = True
            StudentBatch.objects.get(pk=batch_id).update_student_count()
        except Exception as e:
            print(e)
            messages.warning(self.request, "The file you uploaded is not a valid CSV file, please add a valid CSV file")
        return skipped, error, warning, write_flag


class StudentBatchUpdateView(UpdateView):
    model = StudentBatch
    success_url = "/software-training/student-batch/"

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
            # trainingrequest_set.all()
        if 'pk' in kwargs:
            try:
                sb = StudentBatch.objects.get(pk=kwargs['pk'])
                if sb.trainingrequest_set.exists():
                    # messages.warning(self.request, 'This Student Batch has Training. You can not edit this batch.')
                    return HttpResponseRedirect('/software-training/student-batch/edit/' + str(kwargs['pk']))
            except:
                pass
        return super(StudentBatchUpdateView, self).dispatch(*args, **kwargs)


class StudentBatchYearUpdateView(UpdateView):
    model = StudentBatch
    success_url = "/software-training/student-batch/"


class StudentBatchListView(ListView):
    queryset = StudentBatch.objects.none()
    paginate_by = 20
    template_name = ""
    header = None
    raw_get_data = None

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        self.queryset = StudentBatch.objects.filter(academic_id=self.request.user.organiser.academic_id)
        self.header = {
            1: SortableHeader('#', False),
            2: SortableHeader('academic', True, 'Institution'),
            3: SortableHeader('department', True, 'Department'),
            4: SortableHeader('year', True, 'Year'),
            5: SortableHeader('stcount', True, 'Student Count'),
            6: SortableHeader('', False, ''),
        }
        self.raw_get_data = self.request.GET.get('o', None)
        self.queryset = get_sorted_list(self.request, self.queryset, self.header, self.raw_get_data)
        return super(StudentBatchListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StudentBatchListView, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['ordering'] = get_field_index(self.raw_get_data)
        return context


class StudentListView(ListView):
    queryset = Student.objects.none()
    paginate_by = 30
    template_name = None
    batch = None
    header = None
    raw_get_data = None

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        self.batch = StudentBatch.objects.filter(pk=kwargs['bid'])
        if not self.batch.exists():
            return HttpResponseRedirect('/student-batch')
        self.batch = self.batch.first()
        self.header = {
            1: SortableHeader('#', False),
            2: SortableHeader('Edit', False),
            3: SortableHeader('', False, 'Department'),
            4: SortableHeader('', False, 'Year'),
            5: SortableHeader('user__first_name', True, 'First Name'),
            6: SortableHeader('user__last_name', True, 'Last Name'),
            7: SortableHeader('user__email', True, 'Email'),
            8: SortableHeader('gender', True, 'Gender'),
            9: SortableHeader('', False, 'Status'),
            10: SortableHeader('', False, ''),
        }
        self.queryset = Student.objects.filter(
            id__in=StudentMaster.objects.filter(
                batch_id=self.batch.id,
                moved=False
            ).values_list(
                'student'
            )
        )
        self.raw_get_data = self.request.GET.get('o', None)
        self.queryset = get_sorted_list(self.request, self.queryset, self.header, self.raw_get_data)
        return super(StudentListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StudentListView, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['ordering'] = get_field_index(self.raw_get_data)
        context['batch'] = self.batch
        return context


class TrainingRequestCreateView(CreateView):
    form_class = TrainingRequestForm
    template_name = None
    user = None
    tpid = None

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        if not StudentBatch.objects.filter(academic=self.request.user.organiser.academic).exists():
            messages.warning(self.request, 'Please upload the master batch.')
            return HttpResponseRedirect("/software-training/training-planner")

        if 'tpid' in self.kwargs:
            self.tpid = self.kwargs['tpid']
            training_planner = TrainingPlanner.objects.filter(pk=self.tpid, organiser_id=self.request.user.organiser.id)
            if not training_planner.exists():
                # message say Not found
                messages.warning(self.request, 'Invalid Training Planner ID passed')
                return HttpResponseRedirect("/software-training/training-planner")
            else:
                training_planner = training_planner.first()
                if not training_planner.is_current_planner() and not training_planner.is_next_planner():
                    messages.warning(self.request, 'Selected Training Planner is already expired')
                    return HttpResponseRedirect("/software-training/training-planner")
        return super(TrainingRequestCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TrainingRequestCreateView, self).get_context_data(**kwargs)
        context['training_planner_id'] = self.tpid
        context['tp'] = TrainingPlanner.objects.filter(pk=self.tpid, organiser_id=self.request.user.organiser.id)[0]
        return context

    def get_form_kwargs(self):
        kwargs = super(TrainingRequestCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        username = self.request.user
        if username.organiser.academic.institution_type.id == 5 or \
           username.organiser.academic.institution_type.id == 13 or \
           username.organiser.academic.institution_type.id == 15:
            kwargs.update({'course_type': (
                ('', '---------'),
                (0, 'Software Course outside lab hours'),
                (1, 'Software Course mapped in lab hours'),
                (2, 'Software Course unmapped in lab hours'),
                (3, 'EduEasy Software'))
            })
        else:
            kwargs.update({'course_type': (
                ('', '---------'),
                (0, 'Software Course outside lab hours'),
                (1, 'Software Course mapped in lab hours'),
                (2, ' Software Course unmapped in lab hours'))
            })

        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = None
        self.user = request.user
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, **kwargs):
        # Check if all student participate in selected foss
        try:
            form_data = form.save(commit=False)
            sb = StudentBatch.objects.get(pk=form_data.batch.id)
            if sb.student_count():
                if sb.is_foss_batch_acceptable(form_data.course.id):
                    form_data.training_planner_id = self.kwargs['tpid']
                    # form_data.participants = StudentMaster.objects.filter(batch_id = form_data.batch_id).count()
                    form_data.save()
                else:
                    messages.error(self.request, 'This student batch already taken the selected course.')
                    return self.form_invalid(form)
            else:
                sb.update_student_count()
                messages.error(self.request, 'There is no student present in this batch.')
                return self.form_invalid(form)
        except:
            messages.error(self.request, 'Something went wrong, Contact site administrator.')
            return self.form_invalid(form)
        messages.success(self.request, ('STP has been added successfully. Now continue with step 3 '
                                        '"Select Participants" on STPS page. Select the participants from the Master '
                                        'Batch Student List for any one course that you are starting with. This is '
                                        'necessary for receiving certificates.'))
        return HttpResponseRedirect('/software-training/{0}/training-request/'.format(self.tpid))
        # return render_to_response(self.template_name, context, context_instance=RequestContext(self.request))


class TrainingRequestEditView(CreateView):
    form_class = TrainingRequestEditForm
    template_name = None
    user = None
    training = None

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        if 'trid' in self.kwargs:
            self.training = TrainingRequest.objects.get(pk=self.kwargs['trid'])
        if not self.training.can_edit():
            messages.error(self.request, "Training has attendance, edit is not permitted for training.")
            return HttpResponseRedirect('/software-training/training-planner/')
        return super(TrainingRequestEditView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(TrainingRequestEditView, self).get_form_kwargs()
        kwargs.update({'training': self.training})
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(TrainingRequestEditView, self).get_context_data(**kwargs)
        context['training'] = self.training
        return context

    def form_valid(self, form, **kwargs):
        # Check if all student participate in selected foss
        try:
            if self.training.batch.is_foss_batch_acceptable(form.cleaned_data['course']):
                self.training.sem_start_date = form.cleaned_data['sem_start_date']
                self.training.course_id = form.cleaned_data['course']
                self.training.save()
            else:
                messages.error(self.request, 'This student batch already taken the selected course.')
                return self.form_invalid(form)
        except Exception as e:
            print(e)
            messages.error(self.request, 'Something went wrong, Contact site administrator.')
            return self.form_invalid(form)
        return HttpResponseRedirect('/software-training/training-planner/')

    def post(self, request, *args, **kwargs):
        self.object = None
        self.user = request.user
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class TrainingAttendanceListView(ListView):
    queryset = StudentMaster.objects.none()
    paginate_by = 500
    template_name = ""
    training_request = None

    def dispatch(self, *args, **kwargs):
        self.training_request = TrainingRequest.objects.get(pk=kwargs['tid'])
        if self.training_request.status == 1:
            self.queryset = self.training_request.trainingattend_set.all()
        else:
            self.queryset = StudentMaster.objects.filter(batch_id=self.training_request.batch_id, moved=False)
        return super(TrainingAttendanceListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TrainingAttendanceListView, self).get_context_data(**kwargs)
        context['training'] = self.training_request
        context['department'] = self.training_request.department
        languages = Language.objects.filter(
            id__in=FossAvailableForWorkshop.objects.filter(
                foss_id=self.training_request.course.foss_id
            ).values_list('language_id')
        )
        # language
        # for lang in languages:
        context['languages'] = languages
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        self.user = request.user
        training_id = kwargs['tid']
        if request.POST and 'user' in request.POST:
            if csrf.get_token(request) == request.POST['csrfmiddlewaretoken']:
                marked_student = request.POST.getlist('user', None)
                # delete un marked record if exits
                TrainingAttend.objects.filter(training_id=training_id).exclude(student_id__in=marked_student).delete()
                # insert new record if not exits
                for record in marked_student:
                    language_id = request.POST.get(record)
                    training_attend = TrainingAttend.objects.filter(training_id=training_id, student_id=record)
                    if not training_attend.exists():
                        TrainingAttend.objects.create(training_id=training_id,
                                                      student_id=record, language_id=language_id)
                    else:
                        training_attend = training_attend.first()
                        training_attend.language_id = language_id
                        training_attend.save()
            # print marked_student
        else:
            TrainingAttend.objects.filter(training_id=training_id).delete()
        self.training_request.update_participants_count()
        return HttpResponseRedirect('/software-training/training-planner')


class TrainingCertificateListView(ListView):
    queryset = StudentMaster.objects.none()
    paginate_by = 500
    template_name = ""
    training_request = None

    def dispatch(self, *args, **kwargs):
        self.training_request = TrainingRequest.objects.get(pk=kwargs['tid'])
        if self.training_request.status:
            self.queryset = self.training_request.trainingattend_set.all()
        else:
            self.queryset = StudentMaster.objects.filter(batch_id=self.training_request.batch_id, moved=False)
        return super(TrainingCertificateListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TrainingCertificateListView, self).get_context_data(**kwargs)
        context['training'] = self.training_request
        languages = Language.objects.filter(
            id__in=FossAvailableForWorkshop.objects.filter(
                foss_id=self.training_request.course.foss_id
            ).values_list('language_id')
        )
        # language
        # for lang in languages:
        context['languages'] = languages
        return context


class StudentDeleteView(DeleteView):
    model = Student

    def dispatch(self, *args, **kwargs):
        self.success_url = "/software-training/student-batch/" + str(kwargs['bid']) + "/view"
        student = super(StudentDeleteView, self).get_object()
        if student.is_student_has_attendance():
            messages.error(self.request, ("You do not have permission to delete {0} "
                                          "because you have marked the attendance").format(student.student_fullname()))
            return HttpResponseRedirect(self.success_url)
        try:
            sm = StudentMaster.objects.get(student=student, moved=False)
            if not sm.batch.organiser.academic_id == self.request.user.organiser.academic_id:
                messages.error(self.request, "You do not have permission to delete " + student.student_fullname())
                return HttpResponseRedirect(self.success_url)
        except:
            pass
        return super(StudentDeleteView, self).dispatch(*args, **kwargs)


class TrainingCertificate():

    def custom_strftime(self, format, t):
        return t.strftime(format).replace('{S}', str(t.day) + self.suffix(t.day))

    def suffix(self, d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def training_certificate(self, ta):
        response = HttpResponse(content_type='application/pdf')
        filename = (ta.student.user.first_name + '-' + ta.training.course.foss.foss +
                    "-Participant-Certificate").replace(" ", "-")

        response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        imgTemp = StringIO()
        imgDoc = canvas.Canvas(imgTemp)

        # Title
        imgDoc.setFont('Helvetica', 40, leading=None)
        imgDoc.drawCentredString(415, 480, "Certificate of Learning")

        # date
        imgDoc.setFont('Helvetica', 18, leading=None)
        imgDoc.drawCentredString(211, 115, self.custom_strftime('%B {S} %Y', ta.training.sem_start_date))

        # password
        certificate_pass = ''
        imgDoc.setFillColorRGB(211, 211, 211)
        imgDoc.setFont('Helvetica', 10, leading=None)
        imgDoc.drawString(10, 6, certificate_pass)

        # Draw image on Canvas and save PDF in buffer
        imgPath = settings.MEDIA_ROOT + "sign.jpg"
        imgDoc.drawImage(imgPath, 600, 100, 150, 76)

        # paragraphe
        text = ("This is to certify that <b>" + ta.student.user.first_name + " " + ta.student.user.last_name + "</b> "
                "participated in the <b>" + ta.training.course.foss.foss + "</b> training organized at <b>" +
                ta.training.training_planner.academic.institution_name + "</b> by <b>" +
                ta.training.training_planner.organiser.user.first_name + " " +
                ta.training.training_planner.organiser.user.last_name + "</b> on <b>" +
                self.custom_strftime('%B {S} %Y', ta.training.sem_start_date) + "</b> with course material provided "
                "by the Spoken Tutorial Project, IIT Bombay.<br /><br />A comprehensive set of topics pertaining to "
                "<b>" + ta.training.course.foss.foss + "</b> were covered in the training. This training is offered "
                "by the Spoken Tutorial Project, IIT Bombay, funded by National Mission on Education through ICT, "
                "MHRD, Govt. of India.")

        centered = ParagraphStyle(name='centered',
                                  fontSize=16,
                                  leading=30,
                                  alignment=0,
                                  spaceAfter=20
                                  )

        p = Paragraph(text, centered)
        p.wrap(650, 200)
        p.drawOn(imgDoc, 4.2 * cm, 7 * cm)

        imgDoc.save()

        # Use PyPDF to merge the image-PDF into the template
        page = PdfFileReader(file(settings.MEDIA_ROOT + "Blank-Certificate.pdf", "rb")).getPage(0)
        overlay = PdfFileReader(StringIO(imgTemp.getvalue())).getPage(0)
        page.mergePage(overlay)

        # Save the result
        output = PdfFileWriter()
        output.addPage(page)

        # stream to browser
        outputStream = response
        output.write(response)
        outputStream.close()

        return response


class SingleTrainingCertificate():

    def custom_strftime(self, format, t):
        return t.strftime(format).replace('{S}', str(t.day) + self.suffix(t.day))

    def suffix(self, d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def single_training_certificate(self, ta):
        response = HttpResponse(content_type='application/pdf')
        filename = (ta.firstname + '-' + ta.training.course.foss.foss + "-Participant-Certificate").replace(" ", "-")

        response['Content-Disposition'] = 'attachment; filename=' + filename + '.pdf'
        imgTemp = StringIO()
        imgDoc = canvas.Canvas(imgTemp)

        # Title
        imgDoc.setFont('Helvetica', 40, leading=None)
        imgDoc.drawCentredString(415, 480, "Certificate of Learning")

        # date
        imgDoc.setFont('Helvetica', 18, leading=None)
        imgDoc.drawCentredString(211, 115, self.custom_strftime('%B {S} %Y', ta.training.tdate))

        # password
        certificate_pass = ''
        imgDoc.setFillColorRGB(211, 211, 211)
        imgDoc.setFont('Helvetica', 10, leading=None)
        imgDoc.drawString(10, 6, certificate_pass)

        # Draw image on Canvas and save PDF in buffer
        imgPath = settings.MEDIA_ROOT + "sign.jpg"
        imgDoc.drawImage(imgPath, 600, 100, 150, 76)

        # paragraphe
        text = ("This is to certify that <b>{name}</b> participated in the <b>{foss}</b> "
                "training organized at <b>{institute}</b> by <b>{organiser_name}</b> on "
                "<b>{training_date}</b> with course material provided by the Spoken Tutorial "
                "Project, IIT Bombay.<br><br>"
                "A comprehensive set of topics pertaining to <b>{foss}</b> were covered in the "
                "workshop. This training is offered by the Spoken Tutorial Project, IIT Bombay, "
                "funded by National Mission on Education through ICT, MHRD, Govt. of India.").format(
                    name=ta.firstname + " " + ta.lastname,
                    foss=ta.training.course.foss.foss,
                    institute=ta.training.academic.institution_name,
                    organiser_name=ta.training.organiser.user.first_name + " " + ta.training.organiser.user.last_name,
                    training_date=self.custom_strftime('%B {S} %Y', ta.training.tdate))

        centered = ParagraphStyle(name='centered', fontSize=16, leading=30, alignment=0, spaceAfter=20)

        p = Paragraph(text, centered)
        p.wrap(650, 200)
        p.drawOn(imgDoc, 4.2 * cm, 7 * cm)

        imgDoc.save()

        # Use PyPDF to merge the image-PDF into the template
        page = PdfFileReader(file(settings.MEDIA_ROOT + "Blank-Certificate.pdf", "rb")).getPage(0)
        overlay = PdfFileReader(StringIO(imgTemp.getvalue())).getPage(0)
        page.mergePage(overlay)

        # Save the result
        output = PdfFileWriter()
        output.addPage(page)

        # stream to browser
        outputStream = response
        output.write(response)
        outputStream.close()

        return response


class OrganiserTrainingCertificateView(TrainingCertificate, View):
    template_name = ""

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        return super(OrganiserTrainingCertificateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        ta = None
        try:
            ta = TrainingAttend.objects.get(pk=kwargs['taid'])
        except ObjectDoesNotExist:
            messages.error(self.request, "Record not found")
            pass

        if ta and ta.training.training_planner.organiser == self.request.user.organiser:
            return self.training_certificate(ta)
        else:
            messages.error(self.request, "PermissionDenied!")
        return HttpResponseRedirect("/")


class OrganiserSingleTrainingCertificateView(SingleTrainingCertificate, View):
    template_name = ""

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        return super(OrganiserSingleTrainingCertificateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        ta = None
        try:
            ta = SingleTrainingAttendance.objects.get(pk=kwargs['taid'])
        except ObjectDoesNotExist:
            messages.error(self.request, "Record not found")
            pass

        if ta:
            return self.single_training_certificate(ta)
        else:
            messages.error(self.request, "PermissionDenied!")
        return HttpResponseRedirect("/")


class StudentTrainingCertificateView(TrainingCertificate, View):
    template_name = ""

    @method_decorator(group_required("Student"))
    def dispatch(self, *args, **kwargs):
        return super(StudentTrainingCertificateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        ta = None
        try:
            ta = TrainingAttend.objects.get(pk=kwargs['taid'])
        except ObjectDoesNotExist:
            messages.error(self.request, "Record not found")
            pass

        try:
            mdluserid = request.session.get('mdluserid', None)
            mdluser = MdlUser.objects.get(id=mdluserid)
            if ta and ta.student.user.email == mdluser.email:
                return self.training_certificate(ta)
        except Exception:
            messages.error(self.request, "PermissionDenied!")
        return HttpResponseRedirect("/")


class CourseMapCreateView(CreateView):
    form_class = CourseMapForm

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        return super(CourseMapCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CourseMapCreateView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form, **kwargs):
        # Check if all student participate in selected foss
        try:
            form_data = form.save(commit=False)
            if FossAvailableForTest.objects.filter(foss_id=form_data.foss).exists():
                form_data.test = 1
            form_data.save()
        except IntegrityError:
            messages.error(self.request, 'Course with this Foss and Category already exists.')
            return self.form_invalid(form)
        return HttpResponseRedirect('/software-training/course-map/')


class CourseMapListView(ListView):
    queryset = CourseMap.objects.none()
    paginate_by = 50
    header = None
    raw_get_data = None

    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
        self.header = {
            1: SortableHeader('#', False),
            2: SortableHeader('course', True, 'Course'),
            3: SortableHeader('test', True, 'Test'),
            4: SortableHeader('category', True, 'Category'),
            5: SortableHeader('', False, ''),
        }
        self.queryset = CourseMap.objects.exclude(category=0)
        self.raw_get_data = self.request.GET.get('o', None)
        get_sorted_list(self.request, self.queryset, self.header, self.raw_get_data)
        return super(CourseMapListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CourseMapListView, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['ordering'] = get_field_index(self.raw_get_data)
        return context


class CourseMapUpdateView(UpdateView):
    model = CourseMap
    form_class = CourseMapForm
    success_url = "/software-training/course-map-list/"


# Ajax
class SaveStudentView(JSONResponseMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SaveStudentView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        sb = StudentBatchCreateView()
        email = self.request.POST.get('email').strip().lower()
        message = ''
        code = 0  # 0 => None, 1 => Warning, 2 => Error
        if sb.email_validator(email):
            student = sb.get_student(email)
            batch = self.request.POST.get('batch')

            if not student:
                sdetails = self.request.POST.get('student_details').split(',')
                student = sb.create_student(sdetails[0], sdetails[1], email, sdetails[2])
            if student:
                try:
                    smrec = StudentMaster.objects.get(student=student)
                    message = "Student with this email already exists in some other batch."
                    code = 2
                    # check student in different batch
                    if int(batch) == int(smrec.batch_id):
                        code = 1
                        message = "Student with this email already exists in this batch."
                except ObjectDoesNotExist:
                    StudentMaster.objects.create(student=student, batch_id=batch)
                    StudentBatch.objects.get(pk=batch).update_student_count()
            else:
                code = 2
                message = "Something went wrong. Please contact site administrator."
        else:
            code = 4
            message = "Invalid email address"

        context = {
            'code': code,
            'message': message
        }
        return self.render_to_json_response(context)


class GetCourseOptionView(JSONResponseMixin, View):
    department_id = None

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GetCourseOptionView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):

        context = {}
        category = self.request.POST.get('course_type')
        department_id = self.request.POST.get('department')
        tp = TrainingPlanner.objects.get(pk=self.request.POST.get('training_planner'))

        if department_id == '24':
            if tp.is_school_course_full(category, self.request.POST.get('department'), self.request.POST.get('batch')):
                context['is_full'] = True
            else:
                courses = CourseMap.objects.filter(category=category)
                course_option = "<option value=''>---------</option>"
                for course in courses:
                    course_detail = '{0} ({1})'.format(course.foss.foss, course.course)
                    if course.course:
                        course_option += "<option value=" + str(course.id) + ">" + course_detail + "</option>"
                    else:
                        course_option += "<option value=" + str(course.id) + ">" + course.foss.foss + "</option>"
                context = {
                    'course_option': course_option,
                    'is_full': False
                }
        else:
            if tp.is_course_full(category, self.request.POST.get('department'), self.request.POST.get('batch')):
                context['is_full'] = True
            else:
                courses = CourseMap.objects.filter(category=category)
                course_option = "<option value=''>---------</option>"
                for course in courses:
                    course_detail = '{0} ({1})'.format(course.foss.foss, course.course)
                    if course.course:
                        course_option += "<option value=" + str(course.id) + ">" + course_detail + "</option>"
                    else:
                        course_option += "<option value=" + str(course.id) + ">" + course.foss.foss + "</option>"
                context = {
                    'course_option': course_option,
                    'is_full': False
                }
        return self.render_to_json_response(context)

        return render(request, 'course_select.html', context)


class GetBatchOptionView(JSONResponseMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GetBatchOptionView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        department_id = self.request.POST.get('department')
        context = {}

        batches = StudentBatch.objects.filter(
            academic_id=request.user.organiser.academic.id,
            stcount__gt=0,
            department_id=department_id
        )
        batch_option = "<option value=''>---------</option>"
        for batch in batches:
            batch_option += "<option value=" + str(batch.id) + ">" + str(batch) + "</option>"
        context = {
            'batch_option': batch_option,
        }
        return self.render_to_json_response(context)


class GetBatchStatusView(JSONResponseMixin, View):
    department_id = None

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(GetBatchStatusView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        department_id = self.request.POST.get('department')

        batch_id = self.request.POST.get('batch')
        tp = TrainingPlanner.objects.get(pk=self.request.POST.get('training_planner'))
        context = {}

        batch_status = True

        if department_id == '24':
            if tp.is_school_full(department_id, batch_id):
                batch_status = False
        else:
            if tp.is_full(department_id, batch_id):
                batch_status = False

        context = {
            'batch_status': batch_status,
        }
        return self.render_to_json_response(context)


class TrainingRequestListView(ListView):
    queryset = None
    paginate_by = 20
    user = None
    template_name = None
    header = None
    raw_get_data = None
    role = None
    status = None

    @method_decorator(group_required("Resource Person", "Administrator"))
    def dispatch(self, *args, **kwargs):
        if ('role' not in kwargs) or ('status' not in kwargs):
            raise PermissionDenied()
        self.role = kwargs['role']
        self.status = kwargs['status']
        status_list = {'pending': 0, 'completed': 1, 'markcomplete': 2}
        roles = ['rp', 'em']
        self.user = self.request.user
        if self.role in roles and self.status in status_list:
            if self.status == 'completed':
                self.queryset = TrainingRequest.objects.filter(
                    training_planner__academic_id__in=AcademicCenter.objects.filter(
                        state__in=State.objects.filter(
                            resourceperson__user_id=self.user,
                            resourceperson__status=1
                        )
                    ).values_list('id'),
                    status=1,
                    participants__gt=0
                ).order_by('-updated')
            elif self.status == 'pending':
                self.queryset = TrainingRequest.objects.filter(
                    training_planner__academic_id__in=AcademicCenter.objects.filter(
                        state__in=State.objects.filter(
                            resourceperson__user_id=self.user,
                            resourceperson__status=1
                        )
                    ).values_list('id'),
                    status=0
                ).order_by('-updated')
            elif self.status == 'markcomplete':
                if is_administrator(self.user):
                    self.queryset = TrainingRequest.objects.filter(status=2).order_by('-updated')
                else:
                    self.queryset = TrainingRequest.objects.filter(
                        training_planner__academic_id__in=AcademicCenter.objects.filter(
                            state__in=State.objects.filter(
                                resourceperson__user_id=self.user,
                                resourceperson__status=1
                            )
                        ).values_list('id'),
                        status=2
                    ).order_by('-updated')

            self.header = {
                1: SortableHeader('#', False),
                2: SortableHeader(
                    'training_planner__academic__state__name',
                    True,
                    'State'
                ),
                3: SortableHeader(
                    'training_planner__academic__academic_code',
                    True,
                    'Code'
                ),
                4: SortableHeader(
                    'training_planner__academic__institution_name',
                    True,
                    'Institution'
                ),
                5: SortableHeader('batch__department__name', True, 'Department / Batch'),
                6: SortableHeader('course__foss__foss', True, 'Course Name'),
                7: SortableHeader('course__category', True, 'Course Type'),
                8: SortableHeader(
                    'training_planner__organiser__user__first_name',
                    True,
                    'Organiser'
                ),
                9: SortableHeader(
                    'sem_start_date',
                    True,
                    'Sem Start Date / Training Date'
                ),
                10: SortableHeader('participants', True, 'Participants'),
                # 11: SortableHeader('Action', False)
            }
            self.raw_get_data = self.request.GET.get('o', None)
            self.queryset = get_sorted_list(
                self.request,
                self.queryset,
                self.header,
                self.raw_get_data
            )
            if self.status == 'completed':
                self.queryset = TrainingRequestFilter(
                    self.request.GET, queryset=self.queryset, user=self.user, rp_completed=True)
            elif self.status == 'pending':
                self.queryset = TrainingRequestFilter(
                    self.request.GET, queryset=self.queryset, user=self.user, rp_ongoing=True)
            elif self.status == 'markcomplete':
                self.queryset = TrainingRequestFilter(
                    self.request.GET, queryset=self.queryset, user=self.user, rp_markcomplete=True)
        else:
            raise PermissionDenied()
        return super(TrainingRequestListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TrainingRequestListView, self).get_context_data(**kwargs)
        context['form'] = self.queryset.form
        context['role'] = self.role
        context['status'] = self.status
        context['header'] = self.header
        context['ordering'] = get_field_index(self.raw_get_data)
        return context


# #############################  Single Training one day workshop #########

"""
'''
SingleTrainingNewListView will list all the new/pending training requests in the
single-training page pertaining to a specific user, i.e, Organiser or Resource Person.

'''
class SingleTrainingNewListView(ListView):
  queryset = None
  paginate_by = 10

  def get_context_data(self, **kwargs):
    context = super(SingleTrainingNewListView, self).get_context_data(**kwargs)
    temp = self.request.user.groups.all()
    grup = []
    for i in temp:
      grup.append(i.name)
    context['group'] = grup
    return context

  def dispatch(self, *args, **kwargs):
    user_groups_object = self.request.user.groups.all()
    user_group = []
    for i in user_groups_object:
      user_group.append(i.name)
    if 'Administrator' in user_group:
      self.queryset = SingleTraining.objects.filter(Q(status=0)).order_by('-tdate')
      return super(SingleTrainingNewListView, self).dispatch(*args, **kwargs)
    if 'Resource Person' in user_group and 'Organiser' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(Q(status=0),
            academic__state__id__in = state_list).order_by('-tdate')
      return super(SingleTrainingNewListView, self).dispatch(*args, **kwargs)
    elif 'Organiser' in user_group:
      rp_state = self.request.user.organiser.academic_id
      self.queryset = SingleTraining.objects.filter(Q(status=0), academic__id = rp_state).order_by('-tdate')
      return super(SingleTrainingNewListView, self).dispatch(*args, **kwargs)
    elif 'Resource Person' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(Q(status=0),
                academic__state__id__in = state_list).order_by('-tdate')
      return super(SingleTrainingNewListView, self).dispatch(*args, **kwargs)


'''
SingletrainingApprovedListView will list all the approved training requests in the single-training page.

'''
class SingletrainingApprovedListView(ListView):
  queryset = None
  paginate_by = 10

  def get_context_data(self, **kwargs):
    context = super(SingletrainingApprovedListView, self).get_context_data(**kwargs)
    temp = self.request.user.groups.all()
    grup = []
    for i in temp:
      grup.append(i.name)
    context['group'] = grup
    return context

  def dispatch(self, *args, **kwargs):
    user_groups_object = self.request.user.groups.all()
    user_group = []
    for i in user_groups_object:
      user_group.append(i.name)
    if 'Administrator' in user_group:
      self.queryset = SingleTraining.objects.filter(tdate__gt=datetime.today().date().isoformat(),
        status=2).order_by('-tdate')
      return super(SingletrainingApprovedListView, self).dispatch(*args, **kwargs)
    if 'Resource Person' in user_group and 'Organiser' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate__gt=datetime.today().date().isoformat(),status=2,
                               academic__state__id__in = state_list).order_by('-tdate')
      return super(SingletrainingApprovedListView, self).dispatch(*args, **kwargs)
    elif 'Organiser' in user_group:
      rp_state = self.request.user.organiser.academic_id
      self.queryset = SingleTraining.objects.filter(status=2,
        academic__id = rp_state,tdate__gt=datetime.today().date().isoformat()).order_by('-tdate')
      return super(SingletrainingApprovedListView, self).dispatch(*args, **kwargs)
    elif 'Resource Person' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate__gt=datetime.today().date().isoformat(),
                            status=2, academic__state__id__in = state_list).order_by('-tdate')
      return super(SingletrainingApprovedListView, self).dispatch(*args, **kwargs)

'''
 SingletrainingRejectedListView displays the workshop requests which have been rejected
'''
class SingletrainingRejectedListView(ListView):
  queryset = None
  paginate_by = 10

  def get_context_data(self, **kwargs):
    context = super(SingletrainingRejectedListView, self).get_context_data(**kwargs)
    temp = self.request.user.groups.all()
    grup = []
    for i in temp:
      grup.append(i.name)
    context['group'] = grup
    return context

  def dispatch(self, *args, **kwargs):
    user_groups_object = self.request.user.groups.all()
    user_group = []
    for i in user_groups_object:
      user_group.append(i.name)
    if 'Administrator' in user_group:
      self.queryset = SingleTraining.objects.filter(tdate__gt=datetime.today().date().isoformat(),
                                                    status=5).order_by('-tdate')
      return super(SingletrainingRejectedListView, self).dispatch(*args, **kwargs)
    if 'Resource Person' in user_group and 'Organiser' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate__gt=datetime.today().date().isoformat(),
                                                    status=5, academic__state__id__in = state_list).order_by('-tdate')
      return super(SingletrainingRejectedListView, self).dispatch(*args, **kwargs)
    elif 'Organiser' in user_group:
      rp_state = self.request.user.organiser.academic_id
      self.queryset = SingleTraining.objects.filter(status=5,
                    academic__id = rp_state,tdate__gt=datetime.today().date().isoformat()).order_by('-tdate')
      return super(SingletrainingRejectedListView, self).dispatch(*args, **kwargs)
    elif 'Resource Person' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate__gt=datetime.today().date().isoformat(),
                                                    status=5, academic__state__id__in = state_list).order_by('-tdate')
      return super(SingletrainingRejectedListView, self).dispatch(*args, **kwargs)

''' SingletrainingOngoingListView displays the workshops going on that particular day '''
class SingletrainingOngoingListView(ListView):
  queryset = None
  paginate_by = 10

  def get_context_data(self, **kwargs):
    context = super(SingletrainingOngoingListView, self).get_context_data(**kwargs)
    temp = self.request.user.groups.all()
    grup = []
    for i in temp:
      grup.append(i.name)
    context['group'] = grup
    return context

  def dispatch(self, *args, **kwargs):
    user_groups_object = self.request.user.groups.all()
    user_group = []
    for i in user_groups_object:
      user_group.append(i.name)
    if 'Administrator' in user_group:
      self.queryset = SingleTraining.objects.filter(tdate=datetime.today().date().isoformat(),
                                                    status=2).order_by('-tdate')
      return super(SingletrainingOngoingListView, self).dispatch(*args, **kwargs)
    if 'Resource Person' in user_group and 'Organiser' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate=datetime.today().date().isoformat(),
                                                    status=2, academic__state__id__in = state_list).order_by('-tdate')
      return super(SingletrainingOngoingListView, self).dispatch(*args, **kwargs)
    elif 'Organiser' in user_group:
      rp_state = self.request.user.organiser.academic_id
      self.queryset = SingleTraining.objects.filter(tdate=datetime.today().date().isoformat(),
                                                    status=2, academic__id = rp_state).order_by('-tdate')
      return super(SingletrainingOngoingListView, self).dispatch(*args, **kwargs)
    elif 'Resource Person' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate=datetime.today().date().isoformat(),
                                                    status=2, academic__state__id__in = state_list).order_by('-tdate')
      return super(SingletrainingOngoingListView, self).dispatch(*args, **kwargs)

'''
SingleTrainingCompletedListView will list all the completed training requests in the single-training page.

'''
class SingletrainingCompletedListView(ListView):
  queryset = None
  paginate_by = 10


  def dispatch(self, *args, **kwargs):
    user_groups_object = self.request.user.groups.all()
    user_group = []
    for i in user_groups_object:
      user_group.append(i.name)
    if 'Administrator' in user_group:
      self.queryset = SingleTraining.objects.filter(Q(status=4)).order_by('-tdate')
      return super(SingletrainingCompletedListView, self).dispatch(*args, **kwargs)
    if 'Resource Person' in user_group and 'Organiser' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(Q(status=4),
                                                    academic__state__id__in = state_list).order_by('-tdate')
      return super(SingletrainingCompletedListView, self).dispatch(*args, **kwargs)
    elif 'Organiser' in user_group:
      rp_state = self.request.user.organiser.academic_id
      self.queryset = SingleTraining.objects.filter(Q(status=4), academic__id = rp_state).order_by('-tdate')
      return super(SingletrainingCompletedListView, self).dispatch(*args, **kwargs)
    elif 'Resource Person' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(Q(status=4),
                                                    academic__state__id__in = state_list).order_by('-tdate')
      return super(SingletrainingCompletedListView, self).dispatch(*args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(SingletrainingCompletedListView, self).get_context_data(**kwargs)
    temp = self.request.user.groups.all()
    grup = []
    for i in temp:
      grup.append(i.name)
    context['group'] = grup
    return context
"""
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


class SingleTrainingCertificateListView(ListView):
    queryset = SingleTrainingAttendance.objects.none()
    paginate_by = 500
    template_name = ""
    training_request = None

    def dispatch(self, *args, **kwargs):
        self.training_request = SingleTraining.objects.get(pk=kwargs['tid'])
        self.queryset = SingleTrainingAttendance.objects.filter(training_id=self.training_request.id, status=1)
        return super(SingleTrainingCertificateListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SingleTrainingCertificateListView, self).get_context_data(**kwargs)
        context['training'] = self.training_request
        languages = Language.objects.filter(
            id__in=FossAvailableForWorkshop.objects.filter(
                foss_id=self.training_request.course.foss_id
            ).values_list('language_id')
        )
        # language
        # for lang in languages:
        context['languages'] = languages
        return context

"""
''' Pending Attendance '''
class SingletrainingPendingAttendanceListView(ListView):
  queryset = None
  paginate_by = 10

  def dispatch(self, *args, **kwargs):
    user_groups_object = self.request.user.groups.all()
    user_group = []
    for i in user_groups_object:
      user_group.append(i.name)
    if 'Administrator' in user_group:
     # self.queryset = SingleTraining.objects.filter(tdate__lt=datetime.today().date().isoformat(),
                                                     status=2).order_by('-tdate')
     # return super(SingletrainingPendingAttendanceListView, self).dispatch(*args, **kwargs)
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate__lt=datetime.today().date().isoformat(),
                                                    status=2,).order_by('-tdate')
      return super(SingletrainingPendingAttendanceListView, self).dispatch(*args, **kwargs)
    if 'Resource Person' in user_group and 'Organiser' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate__lt=datetime.today().date().isoformat(), status=6,
                                                    academic__state_id__in=state_list).order_by('-tdate')
      return super(SingletrainingPendingAttendanceListView, self).dispatch(*args, **kwargs)
    elif 'Organiser' in user_group:
      org_inst = self.request.user.organiser.academic_id
      self.queryset = SingleTraining.objects.filter(tdate__lt=datetime.today().date().isoformat(), status=2,
                                                    academic__id=org_inst).order_by('-tdate')
      return super(SingletrainingPendingAttendanceListView, self).dispatch(*args, **kwargs)
    elif 'Resource Person' in user_group:
      state_list = []
      rp_state = self.request.user.id
      a = ResourcePerson.objects.filter(user__id=rp_state)
      for i in a:
        state_list.append(i.state_id)
      self.queryset = SingleTraining.objects.filter(tdate__lt=datetime.today().date().isoformat(),
                                                    status=6, academic__state_id__in=state_list).order_by('-tdate')
      return super(SingletrainingPendingAttendanceListView, self).dispatch(*args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(SingletrainingPendingAttendanceListView, self).get_context_data(**kwargs)
    temp = self.request.user.groups.all()
    date_today = datetime.today().date().isoformat()
    grup = []
    for i in temp:
      grup.append(i.name)
    context['group'] = grup
    context['date'] = date_today
    return context
"""

'''
SingleTrainingCreateView will create a request for a new One day workshop.

'''


class SingletrainingCreateView(CreateView):
    form_class = SingleTrainingForm
    template_name = ""
    success_url = "/software-training/single-training/pending/"

    def form_valid(self, form, **kwargs):
        form_data = form.save(commit=False)
        if 'academic' not in self.request.POST:
            form_data.academic = self.request.user.organiser.academic
        elif not self.request.POST.get('academic'):
            form_data.academic = self.request.user.organiser.academic

        form_data.organiser = self.request.user.organiser
        skipped, error, warning, write_flag = self.csv_email_validate(self.request.FILES['csv_file'],
                                                                      str(self.request.POST.get('training_type')))
        csv_error_line_num = ''

        if error or skipped:
            messages.error(self.request, "Batch not added: Error in CSV file")
            for i in error:
                csv_error_line_num = (csv_error_line_num + '%d, ') % (i + 1)
            messages.error(self.request, "You have error(s) in your CSV file on line numbers %s" % (csv_error_line_num))

        else:
            form_data.save()
            student_exists, student_count, csv_data_list = self.create_singletraining_db(
                self.request.FILES['csv_file'], form_data.id, form_data.course.id)
            if len(student_exists) == len(csv_data_list):
                messages.error(self.request, "Batch not added: Batch already exists for the same course")
            elif student_exists:
                messages.error(self.request, "Batch added but Duplicate entries exist in CSV file")
            else:
                messages.success(self.request, "Student Batch added successfully.")
                # SingleTraining.objects.get(id=form_data.id).update(total_participant_count=student_count)
            form_data.participant_count = student_count
            form_data.total_participant_count = student_count
            form_data.save()
            if not student_count:
                form_data.delete()
        return HttpResponseRedirect(self.success_url)

    def email_validator(self, email):
        if email and email.strip():
            email = email.strip().lower()
            try:
                validate_email(email)
                return True
            except:
                pass
        return False

    def get_student_vocational(self, batch_id, email):
        """
        get_student_vocational() will fetch the student object having the
        email id passed to it as an argument.
        """
        if email and email.strip():
            email = email.strip().lower()
            try:
                student = SingleTrainingAttendance.objects.get(email=email, foss=batch_id)
                return student
            except ObjectDoesNotExist:
                pass
        return False

    def create_student_vocational(self, training_id, fossid, fname, lname, email, gender):
        """
        create_student_vocational() will add the database entry for the student
        """
        if not fname or not lname or not email or not gender:
            return False
        fname = fname.strip().upper()
        lname = lname.strip().upper()
        email = email.strip().lower()
        gender = gender.strip().lower()

        if fname and lname and email and gender:
            if gender == 'male' or gender == 'm':
                gender = 'Male'
            else:
                gender = 'Female'
            student = SingleTrainingAttendance.objects.create(
                training_id=training_id, foss=fossid, firstname=fname, lastname=lname, email=email, gender=gender)
            return student
        return False

    def csv_email_validate(self, file_path, ttype):
        """
        csv_email_validate() will validate the email field, from the CSV file,
        for the School and Vocational training type.
        """
        skipped = []
        error = []
        warning = []
        write_flag = False
        csv_data = []
        csvdata = csv.reader(file_path, delimiter=',', quotechar='|')

        # School
        if ttype == '0':
            for i in csvdata:
                csv_data.append(i)
            for j in range(len(csv_data)):
                if len(csv_data[j]) < 3:
                    skipped.append(j)
                    continue
                if csv_data[j][0] == '':
                    error.append(j)
                    continue
                if csv_data[j][1] == '':
                    error.append(j)
                    continue
                if csv_data[j][3] == '':
                    error.append(j)
                    continue

        # Vocational
        else:
            for i in csvdata:
                csv_data.append(i)
            for j in range(len(csv_data)):
                if len(csv_data[j]) < 4:
                    skipped.append(j)
                    continue
                if csv_data[j][0] == '':
                    error.append(j)
                    continue
                if csv_data[j][1] == '':
                    error.append(j)
                    continue
                if not self.email_validator(csv_data[j][2]):
                    error.append(j)
                    continue
                if csv_data[j][3] == '':
                    error .append(j)
                    continue

        return skipped, error, warning, write_flag

    def create_singletraining_db(self, file_path, tr_id, batch_id):
        """
        This will call the create_student_vocational() method to create
        the student entry, from the  CSV file, in the SingleTraining database.
        """
        csv_data_list = []
        student_exists = []
        csvdata = csv.reader(file_path, delimiter=',', quotechar='|')
        for i in csvdata:
            csv_data_list.append(i)
        for j in range(len(csv_data_list)):
            student = self.get_student_vocational(batch_id, csv_data_list[j][2])
            if student:
                student_exists.append(student)
            else:
                self.create_student_vocational(tr_id, batch_id, csv_data_list[j][0], csv_data_list[
                                               j][1], csv_data_list[j][2], csv_data_list[j][3])
            student_count = SingleTrainingAttendance.objects.filter(training_id=tr_id).count()
        return student_exists, student_count, csv_data_list


class SingletrainingUpdateView(UpdateView):
    """
    SingleTrainingUpdateView will update a request for a existing One day workshop.
    """
    model = SingleTraining
    form_class = SingleTrainingEditForm
    success_url = "/software-training/single-training/pending/"

    def form_valid(self, form, **kwargs):
        form_data = form.save(commit=False)
        if 'csv_file' in self.request.FILES and self.request.FILES['csv_file']:
            stcv = SingletrainingCreateView()
            skipped, error, warning, write_flag = stcv.csv_email_validate(
                self.request.FILES['csv_file'], str(self.request.POST.get('training_type')))
            csv_error_line_num = ''
            if error or skipped:
                for i in error:
                    csv_error_line_num = (csv_error_line_num + '%d, ') % (i + 1)
                messages.error(self.request, "You have error(s) in your CSV file on line numbers %s" %
                               (csv_error_line_num))

            else:
                form_data.save()
                student_exists, student_count, csv_data_list = stcv.create_singletraining_db(
                    self.request.FILES['csv_file'], form_data.id, form_data.course.id)

                form_data.participant_count = student_count
                form_data.total_participant_count = student_count
        form_data.save()
        messages.success(self.request, "Student Batch updated successfully.")
        return HttpResponseRedirect(self.success_url)


class SingleTrainingListView(ListView):
    """
    SingleTrainingListView will list all the new/pending training requests in
    the single-training page pertaining to a specific user,
    i.e, Organiser or Resource Person.
    """
    queryset = None
    paginate_by = 10
    user = None
    status = None

    @method_decorator(group_required("Organiser", "Resource Person", "Administrator"))
    def dispatch(self, *args, **kwargs):
        user = self.request.user
        status_list = {
            'pending': 0,
            'approved': 2,
            'ongoing': 3,
            'completed': 4,
            'rejected': 5,
            'pendingattendance': 6,
        }
        self.status = kwargs['status']
        if self.status not in status_list:
            raise PermissionDenied()

        if is_administrator(user):
            self.queryset = SingleTraining.objects.filter(Q(status=status_list[self.status])).order_by('-tdate')
            return super(SingleTrainingListView, self).dispatch(*args, **kwargs)

        if is_resource_person(user) and is_organiser(user):
            self.queryset = SingleTraining.objects.filter(
                Q(status=status_list[self.status]),
                academic__state=user.resource_person.filter(resourceperson__status=1)).order_by('-tdate')

        elif is_organiser(user):
            self.queryset = SingleTraining.objects.filter(
                Q(status=status_list[self.status]),
                academic__id=self.request.user.organiser.academic_id).order_by('-tdate')

        elif is_resource_person(user):
            self.queryset = SingleTraining.objects.filter(
                Q(status=status_list[self.status]),
                academic__state=user.resource_person.filter(resourceperson__status=1)).order_by('-tdate')
        return super(SingleTrainingListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SingleTrainingListView, self).get_context_data(**kwargs)
        context['status'] = self.status
        return context


class SingletrainingMarkCompleteUpdateView(UpdateView):
    '''
    SingletrainingMarkCompleteUpdateView will update ongoing to completed.
    '''
    model = SingleTraining
    form_class = SingleTrainingEditForm
    success_url = "/software-training/single-training/completed/"

    def dispatch(self, *args, **kwargs):
        st = SingleTraining.objects.get(pk=kwargs['pk'])
        if not self.request.user.id == st.organiser.user_id:
            return HttpResponseRedirect('/software-training/single-training/ongoing/')

        if st.training_type in [1, 2] and st.tdate <= datetime.today().date() and st.status == 3:
            st.status = 4
            st.save()
            return HttpResponseRedirect(self.success_url)

        date_extn = datetime.today().date() + timedelta(days=15)
        if date_extn >= st.tdate or st.status != 3:
            return HttpResponseRedirect('/software-training/single-training/ongoing/')

        st.status = 4
        st.save()
        return HttpResponseRedirect(self.success_url)
        return super(SingletrainingMarkCompleteUpdateView, self).dispatch(*args, **kwargs)


class SingleTrainingAttendanceListView(ListView):
    """
    SingleTrainingAttendance is used to (1) List the attendance view, (2) Mark the attendance
    """
    queryset = SingleTrainingAttendance.objects.none()
    paginate_by = 500
    template_name = ""
    single_training = None

    @method_decorator(group_required("Organiser", "Resource Person", "Administrator"))
    def dispatch(self, *args, **kwargs):
        self.single_training = SingleTraining.objects.get(pk=kwargs['tid'])
        # if status 4 redirect to download certificate page
        if self.single_training.status == 4:
            return HttpResponseRedirect('/software-training/single-training/completed/')

        if self.single_training.status == 2 or self.single_training.status == 3:
            #     self.queryset = self.training_request.trainingattend_set.all()
            self.queryset = SingleTrainingAttendance.objects.filter(training_id=self.single_training.id)
        elif self.single_training.status == 4:
            self.queryset = SingleTrainingAttendance.objects.filter(training_id=self.single_training.id, status=1)
        else:
            self.queryset = SingleTrainingAttendance.objects.filter(training_id=self.single_training.id)
        return super(SingleTrainingAttendanceListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SingleTrainingAttendanceListView, self).get_context_data(**kwargs)
        """date_today = datetime.today().date().isoformat()
    participant_count = self.queryset[0].training.participant_count
    tr_date = self.queryset[0].training.tdate
    training_date = self.queryset[0].training.tdate.isoformat()
    training_status = self.queryset[0].training.status
    institute_id = self.queryset[0].training.academic_id
    institute = AcademicCenter.objects.get(id=institute_id)
    foss_id = self.queryset[0].training.course_id
    foss_list = CourseMap.objects.get(id=foss_id)
    foss_name_list = foss_list.foss
    organiser_id = self.queryset[0].training.organiser_id
    organiser_object = Organiser.objects.get(id=organiser_id).user_id
    organiser_firstname = User.objects.get(id=organiser_object).first_name
    organiser_lastname = User.objects.get(id=organiser_object).last_name
    organiser_name = organiser_firstname + " " + organiser_lastname
    date_extn = tr_date + timedelta(days=15)
    date_extn = date_extn.isoformat()
    total_participant_count = SingleTrainingAttendance.objects.filter(training_id=self.single_training_request.id)
    temp = self.request.user.groups.all()
    grup = []
    for i in temp:
      grup.append(i.name)
    context['total_participant_count'] = total_participant_count
    context['organiser_name'] = organiser_name
    context['pr_count'] = participant_count
    context['tdate'] = tr_date
    context['extn_date'] = date_extn
    context['foss'] = foss_name_list
    context['institute'] = institute
    context['group'] = grup
    context['date'] = date_today
    context['training_date'] = training_date
    context['training_status'] = training_status"""
        attendance = self.single_training.singletrainingattendance_set.filter(status=True).count()
        canComplete = False
        if (self.single_training.training_type in [1, 2] and
                self.single_training.tdate <= datetime.today().date() and
                self.single_training.status == 3 and attendance):
            canComplete = True

        date_extn = datetime.today().date() - timedelta(days=15)
        if (date_extn <= self.single_training.tdate and
                self.single_training.status == 3 and
                is_resource_person(self.request.user) and
                attendance):
            canComplete = True

        context['single_training'] = self.single_training
        context['canComplete'] = canComplete
        return context

    def post(self, request, *args, **kwargs):
        training_id = kwargs['tid']
        if request.POST:
            if csrf.get_token(request) == request.POST['csrfmiddlewaretoken']:
                marked_student = request.POST.getlist('user', None)
                if marked_student:
                    SingleTrainingAttendance.objects.filter(training_id=training_id).update(status=0)
                for record in marked_student:
                    student = SingleTrainingAttendance.objects.get(id=record)
                    student.status = 1
                    training_id = student.training_id
                    student.save()
                training_status = SingleTraining.objects.get(id=training_id)
                training_status.status = 3
                training_status.participant_count = len(marked_student)
                training_status.save()
        return HttpResponseRedirect('/software-training/single-training/' + str(self.
                                                                                single_training.id) + '/attendance')

    '''
  def post(self, request, *args, **kwargs):
    self.object = None
    self.user = request.user
    training_id = kwargs['tid']
    if request.POST and 'user' in request.POST:
      if csrf.get_token(request) == request.POST['csrfmiddlewaretoken']:
        marked_student = request.POST.getlist('user', None)
        # delete un marked record if exits
        TrainingAttend.objects.filter(training_id =training_id).exclude(student_id__in = marked_student).delete()
        # insert new record if not exits
        for record in marked_student:
          language_id = request.POST.get(record)
          training_attend = TrainingAttend.objects.filter(training_id =training_id, student_id = record)
          if not training_attend.exists():
            TrainingAttend.objects.create(training_id =training_id, student_id = record, language_id=language_id)
          else:
            training_attend = training_attend.first()
            training_attend.language_id = language_id
            training_attend.save()
      #print marked_student
    else:
      TrainingAttend.objects.filter(training_id =training_id).delete()
    self.training_request.update_participants_count()
    return HttpResponseRedirect('/software-training/training-planner')
  '''


def SingleTrainingApprove(request, pk):
    '''SingleTrainingApprove will take an argument(primary key of a training batch)
     and change the status of the SingleTraining batch, in the SingleTraining database,
     from pending to approved.

    Status code:
    ------------
    0 - new/pending
    2 - approved
    3 - ongoing
    4 - completed
    5 - Rejected
    6 - PendingAttendanceMark
    '''
    st = SingleTraining.objects.get(pk=pk)
    if st:
        st.status = 2
        st.save()
        # Send Emails from here
    else:
        print("Error")
    return HttpResponseRedirect('/software-training/single-training/approved/')


def SingleTrainingReject(request, pk):
    """
    SingleTrainingReject will take an argument(primary key of a training batch)
    and change the status of the SingleTraining batch, in the database, from
    pending to rejected
    """
    st = SingleTraining.objects.get(pk=pk)
    if st:
        st.status = 5
        st.save()
    else:
        print("Error")
    return HttpResponseRedirect("/software-training/single-training/approved/")

# using in stp mark attendance also


def SingleTrainingPendingAttendance(request, pk):
    st = SingleTraining.objects.get(pk=pk)
    if st:
        st.status = 6
        st.save()
    else:
        print("Error")
    return HttpResponseRedirect("/software-training/single-training/pending/")


def MarkAsComplete(request, pk):
    st = TrainingRequest.objects.get(pk=pk)
    if st:
        st.status = 2  # request mark to complete
        st.save()
        messages.success(request, 'Request to mark training complete successfully sent')
    else:
        messages.error(request, 'Request not sent.Please try again.')
    return HttpResponseRedirect("/software-training/training-planner/")


def MarkComplete(request, pk):
    st = TrainingRequest.objects.get(pk=pk)
    if st and st.status == 2:
        st.status = 1  # mark to complete
        st.save()
        messages.success(request, 'Training Marked as complete.')
    else:
        messages.error(request, 'Something went wrong Please try again')
    return HttpResponseRedirect("/software-training/training-request/rp/markcomplete/")


class OldTrainingListView(ListView):
    queryset = Training.objects.none()
    paginate_by = 50
    template_name = ""
    header = None
    raw_get_data = None

    @method_decorator(group_required("Resource Person"))
    def dispatch(self, *args, **kwargs):
        self.queryset = Training.objects.exclude(
            id__in=TrainingRequest.objects.filter(participants__gt=0).values_list('id'),
        ).filter(Q(status__gte=1) & Q(status__lte=3),
                 id__in=TrainingAttendance.objects.all().values_list('training_id').distinct(),
                 academic__state_id__in=self.request.user.resourceperson_set.all().values_list('state_id').distinct())
        self.header = {
            1: SortableHeader('#', False),
            2: SortableHeader('academic', True, 'Institution'),
            3: SortableHeader('academic__state', True, 'State'),
            4: SortableHeader('foss_foss', True, 'Foss'),
            5: SortableHeader('tdate', True, 'Date'),
            6: SortableHeader('id', True, 'Workshop Code'),
            7: SortableHeader('Action', False, ''),
        }
        self.raw_get_data = self.request.GET.get('o', None)
        self.queryset = get_sorted_list(self.request, self.queryset, self.header, self.raw_get_data)
        return super(OldTrainingListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OldTrainingListView, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['ordering'] = get_field_index(self.raw_get_data)
        return context


class OldStudentListView(ListView):
    queryset = TrainingAttendance.objects.none()
    paginate_by = 0
    template_name = None
    header = None
    raw_get_data = None

    @method_decorator(group_required("Resource Person"))
    def dispatch(self, *args, **kwargs):
        self.queryset = TrainingAttendance.objects.filter(training_id=kwargs['tid'])
        self.header = {
            1: SortableHeader('#', False),
            2: SortableHeader('firstname', True, 'First Name'),
            3: SortableHeader('lastname', True, 'Last Name'),
            4: SortableHeader('email', True, 'Email'),
            5: SortableHeader('gender', True, 'Gender'),
            6: SortableHeader('', False, ''),
        }
        self.raw_get_data = self.request.GET.get('o', None)
        self.queryset = get_sorted_list(self.request, self.queryset, self.header, self.raw_get_data)
        return super(OldStudentListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OldStudentListView, self).get_context_data(**kwargs)
        context['header'] = self.header
        context['ordering'] = get_field_index(self.raw_get_data)
        return context


class OldTrainingCloseView(CreateView):

    def _find_course(self, foss, category):
        return CourseMap.objects.get(foss=foss, category=category)

    def _create_training_planner(self, year, academic_id, organiser_id, created, even=False):
        tp = None
        semester = 2
        if even:
            year = int(year) - 1
            semester = 1
        try:
            tp = TrainingPlanner.objects.get(year=year, academic_id=academic_id,
                                             organiser_id=organiser_id, semester__even=even)
        except:
            try:
                tp = TrainingPlanner()
                tp.semester_id = semester
                tp.year = year
                tp.academic_id = academic_id
                tp.organiser_id = organiser_id
                tp.created = created
                tp.updated = created
                tp.save()
            except Exception as e:
                print(e)
        return tp

    def _get_student(self, ta):
        mail = ta.email.strip().lower()
        firstname = ta.firstname.strip()
        lastname = ta.lastname.strip()
        student = None
        if firstname:
            firstname = firstname.upper()
        if lastname:
            lastname = lastname.upper()
        gender = 'Female'
        if ta.gender == 'Male' or ta.gender == 'M':
            gender = 'Male'
        user = None
        try:
            user = User.objects.get(email=mail)
        except:
            user = User.objects.create_user(mail, mail, firstname)
        if user:
            try:
                user.groups.add(student)
            except:
                pass
            try:
                student = Student.objects.get(user=user)
            except:
                student = Student.objects.create(user=user, gender=gender)
        return student

    def _fill_participants_attendance(self, tr, otr, language):
        st_count = 0
        tas = TrainingAttendance.objects.exclude(email=None).filter(training=otr)
        for ta in tas:
            student = self._get_student(ta)
            if not student:
                continue
            if not TrainingAttend.objects.filter(training=tr, student=student).count():
                TrainingAttend.objects.create(training=tr, student=student, language=language)
            st_count += 1
        return st_count

    def dispatch(self, *args, **kwargs):
        if 'tid' in kwargs:
            training = Training.objects.filter(pk=kwargs['tid'])
            others = Department.objects.get(name="Others")
            if training.exists():
                training = training.first()
                try:
                    new_training = TrainingRequest.objects.get(pk=training.id)
                    new_training = self._fill_participants_attendance(tr, training, training.language)
                    new_training.save()
                    messages.error(self.request, 'The selected training is already added to Semester-Planner')
                except:
                    year = str(datetime.now().year)
                    tdate = datetime.strptime(training.tdate.strftime('%Y-%m-%d'), '%Y-%m-%d')
                    even_start = datetime.strptime(year + '-01-01', '%Y-%m-%d')
                    even_end = datetime.strptime(year + '-06-30', '%Y-%m-%d')
                    if tdate >= even_start and tdate <= even_end:
                        tp = self._create_training_planner(
                            year, training.academic_id, training.organiser_id, training.tdate, even=True)
                    else:
                        tp = self._create_training_planner(
                            year, training.academic_id, training.organiser_id, training.tdate)
                    if tp:
                        tr = TrainingRequest()
                        tr.id = training.id
                        tr.sem_start_date = training.tdate
                        tr.created = training.created
                        tr.updated = training.updated
                        tr.batch_id = None
                        tr.course = self._find_course(training.foss, 0)
                        if not training.department.first():
                            training.department.add(others.id)
                        tr.department = training.department.first()  # what to do if multiple dept
                        tr.language = training.language
                        tr.training_planner = tp
                        tr.status = 1
                        tr.save()
                        tr_count = self._fill_participants_attendance(tr, training, training.language)
                        tr.participants = tr_count
                        tr.save()
                        messages.success(self.request, 'Training status updated successfully')
                return HttpResponseRedirect('/software-training/old-training/')
            else:
                return PermissionDenied()
        return super(OldTrainingCloseView, self).dispatch(*args, **kwargs)


class OrganiserFeedbackCreateView(CreateView):
    form_class = OrganiserFeedbackForm
    template_name = "organiser_feedback.html"
    success_url = "/"

    @method_decorator(group_required("Organiser"))
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            form.save()
            messages.success(self.request, ("Thank you for completing this feedback form. "
                                            "We appreciate your input and valuable suggestions."))
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(form)


class OrganiserFeedbackListView(ListView):
    queryset = None
    paginate_by = 10

    def dispatch(self, *args, **kwargs):
        self.queryset = OrganiserFeedback.objects.all()
        return super(OrganiserFeedbackListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrganiserFeedbackListView, self).get_context_data(**kwargs)
        context['count'] = OrganiserFeedback.objects.all().count()
        return context


def LatexWorkshopFileUpload(request):
    template_name = 'latex_workshop_file_upload.html'
    if request.method == 'POST':
        form = LatexWorkshopFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = LatexWorkshopFileUploadForm()
            context = {'form': form, 'success': True}
            return render(request, template_name, context)
        else:
            context = {'form': form}
            return render(request, template_name, context)
    else:
        form = LatexWorkshopFileUploadForm()
        context = {'form': form}
    return render(request, template_name, context)


class UpdateStudentName(UpdateView):
    model = User
    form_class = UserForm

    def dispatch(self, *args, **kwargs):
        self.success_url = "/software-training/student-batch/" + str(kwargs['bid']) + "/view"
        return super(UpdateStudentName, self).dispatch(*args, **kwargs)
