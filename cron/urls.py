from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'mail_list_create/', views.AsyncCronMailListCreateView.as_view(), name='mail_list_create'), 
    url(r'run_cron_mail/', views.run_cron_mail, name='run_cron_mail'),
    url(r'update_cron_mail/', views.update_task, name='update_cron_mail'),
        
]

