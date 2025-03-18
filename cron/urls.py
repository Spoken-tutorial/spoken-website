from django.urls import re_path, path
from . import views


urlpatterns = [
    re_path(r'mail_list_create/', views.AsyncCronMailListCreateView.as_view(), name='mail_list_create'), 
    re_path(r'run_cron_mail/', views.run_cron_mail, name='run_cron_mail'),
    re_path(r'update_cron_mail/', views.update_task, name='update_cron_mail'),
    re_path(r'upload_task/', views.upload_task, name='upload_task'),
    re_path(r'run_cron_worker/', views.run_cron_worker, name='run_cron_worker'),
    re_path(r'read_cron_logs/', views.read_cron_logs, name='read_cron_logs'),
]

