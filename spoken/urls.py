# Third Party Stuff
import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from . import views as spoken_views

urlpatterns = [
    url(r'^$', spoken_views.home, name='home'),

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^sitemap\.xml$', TemplateView.as_view(template_name='sitemap.xml', content_type='text/xml')),
    url(r'^sitemap\.html$', spoken_views.sitemap, name='sitemap'),

    url(r'^addu/$', 'spoken.views.add_user', name='addu'),
    url(r'^tutorial-search/$', 'spoken.views.tutorial_search', name="tutorial-search"),
    url(r'^news/(?P<cslug>[\w-]+)/$', 'spoken.views.news', name="news"),
    url(r'^news/(?P<cslug>[\w-]+)/(?P<slug>[\w-]+)/$', 'spoken.views.news_view', name="news_view"),
    url(r'^keyword-search/$', 'spoken.views.keyword_search', name="keyword-search"),
    url(r'^watch/([0-9a-zA-Z-+%\(\) ]+)/([0-9a-zA-Z-+%\(\) ]+)/([a-zA-Z-]+)/$',
        'spoken.views.watch_tutorial', name="watch_tutorial"),
    url(r'^get-language/$', 'spoken.views.get_language', name="get_language"),
    url(r'^testimonials/$', 'spoken.views.testimonials', name="testimonials"),
    url(r'^testimonials/new/$', 'spoken.views.testimonials_new', name="testimonials_new"),
    url(r'^admin/testimonials/$', 'spoken.views.admin_testimonials', name="admin_testimonials"),
    url(r'^admin/testimonials/(?P<rid>\d+)/edit/$',
        'spoken.views.admin_testimonials_edit', name="admin_testimonials_edit"),
    url(r'^admin/testimonials/(?P<rid>\d+)/delete/$',
        'spoken.views.admin_testimonials_delete', name="admin_testimonials_delete"),
    url(r'^site-feedback/$', 'spoken.views.site_feedback', name='site_feedback'),
    # url(r'^spoken/', include('spoken.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # evens old url
    url(r'^workshops/college/view_college/(\d+)/$', 'workshop.views.view_college', name='view_college'),
    url(r'^workshops/resource_center_view_college/(\d+)/$',
        'workshop.views.view_college', name='view_college'),
    url(r'^resource_center_view_college_map_details/(\d+)/$',
        'workshop.views.view_college', name='view_college'),
    # url(r'^software-training/academic-center/(\d+)/([a-zA-Z-]+)/$', 'workshop.views.view_college',
    #     name='view_college'),
    url(r'^completed_workshops_list/(?P<state_code>[\w-]+)/$',
        'workshop.views.training_list', name='training_list'),
    url(r'^view_completed_workshop/(\d+)/$', 'workshop.views.view_training', name='view_training'),
    url(r'^feedback_list/(?P<code>.+)/$', 'workshop.views.training_feedback', name='training_feedback'),
    url(r'^feedback_view/(?P<code>.+)/(?P<user_id>.+)/$',
        'workshop.views.view_training_feedback', name='view_training_feedback'),
    url(r'^workshops/academic_details/$', 'workshop.views.academic_details', name='academic_details'),
    url(r'^workshops/academic_details/(?P<state>.+)/$',
        'workshop.views.academic_details_state', name='academic_details_state'),
    url(r'^resource_center_map_details/(?P<state>.+)/$',
        'workshop.views.academic_details_state', name='academic_details_state'),
    url(r'^workshops/resource_center_details/$', 'workshop.views.view_college', name='view_college'),
    # url(r'^statistics/training/$', 'workshop.views.statistics_training', name='statistics_training'),

    # events urls
    url(r'^software-training/', include('events.urls', namespace='events')),
    url(r'^participant/', include('mdldjango.urls', namespace='mdldjango')),
    url(r'^cdcontent/', include('cdcontent.urls', namespace='cdcontent')),
    url(r'^create_cd_content/', include('cdcontent.urls', namespace='cdcontent')),
    url(r'^statistics/', include('statistics.urls', namespace='statistics')),

    # team
    url(r'^team/', include('team.urls')),

    url(r'^creation/', include('creation.urls', namespace='creation')),
    url(r'^nicedit/', include('nicedit.urls')),
    # url(r'^migration/creation/', include('creationmigrate.urls', namespace='creationmigrate')),
    # url(r'^migration/events/', include('eventsmigration.urls', namespace='eventsmigration')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),

    # Old url adjustments
    url(r'^list_videos/$', 'cdeep.views.list_videos', name='list_videos'),
    url(r'^show_video/$', 'cdeep.views.show_video', name='show_video'),
    url(r'^search/node/([0-9a-zA-Z-+%\(\)]+)/$', 'cdeep.views.search_node', name='search_node'),

    # Masquerade user
    url(r'^masquerade/', include('masquerade.urls', namespace='masquerade')),

    # Cron links
    url(r'^cron/subtitle-files/create/$', 'spoken.views.create_subtitle_files', name='create_subtitle_files'),

    # reports
    url(r'^report_builder/', include('report_builder.urls')),

    # Youtube API V3
    url(r'^youtube/', include('youtube.urls', namespace='youtube')),

    # reports
    url(r'^reports/', include('reports.urls', namespace='reports')),

    # events2
    # url(r'^events2/', include('events2.urls', namespace='events2')),

    # cms
    url(r'^', include('cms.urls', namespace='cms')),
]
