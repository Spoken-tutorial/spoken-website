# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Third Party Stuff
from django.conf.urls import url

# Spoken Tutorial Stuff
from events.decorators import *
from events.formsv2 import *
from events.urls import *
from events.viewsv2 import *

urlpatterns = [
    url(
        r'^training-planner/',
        TrainingPlannerListView.as_view(template_name="training_planner.html"),
        name="training_planner"
    ),
    url(
        r'^select-participants/',
        TrainingPlannerListView.as_view(template_name="select_participants.html"),
        name="select_participants"
    ),
    url(
        r'^student-batch/new/$',
        StudentBatchCreateView.as_view(template_name="new_batch.html",
                                       form_class=StudentBatchForm),
        name="add_batch"
    ),
    url(
        r'^student-batch/(?P<bid>\d+)/new/$',
        StudentBatchCreateView.as_view(template_name="update_batch.html",
                                       form_class=NewStudentBatchForm),
        name="add_student"
    ),
    url(
        r'^student-batch/(?P<pk>\d+)/$',
        StudentBatchUpdateView.as_view(template_name="edit_batch.html",
                                       form_class=UpdateStudentBatchForm),
        name="edit_student"
    ),
    url(
        r'^student-batch/edit/(?P<pk>\d+)/$',
        StudentBatchYearUpdateView.as_view(template_name="edit_batch_year.html",
                                           form_class=UpdateStudentYearBatchForm),
        name="edit_year"
    ),
    url(
        r'^student-batch/(?P<bid>\d+)/view/$',
        StudentListView.as_view(template_name="list_student.html"),
        name="list_student"
    ),
    url(
        r'^student-batch/$',
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
        TrainingAttendanceListView.as_view(template_name="training_attendance.html"),
        name="training_attendance"
    ),
    url(
        r'^(?P<tid>\d+)/certificate',
        TrainingCertificateListView.as_view(template_name="training_certificate.html"),
        name="training_certificate"
    ),
    url(
        r'^training-request/(?P<trid>\d+)/$',
        TrainingRequestEditView.as_view(template_name="edit_training_request.html"),
        name="edit_training_request"
    ),
    url(
        r'^(?P<bid>\d+)/student-delete/(?P<pk>\d+)/$',
        StudentDeleteView.as_view(template_name="student_delete.html",
                                  success_url="/software-training/student-batch"),
        name="student_delete"
    ),
    url(
        r'^training-certificate/(?P<taid>\d+)/organiser/$',
        OrganiserTrainingCertificateView.as_view(),
        name="organiser_training_certificate"
    ),
    url(
        r'^training-certificate/(?P<taid>\d+)/student/$',
        StudentTrainingCertificateView.as_view(),
        name="student_training_certificate"
    ),
    url(
        r'^course-map-list/$',
        CourseMapListView.as_view(template_name="coursemap_list.html"),
        name="coursemaplist"
    ),
    url(
        r'^course-map/(?P<pk>\d+)$',
        CourseMapUpdateView.as_view(template_name="coursemap.html"),
        name="coursemapupdate"
    ),
    #    url(
    #      r'^single-training/pending/$',
    #     SingleTrainingNewListView.as_view(template_name="single-training.html"),
    #      name="single-training-pending"
    #    ),
    #    url(
    #      r'^single-training/approved/$',
    #     SingletrainingApprovedListView.as_view(template_name="single-training.html"),
    #      name="single-training-approved"
    #    ),
    #    url(
    #      r'^single-training/rejected/$',
    #     SingletrainingRejectedListView.as_view(template_name="single-training.html"),
    #      name="single-training-rejected"
    #    ),
    #    url(
    #      r'^single-training/ongoing/$',
    #     SingletrainingOngoingListView.as_view(template_name="single-training.html"),
    #      name="single-training-ongoing"
    #    ),
    #    url(
    #      r'^single-training/pendingattendance/$',
    #     SingletrainingPendingAttendanceListView.as_view(template_name="single-training.html"),
    #      name="single-training-pendingattendance"
    #    ),
    #    url(
    #      r'^single-training/completed/$',
    #     SingletrainingCompletedListView.as_view(template_name="single-training.html"),
    #      name="single-training-completed"
    #    ),
    url(
        r'^single-training/new/$',
        SingletrainingCreateView.as_view(template_name="single-training-form.html"),
        name="new-single-training"
    ),
    url(
        r'^single-training/(?P<pk>\d+)/edit/$',
        SingletrainingUpdateView.as_view(template_name="single-training-form.html"),
        name="update-single-training"
    ),
    url(
        r'^single-training/(?P<status>\w+)/$',
        SingleTrainingListView.as_view(template_name="single-training.html"),
        name="single-training-list"
    ),
    url(
        r'^single-training/(?P<pk>\d+)/complete/$',
        SingletrainingMarkCompleteUpdateView.as_view(template_name=""),
        name="markcomplete-single-training"
    ),
    url(
        r'^single-training/(?P<tid>\d+)/certificate',
        SingleTrainingCertificateListView.as_view(template_name="single-training-certificate.html"),
        name="single-training-certificate"
    ),
    url(
        r'^single-training-certificate/(?P<taid>\d+)/organiser/$',
        OrganiserSingleTrainingCertificateView.as_view(), \
        name="organiser_singletraining_certificate"
    ),
    # ajax
    url(r'^save-student/', SaveStudentView.as_view()),
    url(r'^get-course-option/', GetCourseOptionView.as_view()),
    url(r'^get-batch-option/', GetBatchOptionView.as_view()),
    url(r'^get-batch-course-status/', GetBatchStatusView.as_view()),
    url(
        r'^training-request/(?P<role>\w+)/(?P<status>\w+)/$',
        TrainingRequestListView.as_view(template_name='training_list.html'),
        name='training_list'
    ),
    # url(r'^get-language-option/', GetLanguageOptionView.as_view()),
    url(
        r'^single-training/pending/(?P<pk>\d+)/approve/$',
        'events.viewsv2.SingleTrainingApprove',
        name="single-training-approve"
    ),
    url(
        r'^single-training/pending/(?P<pk>\d+)/reject/$',
        'events.viewsv2.SingleTrainingReject',
        name="single-training-reject"
    ),
    url(
        r'^single-training/pending/(?P<pk>\d+)/requestmarkattendance/$',
        'events.viewsv2.SingleTrainingPendingAttendance',
        name="single_training_pending"
    ),
    url(
        r'^markas/(?P<pk>\d+)/complete/$',
        'events.viewsv2.MarkAsComplete',
        name="mark_as_complete"
    ),
    url(
        r'^mark/(?P<pk>\d+)/complete/$',
        'events.viewsv2.MarkComplete',
        name="mark_complete"
    ),
    url(
        r'^single-training/(?P<tid>\d+)/attendance',
        SingleTrainingAttendanceListView.as_view(template_name="single-training-attendance.html"),
        name="single_training_attendance"
    ),
    url(
        r'^organiser-feedback/',
        OrganiserFeedbackCreateView.as_view(template_name='organiser_feedback.html'),
        name='organiser_feedback'
    ),
    url(
        r'^organiser-feedback-display/$',
        OrganiserFeedbackListView.as_view(template_name="organiser_feedback_display.html"),
        name="organiser-feedback-display"
    ),
    url(
        r'^old-training/$',
        OldTrainingListView.as_view(template_name="old_training.html"),
        name="old_training"
    ),
    url(
        r'^old-training/(?P<tid>\d+)/participant/$',
        OldStudentListView.as_view(template_name="old_list_student.html"),
        name="old_list_student"
    ),
    url(
        r'^old-training/(?P<tid>\d+)/close/$',
        OldTrainingCloseView.as_view(template_name=""),
        name="old_training_close"
    ),
    url(
        r'^latex_workshop/$',
        'events.viewsv2.LatexWorkshopFileUpload',
        name="latex-workshop"
    ),
    url(
        r'^student-batch/(?P<bid>\d+)/view/(?P<pk>\d+)$',
        UpdateStudentName.as_view(template_name="update_student.html"),
        name="update_student"
    ),
]
