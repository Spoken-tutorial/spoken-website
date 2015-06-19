# urls.py
from django.conf.urls import url
from events2.views import *
from events2.decorators import *
from events2.forms import *
urlpatterns = [
    url(
      r'^training-planner/', 
      TrainingPlannerListView.as_view(template_name="training_planner.html"), 
      name="training_planner"
    ),
    url(
      r'^student-batch/new', 
      StudentBatchCreateView.as_view(template_name="new_batch.html", \
        form_class=StudentBatchForm), 
      name="add_batch"
    ),
    url(
      r'^student-batch/(?P<bid>\d+)/new', 
      StudentBatchCreateView.as_view(template_name="update_batch.html", \
        form_class=NewStudentBatchForm), 
      name="add_student"
    ),
    url(
      r'^student-batch/(?P<bid>\d+)/view', 
      StudentListView.as_view(template_name="list_student.html"), 
      name="list_student"
    ),
    url(
      r'^student-batch', 
      StudentBatchListView.as_view(template_name="student_batch_list.html"), 
      name="batch_list"
    ),
    url(
      r'^(?P<tpid>\d+)/training-request', 
      TrainingRequestCreateView.as_view(template_name="training_request.html"), 
      name="training_request"
    ),
    url(
      r'^(?P<tid>\d+)/attendance', 
      TrainingAttendanceListView.as_view(template_name=\
        "training_attendance.html"), 
      name="training_attendance"
    ),
    url(
      r'^training-request/(?P<trid>\d+)/$', 
      TrainingRequestEditView.as_view(template_name=\
        "edit_training_request.html"), 
      name="edit_training_request"
    ),
    url(
      r'^(?P<bid>\d+)/student-delete/(?P<pk>\d+)/$', 
      StudentDeleteView.as_view(template_name="student_delete.html", \
        success_url="/events2/student-batch"), 
      name="student_delete"
    ),

    #ajax
    url(
      r'^save-student/', 
      SaveStudentView.as_view()
    ),
    url(
      r'^get-course-option/', 
      GetCourseOptionView.as_view()
    ),
    url(
      r'^get-batch-option/', 
      GetBatchOptionView.as_view()
    ),
    #url(r'^get-language-option/', GetLanguageOptionView.as_view()),
]
