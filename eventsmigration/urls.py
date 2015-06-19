from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^participants/$', 'eventsmigration.views.participants', name="participants"),
    url(r'^course-map/$', 'eventsmigration.views.course_map', name="course_map"),
    url(r'^training-planner/$', 'eventsmigration.views.training_planner', name="training_planner"),
    url(r'^attendance/$', 'eventsmigration.views.attendance', name="attendance"),
    url(r'^school-training/$', 'eventsmigration.views.school_training', name="school_training"),
)
