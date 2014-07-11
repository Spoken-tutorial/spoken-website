from django.conf.urls import patterns, include, url
import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Examples:
    url(r'^tutorial-search/$', 'spoken.views.tutorial_search', name="tutorial-search"),
    url(r'^keyword-search/$', 'spoken.views.keyword_search', name="keyword-search"),
    url(r'^watch/([0-9a-zA-Z-+%]+)/([0-9a-zA-Z-+%]+)/(\w+)/$', 'spoken.views.watch_tutorial', name="watch_tutorial"),
    url(r'^get-language/$', 'spoken.views.get_language', name="get_language"),
    url(r'^testimonials/$', 'spoken.views.testimonials', name="testimonials"),
    url(r'^testimonials/new/$', 'spoken.views.testimonials_new', name="testimonials_new"),
    url(r'^admin/testimonials/$', 'spoken.views.admin_testimonials', name="admin_testimonials"),
    url(r'^admin/testimonials/(?P<rid>\d+)/edit/$', 'spoken.views.admin_testimonials_edit', name="admin_testimonials_edit"),
    url(r'^$', 'spoken.views.home', name='home'),
    url(r'^home/', 'spoken.views.home', name='home'),
    # url(r'^spoken/', include('spoken.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #events urls
    url(r'^software-training/', include('events.urls', namespace='events')),
    url(r'^moodle/', include('mdldjango.urls', namespace='mdldjango')),

    url(r'^creation/', include('creation.urls', namespace='creation')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^migration/creation/', include('creationmigrate.urls', namespace='creationmigrate')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':False}),
    #cms
    url(r'^', include('cms.urls', namespace='cms')),
)
