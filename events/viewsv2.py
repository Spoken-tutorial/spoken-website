from django.shortcuts import render
from datetime import datetime

# Create your views here.
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from events.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils.decorators import method_decorator
from events.decorators import group_required
from events.forms import StudentBatchForm, TrainingRequestForm, \
    TrainingRequestEditForm, CourseMapForm, SingleTrainingForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.core.validators import validate_email
from django.contrib.auth.models import Group, User
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.middleware import csrf
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from creation.models import FossAvailableForWorkshop
import csv
from cms.sortable import *
from django.contrib import messages

#pdf generate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from PyPDF2 import PdfFileWriter, PdfFileReader
from StringIO import StringIO

class JSONResponseMixin(object):
  """
  A mixin that can be used to render a JSON response.
  """
  def render_to_json_response(self, context, **response_kwargs):
    """
    Returns a JSON response, transforming 'context' to make the payload.
    """
    return JsonResponse(
        self.get_data(context),
        **response_kwargs
    )

  def get_data(self, context):
    """
    Returns an object that will be serialized as JSON by json.dumps().
    """
    # Note: This is *EXTREMELY* naive; in reality, you'll need
    # to do much more complex handling to ensure that arbitrary
    # objects -- such as Django model instances or querysets
    # -- can be serialized as JSON.
    return context

class TrainingPlannerListView(ListView):
  queryset = None
  paginate_by = 20
  user = None
  template_name = None
  @method_decorator(group_required("Organiser"))
  def dispatch(self, *args, **kwargs):
    self.user = self.request.user
    self.get_current_planner()
    self.queryset = TrainingPlanner.objects.filter(
        organiser_id = self.request.user.organiser.id,
        academic_id = self.request.user.organiser.academic.id,
      ).order_by('-year')
    return super(TrainingPlannerListView, self).dispatch(*args, **kwargs)
  
  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(TrainingPlannerListView, self).get_context_data(**kwargs)
    # Add in a QuerySet of all the books
    context['current_planner'] = self.get_current_planner()
    context['next_planner'] = self.get_next_planner(context['current_planner'])
    return context

  #def get(self, request):
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
      return TrainingPlanner.objects.get(year=year, semester__even=sem, \
        academic=self.user.organiser.academic, organiser=self.user.organiser)
    except ObjectDoesNotExist:
      return TrainingPlanner.objects.create(year=year, \
        semester=self.get_semester(sem), academic=self.user.organiser.academic,\
          organiser=self.user.organiser)
    except Exception, e:
      print e
    return False
  def get_next_planner(self, current_planner):
    year = int(current_planner.year)
    even = True
    if current_planner.semester.even:
      year = year + 1
      even = False
    sem = self.get_semester(even)
    try:
      next_planner = TrainingPlanner.objects.get(year=year, semester=sem, \
        academic=self.user.organiser.academic, organiser=self.user.organiser)
      return next_planner
    except ObjectDoesNotExist:
      return TrainingPlanner.objects.create(year=year, \
        semester=sem, academic=self.user.organiser.academic, \
        organiser=self.user.organiser)
    except Exception, e:
      print e
    return False

class StudentBatchCreateView(CreateView):
  form_class = None
  template_name = None
  user = None
  batch = None

  @method_decorator(group_required("Organiser"))
  def dispatch(self, *args, **kwargs):
    if 'bid' in kwargs:
      sb = StudentBatch.objects.filter(pk=kwargs['bid'])
      if sb.exists():
        self.batch = sb.first()
    return super(StudentBatchCreateView, self).dispatch(*args, **kwargs)

  #def get_form_kwargs(self):
  #  kwargs = super(StudentBatchCreateView, self).get_form_kwargs()
  #  kwargs.update({'user' : self.request.user})
  #  return kwargs
  
  def get_context_data(self, **kwargs):
    context = super(StudentBatchCreateView, self).get_context_data(**kwargs)
    if self.batch:
      existing_student = Student.objects.filter(
        id__in=StudentMaster.objects.filter(
          batch_id=self.batch.id,
          moved=False
        ).values_list(
          'student_id'
        )
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
    form_data.organiser = self.user.organiser
    try:
      if 'bid' in self.kwargs:
        form_data = StudentBatch.objects.get(pk=self.kwargs['bid'])
      else:
        form_data = StudentBatch.objects.get(year=form_data.year, academic=form_data.academic, department=form_data.department)
    except ObjectDoesNotExist:
      form_data.save()
    except Exception, e:
      print e
      return HttpResponseRedirect("/software-training/student-batch/")
    skipped, error, warning, write_flag = \
      self.csv_email_validate(self.request.FILES['csv_file'], form_data.id)
    context = {'error' : error, 'warning' : warning, 'batch':form_data}
    
    if error or warning:
      return render_to_response(self.template_name, context, context_instance=RequestContext(self.request))
#    messages.success(self.request, "Student Batch added successfully.")
    return HttpResponseRedirect('/software-training/student-batch/%s/new/'%(str(form_data.id)))

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
        user = User.objects.get(email = email)
      except ObjectDoesNotExist:
        user = User.objects.create_user(email, email, fname)
        user.is_active = False
      if user:
        user.first_name = fname
        user.last_name = lname
        user.save()
        try:
          student_group = Group.objects.get(name = 'Student')
          user.groups.add(student_group)
        except:
          pass
        student = Student.objects.create(user = user, gender = gender)
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
    except:
      messages.warning(self.request, "The file you uploaded is not a valid CSV file, please add a valid CSV file")
    return skipped, error, warning, write_flag

class StudentBatchUpdateView(UpdateView):
    model = StudentBatch
    success_url = "/software-training/student-batch/"
    @method_decorator(group_required("Organiser"))
    def dispatch(self, *args, **kwargs):
      #trainingrequest_set.all()
      if 'pk' in kwargs:
        try:
          sb = StudentBatch.objects.get(pk=kwargs['pk'])
          if sb.trainingrequest_set.exists():
            messages.warning(self.request, 'This Student Batch has Training. You can not edit this batch.')
            return HttpResponseRedirect('/software-training/student-batch/')
        except:
          pass
      return super(StudentBatchUpdateView, self).dispatch(*args, **kwargs)


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
        2: SortableHeader('', False, 'Department'),
        3: SortableHeader('', False, 'Year'),
        4: SortableHeader('user__first_name', True, 'First Name'),
        5: SortableHeader('user__last_name', True, 'Last Name'),
        6: SortableHeader('user__email', True, 'Email'),
        7: SortableHeader('gender', True, 'Gender'),
        8: SortableHeader('', False, 'Status'),
        9: SortableHeader('', False, ''),
    }
    self.queryset = Student.objects.filter(
      id__in = StudentMaster.objects.filter(
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
      training_planner = TrainingPlanner.objects.filter(pk=self.tpid, organiser_id = self.request.user.organiser.id)
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
    return context

  def get_form_kwargs(self):
    kwargs = super(TrainingRequestCreateView, self).get_form_kwargs()
    kwargs.update({'user' : self.request.user})
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
      if sb.is_foss_batch_acceptable(form_data.course.id):
        form_data.training_planner_id = self.kwargs['tpid']
        form_data.participants = StudentMaster.objects.filter(batch_id = form_data.batch_id).count()
        form_data.save()
      else:
        messages.error(self.request, 'This student batch already taken the selected course.')
        return self.form_invalid(form)
    except:
      messages.error(self.request, 'Something went wrong, Contact site administrator.')
      return self.form_invalid(form)
    context = {}
    return HttpResponseRedirect('/software-training/training-planner/')
    #return render_to_response(self.template_name, context, context_instance=RequestContext(self.request))

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
    kwargs.update({'training' : self.training})
    kwargs.update({'user' : self.request.user})
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
    except Exception, e:
      print e
      messages.error(self.request, 'Something went wrong, Contact site administrator.')
      return self.form_invalid(form)
    context = {}
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
    if self.training_request.status:
      self.queryset = self.training_request.trainingattend_set.all()
    else:
      self.queryset = StudentMaster.objects.filter(batch_id=self.training_request.batch_id, moved=False)
    return super(TrainingAttendanceListView, self).dispatch(*args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(TrainingAttendanceListView, self).get_context_data(**kwargs)
    context['training'] = self.training_request
    languages = Language.objects.filter(
        id__in = FossAvailableForWorkshop.objects.filter(
          foss_id = self.training_request.course.foss_id
        ).values_list('language_id')
      )
    #language
    #for lang in languages:
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

class StudentDeleteView(DeleteView):
  model=Student
  def dispatch(self, *args, **kwargs):
    self.success_url="/software-training/student-batch/"+str(kwargs['bid'])+"/view"
    student = super(StudentDeleteView, self).get_object()
    if student.is_student_has_attendance():
      messages.error(self.request, "You do not have permission to delete " + student.student_fullname())
      return HttpResponseRedirect(self.success_url)
    try:
      sm = StudentMaster.objects.get(student=student, moved=False)
      if not sm.batch.organiser_id == self.request.user.organiser.id:
        messages.error(self.request, "You do not have permission to delete " + student.student_fullname())
        return HttpResponseRedirect(self.success_url)
    except:
      pass
    return super(StudentDeleteView, self).dispatch(*args, **kwargs)

class TrainingCertificate():
  def custom_strftime(self, format, t):
    return t.strftime(format).replace('{S}', str(t.day) + self.suffix(t.day))

  def suffix(self, d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

  def training_certificate(self, ta):
    response = HttpResponse(content_type='application/pdf')
    filename = (ta.student.user.first_name+'-'+ta.training.course.foss.foss+"-Participant-Certificate").replace(" ", "-");
    
    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = StringIO()
    imgDoc = canvas.Canvas(imgTemp)

    # Title 
    imgDoc.setFont('Helvetica', 40, leading=None)
    imgDoc.drawCentredString(415, 480, "Certificate of Learning")

    #date
    imgDoc.setFont('Helvetica', 18, leading=None)
    imgDoc.drawCentredString(211, 115, self.custom_strftime('%B {S} %Y', ta.training.sem_start_date)) 

    #password
    certificate_pass = ''
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)

    # Draw image on Canvas and save PDF in buffer
    imgPath = settings.MEDIA_ROOT +"sign.jpg"
    imgDoc.drawImage(imgPath, 600, 100, 150, 76)

    #paragraphe
    text = "This is to certify that <b>"+ta.student.user.first_name +" "+ta.student.user.last_name+"</b> participated in the <b>"+ta.training.course.foss.foss+"</b> training organized at <b>"+ta.training.training_planner.academic.institution_name+"</b> by  <b>"+ta.training.training_planner.organiser.user.first_name + " "+ta.training.training_planner.organiser.user.last_name+"</b> on <b>"+self.custom_strftime('%B {S} %Y', ta.training.sem_start_date)+"</b> with course material provided by the Talk To A Teacher project at IIT Bombay.<br /><br />A comprehensive set of topics pertaining to <b>"+ta.training.course.foss.foss+"</b> were covered in the workshop. This training is offered by the Spoken Tutorial Project, IIT Bombay, funded by National Mission on Education through ICT, MHRD, Govt., of India."
    
    centered = ParagraphStyle(name = 'centered',
      fontSize = 16,  
      leading = 30,  
      alignment = 0,  
      spaceAfter = 20
    )

    p = Paragraph(text, centered)
    p.wrap(650, 200)
    p.drawOn(imgDoc, 4.2 * cm, 7 * cm)

    imgDoc.save()

    # Use PyPDF to merge the image-PDF into the template
    page = PdfFileReader(file(settings.MEDIA_ROOT +"Blank-Certificate.pdf","rb")).getPage(0)
    overlay = PdfFileReader(StringIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)
    
    #stream to browser
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
    except Exception, e:
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
    collection = get_sorted_list(self.request, self.queryset, self.header, self.raw_get_data)
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


### Ajax
class SaveStudentView(JSONResponseMixin, View):
  @method_decorator(csrf_exempt)
  def dispatch(self, *args, **kwargs):
    return super(SaveStudentView, self).dispatch(*args, **kwargs)

  def post(self, request, *args, **kwargs):
    sb = StudentBatchCreateView()
    email = self.request.POST.get('email').strip().lower()
    message = ''
    code = 0 # 0 => None, 1 => Warning, 2 => Error
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
      'code' : code,
      'message' : message
    }
    return self.render_to_json_response(context)

class GetCourseOptionView(JSONResponseMixin, View):
  @method_decorator(csrf_exempt)
  def dispatch(self, *args, **kwargs):
    return super(GetCourseOptionView, self).dispatch(*args, **kwargs)
  
  def post(self, request, *args, **kwargs):
    
    context = {}
    category = self.request.POST.get('course_type')
    tp = TrainingPlanner.objects.get(pk=self.request.POST.get('training_planner'))
    if tp.is_course_full(category, self.request.POST.get('department')):
      context['is_full'] = True
    else:
      courses = CourseMap.objects.filter(category=category)
      course_option = "<option value=''>---------</option>"
      for course in courses:
        course_detail = '{0} ({1})'.format(course.foss.foss, course.course)
        if course.course:
          course_option += "<option value=" + str(course.id) + ">" + course_detail +  "</option>"
        else:
          course_option += "<option value=" + str(course.id) + ">" + course.foss.foss + "</option>"
      context = {
        'course_option' : course_option,
        'is_full' : False
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
    tp = TrainingPlanner.objects.get(pk=self.request.POST.get('training_planner'))
    if tp.is_full(department_id):
      context['is_full'] = True
    else:
      batches = StudentBatch.objects.filter(
        academic_id=request.user.organiser.academic.id,
        stcount__gt=0,
        department_id=department_id
      )
      batch_option = "<option value=''>---------</option>"
      for batch in batches:
        batch_option += "<option value=" + str(batch.id) + ">" + str(batch) + "</option>"
      context = {
        'batch_option' : batch_option,
        'is_full' : False
      }
    return self.render_to_json_response(context)


class SingletrainingApprovedListView(ListView):
  queryset = None
  paginate_by = 10
  
  def dispatch(self, *args, **kwargs):
    self.queryset = SingleTraining.objects.filter(Q(status=0) | Q(status=1))
    return super(SingletrainingApprovedListView, self).dispatch(*args, **kwargs)

class SingletrainingCompletedListView(ListView):
  queryset = None
  paginate_by = 10
  
  def dispatch(self, *args, **kwargs):
    self.queryset = SingleTraining.objects.filter(status=2)
    return super(SingletrainingCompletedListView, self).dispatch(*args, **kwargs)

class SingletrainingCreateView(CreateView):
  form_class = SingleTrainingForm
  template_name = ""
  success_url = "/software-training/single-training/approved/"
  
  def form_valid(self, form, **kwargs):
    form_data = form.save(commit=False)
    form_data.academic = self.request.user.organiser.academic
    form_data.organiser = self.request.user.organiser
    skipped, error, warning, write_flag = self.csv_email_validate(self.request.FILES['csv_file'], form_data.id, str(self.request.POST.get('training_type')))
    context = {'error': error, 'warning': warning, 'batch': form_data}
    csv_error_line_num = ''
    
    if error or skipped:
#     print error, skipped
#     print self.request.POST.get('training_type')
      return render_to_response(self.template_name, context, context_instance=RequestContext(self.request))
      messages.error(self.request, "Batch not added: Error in CSV file")
      for i in error:
        csv_error_line_num = (csv_error_line_num+'%d, ')%(i+1)
      messages.error(self.request, "You have error(s) in your CSV file on line numbers %s"%(csv_error_line_num))
      
    else:
      messages.success(self.request, "Student Batch added successfully.")
      form_data.save()
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

  def csv_email_validate(self, file_path, batch_id, ttype):
    skipped = []
    error = []
    warning = []
    write_flag = False
    csv_data = []
    csvdata = csv.reader(file_path, delimiter=',', quotechar='|')

    #School
    if ttype == '0':
      for i in csvdata:
        csv_data.append(i)
      for j in range(len(csv_data)):
        if len(csv_data[j]) < 3:
          skipped.append(j)
          continue
      
    #Vocational
    else:
      for i in csvdata:
        csv_data.append(i)
      for j in range(len(csv_data)):
        if len(csv_data[j]) < 4:
          skipped.append(j)
          continue
        if not self.email_validator(csv_data[j][2]):
          error.append(j)
          continue
        
    '''
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
      StudentBatch.objects.get(pk=batch_id).update_student_count()'''
    return skipped, error, warning, write_flag
  
  
'''class GetLanguageOptionView(JSONResponseMixin, View):
  @method_decorator(csrf_exempt)
  def dispatch(self, *args, **kwargs):
    return super(GetLanguageOptionView, self).dispatch(*args, **kwargs)
  
  def post(self, request, *args, **kwargs):
    try:
      course = CourseMap.objects.get(pk=self.request.POST.get('course'))
    except Exception, e:
      return HttpResponse('')
    context = {
      'languages': Language.objects.filter(
        id__in = FossAvailableForWorkshop.objects.filter(
          foss_id = course.foss_id
        ).values_list('language_id')
      )
    }
    return render(request, 'language_options.html', context)
'''


class TrainingRequestListView(ListView):
  queryset = None
  paginate_by = 20
  user = None
  template_name = None
  header = None
  raw_get_data = None
  role = None
  status = None

  @method_decorator(group_required("Resource Person"))
  def dispatch(self, *args, **kwargs):
    print 'entered', '************************'
    if (not 'role' in kwargs) or (not 'status' in kwargs):
      print 11111111
      raise PermissionDenied()
    self.role = kwargs['role']
    self.status = kwargs['status']
    status_list = {'pending': 0, 'completed': 1}
    roles = ['rp', 'em']
    self.user = self.request.user
    if self.role in roles and self.status in status_list:
      if self.status == 'completed':
        self.queryset = TrainingRequest.objects.filter(
          training_planner__academic_id__in=AcademicCenter.objects.filter(
            state__in = State.objects.filter(
              resourceperson__user_id=self.user, 
              resourceperson__status=1
            )
          ).values_list('id'), 
          status=True,
          participants__gt=0
        ).order_by('-updated')
      else:
        self.queryset = TrainingRequest.objects.filter(
          training_planner__academic_id__in=AcademicCenter.objects.filter(
            state__in = State.objects.filter(
              resourceperson__user_id=self.user, 
              resourceperson__status=1
            )
          ).values_list('id'), 
          status=False
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
        5: SortableHeader('course__foss__foss', True, 'FOSS'),
        6: SortableHeader('course__course', True, 'Course Name'),
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
        #11: SortableHeader('Action', False)
      }
      self.raw_get_data = self.request.GET.get('o', None)
      self.queryset = get_sorted_list(
        self.request, 
        self.queryset, 
        self.header, 
        self.raw_get_data
      )
    else:
      print 222222
      raise PermissionDenied()
    return super(TrainingRequestListView, self).dispatch(*args, **kwargs)

  def get_context_data(self, **kwargs):
    context = super(TrainingRequestListView, self).get_context_data(**kwargs)
    context['role'] = self.role
    context['status'] = self.status
    context['header'] = self.header
    context['ordering'] = get_field_index(self.raw_get_data)
    return context
