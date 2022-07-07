from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'mail_list_create/', views.AsyncCronMailListCreateView.as_view(), name='mail_list_create'), 
    url(r'run_cron_mail/', views.run_cron_mail, name='run_cron_mail'),
    url(r'update_cron_mail/', views.update_task, name='update_cron_mail'),
    url(r'upload_task/', views.upload_task, name='upload_task'),
    url(r'run_cron_worker/', views.run_cron_worker, name='run_cron_worker'),
    url(r'read_cron_logs/', views.read_cron_logs, name='read_cron_logs'),
]

