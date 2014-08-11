from django.conf.urls import patterns, include, url
import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Examples:
    url(r'^tutorial-search/$', 'spoken.views.tutorial_search', name="tutorial-search"),
    url(r'^news/(?P<cslug>[\w-]+)/$', 'spoken.views.news', name="news"),
    url(r'^news/(?P<cslug>[\w-]+)/(?P<slug>[\w-]+)/$', 'spoken.views.news_view', name="news_view"),
    url(r'^keyword-search/$', 'spoken.views.keyword_search', name="keyword-search"),
    url(r'^watch/([0-9a-zA-Z-+%\(\)]+)/([0-9a-zA-Z-+%\(\)]+)/(\w+)/$', 'spoken.views.watch_tutorial', name="watch_tutorial"),
    url(r'^get-language/$', 'spoken.views.get_language', name="get_language"),
    url(r'^testimonials/$', 'spoken.views.testimonials', name="testimonials"),
    url(r'^testimonials/new/$', 'spoken.views.testimonials_new', name="testimonials_new"),
    url(r'^admin/testimonials/$', 'spoken.views.admin_testimonials', name="admin_testimonials"),
    url(r'^admin/testimonials/(?P<rid>\d+)/edit/$', 'spoken.views.admin_testimonials_edit', name="admin_testimonials_edit"),
    url(r'^admin/testimonials/(?P<rid>\d+)/delete/$', 'spoken.views.admin_testimonials_delete', name="admin_testimonials_delete"),
    url(r'^$', 'spoken.views.home', name='home'),
    url(r'^home/$', 'spoken.views.home', name='home'),
    url(r'^site-feedback/$', 'spoken.views.site_feedback', name='site_feedback'),
    # url(r'^spoken/', include('spoken.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #events urls
    url(r'^software-training/', include('events.urls', namespace='events')),
    url(r'^participant/', include('mdldjango.urls', namespace='mdldjango')),
    url(r'^cdcontent/', include('cdcontent.urls', namespace='cdcontent')),
    url(r'^create_cd_content/', include('cdcontent.urls', namespace='cdcontent')),
    url(r'^statistics/', include('statistics.urls', namespace='statistics')),
    url(r'^creation/', include('creation.urls', namespace='creation')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^nicedit/', include('nicedit.urls')),
    url(r'^migration/creation/', include('creationmigrate.urls', namespace='creationmigrate')),
    url(r'^migration/events/', include('eventsmigration.urls', namespace='eventsmigration')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':False}),
    #cms
    url(r'^', include('cms.urls', namespace='cms')),
)
