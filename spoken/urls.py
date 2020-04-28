
# Third Party Stuff
from . import settings

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from spoken.views import *
from workshop.views import *
from cdeep.views import *
from django.conf import settings
from django.conf.urls.static import static


app_name = 'spoken'
admin.autodiscover()

urlpatterns = [
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    #url(r'^sitemap\.xml$', TemplateView.as_view(template_name='sitemap.xml', content_type='text/xml')),
    url(r'^sitemap\.html$', sitemap, name='sitemap'),
    # Examples:
    url(r'^addu/$', add_user, name='addu'),
    # url(r'^NMEICT-Intro/$', nmeict_intro, name="nmeict_intro"),
    url(r'^tutorial-search/$', tutorial_search, name="tutorial-search"),
    url(r'^series/$', series_foss, name="series"),
    url(r'^series_tutorial-search/$',  series_tutorial_search, name="series-tutorial-search"),
    url(r'^archived/$', archived_foss, name="archived"),
    url(r'^archived_tutorial-search/$',  archived_tutorial_search, name="archived-tutorial-search"),
    url(r'^news/(?P<cslug>[\w-]+)/$',  news, name="news"),
    url(r'^news/(?P<cslug>[\w-]+)/(?P<slug>[\w-]+)/$',  news_view, name="news_view"),
    url(r'^keyword-search/$',  keyword_search, name="keyword-search"),
    url(r'^watch/([0-9a-zA-Z-+%\(\)., ]+)/([0-9a-zA-Z-+%\(\)., ]+)/([a-zA-Z-]+)/$',  watch_tutorial, name="watch_tutorial"),
    url(r'^What_is_a_Spoken_Tutorial/$',  what_is_spoken_tutorial, name="what_is_spoken_tutorial"),
    url(r'^get-language/(?P<tutorial_type>[\w-]+)/$',  get_language, name="get_language"),
    url(r'^testimonials/new/$',  testimonials_new, name="testimonials_new"),
    url(r'^testimonials/$',  testimonials, name="testimonials"),
    url(r'^testimonials/(?P<testimonial_type>[\w]+)/$',  testimonials, name="testimonials"),
    url(r'^testimonials/media/(?P<foss>[\w ]+)/$',  foss_testimonials, name="foss_testimonials"),

    url(r'^admin/testimonials/$',  admin_testimonials, name="admin_testimonials"),
    url(r'^admin/testimonials/(?P<rid>\d+)/edit/$',  admin_testimonials_edit, name="admin_testimonials_edit"),
    url(r'^testimonials/new/media/(?P<testimonial_type>[\w]+)/$',  testimonials_new_media, name="testimonials_new_media"),
    url(r'^admin/testimonials/(?P<rid>\d+)/delete/$',  admin_testimonials_delete, name="admin_testimonials_delete"),
    url(r'^admin/testimonials/media/(?P<rid>\d+)/delete/$',  admin_testimonials_media_delete,name="admin_testimonials_media_delete"),
    url(r'^brochures/$',  ViewBrochures, name="view_brochures"),
    url(r'^$',  home, name='home'),
    url(r'^home/$',  home, name='home'),
    url(r'^site-feedback/$',  site_feedback, name='site_feedback'),
    url(r'^learn-Drupal/$',  learndrupal, name='learndrupal'),
    # url(r'^learn-Drupal./$',  learndrupal', name='learndrupal'),
    # url(r'^induction_old/$',  induction_2017', name='induction_2017'),
    url(r'^induction/$',  induction_2017_new, name='induction_2017_new'),
    # url(r'^induction/expression_of_intrest/$',  expression_of_intrest', name='expression_of_intrest'),
    url(r'^induction/expression_of_intrest/$',  expression_of_intrest, name='expression_of_intrest'),
    url(r'^induction/eoi/$',  expression_of_intrest_new, name='expression_of_intrest_new'),
    url(r'^admin/testimonials/media/(?P<rid>\d+)/edit/$', admin_testimonials_media_edit, name="admin_testimonials_media_edit"),

        # url(r'^spoken/', include('spoken.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # evens old url
    url(r'^workshops/college/view_college/(\d+)/$',  view_college, name='view_college'),
    url(r'^workshops/resource_center_view_college/(\d+)/$',  view_college, name='view_college'),
    url(r'^resource_center_view_college_map_details/(\d+)/$',  view_college, name='view_college'),
    # url(r'^software-training/academic-center/(\d+)/([a-zA-Z-]+)/$',  view_college', name='view_college'),
    url(r'^completed_workshops_list/(?P<state_code>[\w-]+)/$',  training_list, name='training_list'),
    url(r'^view_completed_workshop/(\d+)/$',  view_training, name='view_training'),
    url(r'^feedback_list/(?P<code>.+)/$',  training_feedback, name='training_feedback'),
    url(r'^feedback_view/(?P<code>.+)/(?P<user_id>.+)/$',  view_training_feedback, name='view_training_feedback'),
    url(r'^workshops/academic_details/$',  academic_details, name='academic_details'),
    url(r'^workshops/academic_details/(?P<state>.+)/$',  academic_details_state, name='academic_details_state'),
    url(r'^resource_center_map_details/(?P<state>.+)/$',  academic_details_state, name='academic_details_state'),
    url(r'^workshops/resource_center_details/$',  view_college, name='view_college'),
    # url(r'^statistics/training/$',  statistics_training', name='statistics_training'),

    # events urls
    url(r'^software-training/', include('events.urls', namespace='events')),
    url(r'^software-training/', include('events.urlsv2', namespace='eventsv2')),

    url(r'^participant/', include('mdldjango.urls', namespace='mdldjango')),
    url(r'^cdcontent/', include('cdcontent.urls', namespace='cdcontent')),
    url(r'^create_cd_content/', include('cdcontent.urls', namespace='cdcontent')),
    url(r'^statistics/', include('statistics.urls', namespace='statistics')),
    url(r'^list_videos/$',  list_videos, name='list_videos'),
    # team
    url(r'^team/', include('team.urls')),

    #api
    url(r'^api/', include('api.urls', namespace='api')),

    # certificate
    url(r'^certificate/', include('certificate.urls', namespace='certificate')),

    url(r'^creation/', include('creation.urls', namespace='creation')),
    url(r'^nicedit/', include('nicedit.urls')),
    # url(r'^migration/creation/', include('creationmigrate.urls', namespace='creationmigrate')),
    # url(r'^migration/events/', include('eventsmigration.urls', namespace='eventsmigration')),
    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),

    # Old url adjustments
    # url(r'^list_videos/$',  list_videos', name='list_videos'),
    url(r'^show_video/$',  show_video, name='show_video'),
    url(r'^search/node/([0-9a-zA-Z-+%\(\)]+)/$',  search_node, name='search_node'),

    # Masquerade user
    # url(r'^masquerade/', include('masquerade.urls', namespace='masquerade')),
    url(r'^masquerade/', include('impersonate.urls', namespace='impersonate')),
    # Cron links
    url(r'^cron/subtitle-files/create/$',  create_subtitle_files, name='create_subtitle_files'),

    # reports
    url(r'^report_builder/', include('report_builder.urls')),

    # Youtube API V3
    url(r'^youtube/', include('youtube.urls', namespace='youtube')),

    # reports
    url(r'^reports/', include('reports.urls', namespace='reports')),

    # events2
    # url(r'^events2/', include('events2.urls', namespace='events2')),
    url(r'^cron/', include('cron.urls', namespace='cron')),

    # cms
    url(r'^', include('cms.urls', namespace='cms')),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
