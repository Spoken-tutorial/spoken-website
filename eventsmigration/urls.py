from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^resource-person/$', 'eventsmigration.views.resource_person', name="resource_person"),
    url(r'^states/$', 'eventsmigration.views.states', name="states"),
    url(r'^academic-center/$', 'eventsmigration.views.academic_center', name="academic_center"),
    url(r'^organiser/$', 'eventsmigration.views.organiser', name="organiser"),
    url(r'^invigilator/$', 'eventsmigration.views.invigilator', name="invigilator"),
    url(r'^workshop/$', 'eventsmigration.views.workshop', name="workshop"),
    url(r'^department/$', 'eventsmigration.views.department', name="department"),
    url(r'^workshop-feedback/$', 'eventsmigration.views.workshop_feedback', name="workshop_feedback"),
    url(r'^test/$', 'eventsmigration.views.test', name="test"),
    url(r'^test-attendance/$', 'eventsmigration.views.test_attendance', name="test_attendance"),
    url(r'^testimonials/$', 'eventsmigration.views.testimonials', name="testimonials"),
    url(r'^articles/$', 'eventsmigration.views.articles', name="articles"),
)
