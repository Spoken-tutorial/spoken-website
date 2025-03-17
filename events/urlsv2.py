# urls.py
from django.urls import re_path
from events.viewsv2 import *
from events.decorators import *
from events.formsv2 import *
from events.urls import *
from .viewsv2 import *

app_name = 'eventsv2'
urlpatterns = [
    re_path(
      r'^training-planner/', 
      TrainingPlannerListView.as_view(template_name="training_planner.html"), 
      name="training_planner"
    ),
    re_path(
      r'^select-participants/', 
      TrainingPlannerListView.as_view(template_name="select_participants.html"), 
      name="select_participants"
    ),
    re_path(
      r'^student-batch/new/$', 
      StudentBatchCreateView.as_view(template_name="new_batch.html", \
        form_class=StudentBatchForm), 
      name="add_batch"
    ),
    re_path(
      r'^student-batch/(?P<bid>\d+)/new/$', 
      StudentBatchCreateView.as_view(template_name="update_batch.html", \
        form_class=NewStudentBatchForm), 
      name="add_student"
    ),
    re_path(
      r'^student-batch/(?P<pk>\d+)/$', 
      StudentBatchUpdateView.as_view(template_name="edit_batch.html", \
        form_class=UpdateStudentBatchForm), 
      name="edit_batch"
    ),
    re_path(
      r'^student-batch/edit/(?P<pk>\d+)/$', 
      StudentBatchYearUpdateView.as_view(template_name="edit_batch_year.html", \
        form_class=UpdateStudentYearBatchForm), 
      name="edit_year"
    ),
    re_path(
      r'^student-batch/(?P<bid>\d+)/view/$', 
      StudentListView.as_view(template_name="list_student.html"), 
      name="list_student"
    ),
    re_path(
      r'^student-batch/$', 
      StudentBatchListView.as_view(template_name="student_batch_list.html"), 
      name="batch_list"
    ),
    re_path(
      r'^(?P<tpid>\d+)/training-request', 
      TrainingRequestCreateView.as_view(template_name="training_request.html"), 
      name="training_request"
    ),
    re_path(
      r'^(?P<tid>\d+)/attendance', 
      TrainingAttendanceListView.as_view(template_name=\
        "training_attendance.html"), 
      name="training_attendance"
    ),
    re_path(
      r'^(?P<tid>\d+)/certificate', 
      TrainingCertificateListView.as_view(template_name=\
        "training_certificate.html"), 
      name="training_certificate"
    ),
    re_path(
      r'^training-request/(?P<pk>\d+)/$',
      TrainingRequestEditView.as_view(template_name=\
        "edit_training_request.html"), 
      name="edit_training_request"
    ),
    re_path(
      r'^(?P<bid>\d+)/student-delete/(?P<pk>\d+)/$', 
      StudentMasterDeleteView.as_view(template_name="student_delete_masterbatch.html", \
        success_url="/software-training/student-batch"), 
      name="student_delete"
    ),
    re_path(
      r'^training-certificate/(?P<taid>\d+)/organiser/$', 
      OrganiserTrainingCertificateView.as_view(), \
        name="organiser_training_certificate"
    ),
    re_path(
      r'^training-certificate/(?P<taid>\d+)/student/$', 
      StudentTrainingCertificateView.as_view(), \
        name="student_training_certificate"
    ),
    re_path(
      r'^course-map-list/$', 
      CourseMapListView.as_view(template_name="coursemap_list.html"), 
      name="coursemaplist"
    ),
    re_path(
      r'^course-map/(?P<pk>\d+)$', 
      CourseMapUpdateView.as_view(template_name=\
        "coursemap.html"), 
      name="coursemapupdate"
    ),
#    re_path(
#      r'^single-training/pending/$', 
#     SingleTrainingNewListView.as_view(template_name="single-training.html"), 
#      name="single-training-pending"
#    ),
#    re_path(
#      r'^single-training/approved/$', 
#     SingletrainingApprovedListView.as_view(template_name="single-training.html"), 
#      name="single-training-approved"
#    ),
#    re_path(
#      r'^single-training/rejected/$', 
#     SingletrainingRejectedListView.as_view(template_name="single-training.html"), 
#      name="single-training-rejected"
#    ),
#    re_path(
#      r'^single-training/ongoing/$', 
#     SingletrainingOngoingListView.as_view(template_name="single-training.html"), 
#      name="single-training-ongoing"
#    ),
#    re_path(
#      r'^single-training/pendingattendance/$', 
#     SingletrainingPendingAttendanceListView.as_view(template_name="single-training.html"), 
#      name="single-training-pendingattendance"
#    ),
#    re_path(
#      r'^single-training/completed/$', 
#     SingletrainingCompletedListView.as_view(template_name="single-training.html"), 
#      name="single-training-completed"
#    ),
    # re_path(
    #   r'^single-training/new/$', 
    #  SingletrainingCreateView.as_view(template_name="single-training-form.html"), 
    #   name="new-single-training"
    # ),
    re_path(
      r'^single-training/(?P<pk>\d+)/edit/$',
     SingletrainingUpdateView.as_view(template_name="single-training-form.html"),
      name="update-single-training"
    ),
    re_path(
      r'^single-training/(?P<status>\w+)/$', 
     SingleTrainingListView.as_view(template_name="single-training.html"), 
      name="single-training-list"
    ),
    re_path(
      r'^single-training/(?P<pk>\d+)/complete/$',
     SingletrainingMarkCompleteUpdateView.as_view(template_name=""),
      name="markcomplete-single-training"
    ),
    re_path(
      r'^single-training/(?P<tid>\d+)/certificate', 
      SingleTrainingCertificateListView.as_view(template_name=\
        "single-training-certificate.html"), 
      name="single-training-certificate"
    ),
    re_path(
      r'^single-training-certificate/(?P<taid>\d+)/organiser/$', 
      OrganiserSingleTrainingCertificateView.as_view(), \
        name="organiser_singletraining_certificate"
    ),
    #ajax
    re_path(
      r'^save-student/', 
      SaveStudentView.as_view()
    ),
    # re_path(
    #   r'^get-course-option/', 
    #   GetCourseOptionView.as_view()
    # ),
    re_path(
      r'^get-batch-option/', 
      GetBatchOptionView.as_view()
    ),
    re_path(
      r'^get-course-option/', 
      GetCourseOptionView.as_view()
    ),
    re_path(
      r'^get-batch-course-status/', 
      GetBatchStatusView.as_view()
    ),
    re_path(
      r'^get-department-organiser-status/', 
      GetDepartmentOrganiserStatusView.as_view()
    ),
    # re_path(
    #   r'^training-request/(?P<role>\w+)/(?P<status>\w+)/$', 
    #   TrainingRequestListView.as_view(template_name='training_list.html'), 
    #   name='training_list'
    # ),
    #re_path(r'^get-language-option/', GetLanguageOptionView.as_view()),
    re_path(
      r'^single-training/pending/(?P<pk>\d+)/approve/$',
       SingleTrainingApprove, 
      name="single-training-approve"
    ),
    re_path(
      r'^single-training/pending/(?P<pk>\d+)/reject/$', 
       SingleTrainingReject, 
      name="single-training-reject"
    ),
    re_path(
      r'^single-training/pending/(?P<pk>\d+)/requestmarkattendance/$', 
       SingleTrainingPendingAttendance, 
      name="single_training_pending"
    ),
    re_path(
      r'^markas/(?P<pk>\d+)/complete/$', 
       MarkAsComplete, 
      name="mark_as_complete"
    ),
    re_path(
      r'^mark/(?P<pk>\d+)/complete/$', 
       MarkComplete, 
      name="mark_complete"
    ),
    re_path(
      r'^single-training/(?P<tid>\d+)/attendance', 
      SingleTrainingAttendanceListView.as_view(template_name=\
        "single-training-attendance.html"), 
      name="single_training_attendance"
     ),
     re_path(
      r'^organiser-feedback/', 
      OrganiserFeedbackCreateView.as_view(template_name='organiser_feedback.html'), 
      name='organiser_feedback'
    ),
    re_path(
      r'^organiser-feedback-display/$', 
     OrganiserFeedbackListView.as_view(template_name="organiser_feedback_display.html"), 
      name="organiser-feedback-display"
    ),
    re_path(
      r'^old-training/$',
      OldTrainingListView.as_view(template_name=\
        "old_training.html"),
      name="old_training"
    ),
    re_path(
      r'^old-training/(?P<tid>\d+)/participant/$',
      OldStudentListView.as_view(template_name="old_list_student.html"), 
      name="old_list_student"
    ),
    re_path(
      r'^old-training/(?P<tid>\d+)/close/$',
      OldTrainingCloseView.as_view(template_name=""), 
      name="old_training_close"
    ),
    re_path(
       r'^latex_workshop/$',
        LatexWorkshopFileUpload,
       name="latex-workshop"
       ),
    re_path(
       r'^student-batch/(?P<bid>\d+)/view/(?P<pk>\d+)$',
       UpdateStudentName.as_view(template_name="update_student.html"),
       name="update_student"
       ),
    re_path(
      r'^stworkshop-feedback/', 
      STWorkshopFeedbackCreateView.as_view(template_name='stworkshop_feedback.html'), 
      name='stworkshop_feedback'
    ),
    re_path(
      r'^stworkshop-feedback-pre/', 
      STWorkshopFeedbackPreCreateView.as_view(template_name='stworkshop_feedback_pre.html'), 
      name='stworkshop_feedback_pre'
    ),
    re_path(
      r'^stworkshop-feedback-post/', 
      STWorkshopFeedbackPostCreateView.as_view(template_name='stworkshop_feedback_post.html'), 
      name='stworkshop_feedback_post'
    ),
    re_path(
      r'^learn-drupal-feedback/', 
      LearnDrupalFeedbackCreateView.as_view(template_name='learndrupalfeedback.html'), 
      name='learndrupalfeedback'
    ),
    re_path(
      r'^(?P<tid>\d+)/oldattendance', 
      TrainingAttendanceListView.as_view(template_name=\
        "mark_prev_attendance.html"), 
      name="previous_training_attendance"
    ),
    re_path(
      r'^(?P<pk>\d+)/reopen-training/$', 
       ReOpenTraining, 
      name="re-open-training"
    ),
    re_path(
      r'^payment-home/$', 
       payment_home, 
      name="payment_home"
    ),
      re_path(
      r'^payment-status/$', 
       payment_status, 
      name="payment_status"
    ),
      re_path(
      r'^payment-success/$', 
       payment_success, 
      name="payment_success"
    ),
    re_path(
      r'^payment-details/(?P<choice>\w+)/$', 
       payment_details, 
      name="payment_details"
    ),
    re_path(
      r'^payment-reconciliation-update/$', 
       payment_reconciliation_update, 
      name="payment_reconciliation_update"
    ),
    
    re_path(r'^academic-transactions/$', academic_transactions,name="payment"),
    re_path(
      r'^training-request/(?P<role>\w+)/(?P<status>\w+)/$', 
      trainingrequest, 
      name='training_list'
    ),
    re_path(
      r'^request/(?P<trid>\d+)/certificate/$', 
      RequestCertificate, 
      name="request_certificate"
    ),

    re_path(
      r'^certificate-request/(?P<role>\w+)/(?P<choice>\w+)/$', 
      CertificateRequest, 
      name='certificate_request_list'
    ),
    re_path(
      r'^generate/(?P<trid>\d+)/certificate/$', 
      GenerateCertificate, 
      name="generate_certificate"
    ),
    re_path(
      r'^training-certificate/(?P<trid>\d+)/allcertificates/$', 
      AllTrainingCertificateView.as_view(), \
        name="alltraining_certificate"
    ),
    re_path(
      r'^student-grade-filter/$',
      StudentGradeFilter.as_view(),
      name="student_grade_filter"
    ),
    re_path(
      r'^academic_payment_details/', 
      AcademicKeyCreateView.as_view(template_name='academic_payment_details_form.html'), 
      name='academic_payment_details'
    ),
    re_path(
      # r'^software-training/ajax-academic-details/', 
      r'^ajax-academic-details/', 
      FetchAcademicDetailsView.as_view(), 
      name='ajax_academic_details'
    ),


]
