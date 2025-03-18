
# Third Party Stuff
from . import settings

from django.urls import path, re_path, include
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
    re_path(r'^robots\.txt', robots_txt, name='robots-txt'),
    #re_path(r'^sitemap\.xml$', TemplateView.as_view(template_name='sitemap.xml', content_type='text/xml')),
    re_path(r'^sitemap\.html$', sitemap, name='sitemap'),
    # Examples:
    re_path(r'^addu/$', add_user, name='addu'),
    # re_path(r'^NMEICT-Intro/$', nmeict_intro, name="nmeict_intro"),
    re_path(r'^tutorial-search/$', tutorial_search, name="tutorial-search"),
    re_path(r'^series/$', series_foss, name="series"),
    re_path(r'^series_tutorial-search/$',  series_tutorial_search, name="series-tutorial-search"),
    re_path(r'^archived/$', archived_foss, name="archived"),
    re_path(r'^archived_tutorial-search/$',  archived_tutorial_search, name="archived-tutorial-search"),
    re_path(r'^news/(?P<cslug>[\w-]+)/$',  news, name="news"),
    re_path(r'^news/(?P<cslug>[\w-]+)/(?P<slug>[\w-]+)/$',  news_view, name="news_view"),
    re_path(r'^keyword-search/$',  keyword_search, name="keyword-search"),
    re_path(r'^watch/([0-9a-zA-Z-+%\(\).,\' ]+)/([0-9a-zA-Z-+%\(\).,\' ]+)/([a-zA-Z-]+)/$',  watch_tutorial, name="watch_tutorial"),
    re_path(r'^What_is_a_Spoken_Tutorial/$',  what_is_spoken_tutorial, name="what_is_spoken_tutorial"),
    re_path(r'^get-language/(?P<tutorial_type>[\w-]+)/$',  get_language, name="get_language"),
    re_path(r'^testimonials/new/$',  testimonials_new, name="testimonials_new"),
    re_path(r'^testimonials/$',  testimonials, name="testimonials"),
    re_path(r'^testimonials/(?P<testimonial_type>[\w]+)/$',  testimonials, name="testimonials"),
    re_path(r'^testimonials/media/(?P<foss>[\w ]+)/$',  foss_testimonials, name="foss_testimonials"),

    re_path(r'^admin/testimonials/$',  admin_testimonials, name="admin_testimonials"),
    re_path(r'^admin/testimonials/(?P<rid>\d+)/edit/$',  admin_testimonials_edit, name="admin_testimonials_edit"),
    re_path(r'^testimonials/new/media/(?P<testimonial_type>[\w]+)/$',  testimonials_new_media, name="testimonials_new_media"),
    re_path(r'^admin/testimonials/(?P<rid>\d+)/delete/$',  admin_testimonials_delete, name="admin_testimonials_delete"),
    re_path(r'^admin/testimonials/media/(?P<rid>\d+)/delete/$',  admin_testimonials_media_delete,name="admin_testimonials_media_delete"),
    re_path(r'^brochures/$',  ViewBrochures, name="view_brochures"),
    re_path(r'^$',  home, name='home'),
    re_path(r'^home/$',  home, name='home'),
    re_path(r'^site-feedback/$',  site_feedback, name='site_feedback'),
    re_path(r'^learn-Drupal/$',  learndrupal, name='learndrupal'),
    # re_path(r'^learn-Drupal./$',  learndrupal', name='learndrupal'),
    # re_path(r'^induction_old/$',  induction_2017', name='induction_2017'),
    re_path(r'^induction/$',  induction_2017_new, name='induction_2017_new'),
    # re_path(r'^induction/expression_of_intrest/$',  expression_of_intrest', name='expression_of_intrest'),
    re_path(r'^induction/expression_of_intrest/$',  expression_of_intrest, name='expression_of_intrest'),
    re_path(r'^induction/eoi/$',  expression_of_intrest_new, name='expression_of_intrest_new'),
    re_path(r'^admin/testimonials/media/(?P<rid>\d+)/edit/$', admin_testimonials_media_edit, name="admin_testimonials_media_edit"),

        # re_path(r'^spoken/', include('spoken.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls),

    #subscription urls
    re_path(r'^payment/callback/$',  payment_callback, name="payment_callback"),
    re_path(r'^payment/status/(?P<order_id>[\w-]+)/$', check_payment_status, name="check_payment_status"),
    re_path(r'^payment/subscription/$',  subscription, name="initiate_payment"),

    # evens old url
    re_path(r'^workshops/college/view_college/(\d+)/$',  view_college, name='view_college'),
    re_path(r'^workshops/resource_center_view_college/(\d+)/$',  view_college, name='view_college'),
    re_path(r'^resource_center_view_college_map_details/(\d+)/$',  view_college, name='view_college'),
    # re_path(r'^software-training/academic-center/(\d+)/([a-zA-Z-]+)/$',  view_college', name='view_college'),
    re_path(r'^completed_workshops_list/(?P<state_code>[\w-]+)/$',  training_list, name='training_list'),
    re_path(r'^view_completed_workshop/(\d+)/$',  view_training, name='view_training'),
    re_path(r'^feedback_list/(?P<code>.+)/$',  training_feedback, name='training_feedback'),
    re_path(r'^feedback_view/(?P<code>.+)/(?P<user_id>.+)/$',  view_training_feedback, name='view_training_feedback'),
    re_path(r'^workshops/academic_details/$',  academic_details, name='academic_details'),
    re_path(r'^workshops/academic_details/(?P<state>.+)/$',  academic_details_state, name='academic_details_state'),
    re_path(r'^resource_center_map_details/(?P<state>.+)/$',  academic_details_state, name='academic_details_state'),
    re_path(r'^workshops/resource_center_details/$',  view_college, name='view_college'),
    # re_path(r'^statistics/training/$',  statistics_training', name='statistics_training'),

    # events urls
    re_path(r'^software-training/', include('events.urls', namespace='events')),
    re_path(r'^software-training/', include('events.urlsv2', namespace='eventsv2')),

    re_path(r'^participant/', include('mdldjango.urls', namespace='mdldjango')),
    re_path(r'^cdcontent/', include('cdcontent.urls', namespace='cdcontent')),
    re_path(r'^create_cd_content/', include('cdcontent.urls', namespace='cdcontent')),
    re_path(r'^statistics/', include('statistics.urls', namespace='statistics')),
    re_path(r'^list_videos/$',  list_videos, name='list_videos'),
    # team
    re_path(r'^team/', include('team.urls')),

    #api
    re_path(r'^api/', include('api.urls', namespace='api')),

    #training
    re_path(r'^training/', include('training.urls', namespace='training')),

    # certificate
    re_path(r'^certificate/', include('certificate.urls', namespace='certificate')),

    re_path(r'^creation/', include('creation.urls', namespace='creation')),
    # re_path(r'^migration/creation/', include('creationmigrate.urls', namespace='creationmigrate')),
    # re_path(r'^migration/events/', include('eventsmigration.urls', namespace='eventsmigration')),
    #re_path(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),

    # Old url adjustments
    # re_path(r'^list_videos/$',  list_videos', name='list_videos'),
    re_path(r'^show_video/$',  show_video, name='show_video'),
    re_path(r'^search/node/([0-9a-zA-Z-+%\(\)]+)/$',  search_node, name='search_node'),
    re_path(r'^saveVideoData/$',  saveVideoData, name='saveVideoData'),
    # Masquerade user
    # re_path(r'^masquerade/', include('masquerade.urls', namespace='masquerade')),
    re_path(r'^masquerade/', include(('impersonate.urls', 'impersonate'))),
    # Cron links
    re_path(r'^cron/subtitle-files/create/$',  create_subtitle_files, name='create_subtitle_files'),

    # reports
    # re_path(r'^report_builder/', include('report_builder.urls')),

    # Youtube API V3
    re_path(r'^youtube/', include('youtube.urls', namespace='youtube')),

    # reports
    re_path(r'^reports/', include('reports.urls', namespace='reports')),

    # events2
    # re_path(r'^events2/', include('events2.urls', namespace='events2')),
    re_path(r'^cron/', include('cron.urls')),

    #donation
    re_path(r'^donate/', include('donate.urls', namespace='donate')),

    # cms
    path(r'', include('cms.urls', namespace='cms')),
    
    #nep book fiar
    re_path(r'wbf-book-fair-2023', bookfair,name="bookfair"),
    
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
