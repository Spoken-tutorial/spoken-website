from .models import AsyncCronMail
from django.views.generic import CreateView, FormView
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import AsyncCronMailForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from .tasks import async_bulk_email
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json
import csv
import uuid
from django.http import HttpResponse, JsonResponse
import datetime as dt
from config import WORKER_STATUS,WORKER_TIME

class AsyncCronMailListCreateView(UserPassesTestMixin, CreateView):
    template_name = 'cron/cron_mail_list_create.html'
    model = AsyncCronMail
    form_class = AsyncCronMailForm
    success_url = reverse_lazy('cron:mail_list_create')

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        if 'view' not in kwargs:
            kwargs['view'] = self
        if 'task' not in kwargs:
            kwargs['task'] = AsyncCronMail.objects.all().order_by('-uploaded_at') 
        return kwargs

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.uploaded_by = self.request.user
        self.object.status = False
        self.object.save()
        return super(CreateView, self).form_valid(form)


    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='HR').exists()

@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='HR').exists())
def run_cron_mail(request):
    if 'submit' in request.POST:
        submit = request.POST['submit']
        if submit == 'Run':
            if dt.time(*WORKER_TIME) < dt.datetime.now().time():
                if WORKER_STATUS:
                    if AsyncCronMail.objects.filter(started_at__isnull=False,status=False).count() == 0:
                        cron_id = request.POST['cron_id']
                        task = AsyncCronMail.objects.get(pk=cron_id)
                        task.started_at = timezone.now()
                        task.job_id=str(uuid.uuid4())
                        task.save()
                        async_bulk_email(task)
                        messages.success(request, "We are processing your request. Please wait a moment and refresh this page.")
                        return redirect('cron:mail_list_create')
                    else:
                        messages.error(request, "Cannot run task. A mass mail is already running.")
                        return redirect('cron:mail_list_create')
                else:
                    messages.error(request, "Mass mail worker is not running. Ask Spoken Tutorial Administrator to run it.")
                    return redirect('cron:mail_list_create')
            else:
                messages.error(request, "Cannot run task. You can run mails only after 5.30 pm")
                return redirect('cron:mail_list_create')
        else:
            messages.success(request, "Invalid Request.")
            return redirect('cron:mail_list_create')
    else:
        return redirect('cron:mail_list_create')




@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='HR').exists())
def update_task(request):
    if request.method == 'POST':
        cron_id = int(request.POST['task_id'])
        task = AsyncCronMail.objects.get(pk=cron_id)
        if not task.status:
            task.subject=request.POST['task_subject']
            task.message=request.POST['task_message']
            task.save()
            return redirect('cron:mail_list_create')
    return redirect('cron:mail_list_create')

@csrf_exempt
def upload_task(request):
    if request.user.is_superuser or request.user.groups.filter(name='HR').exists():
        if request.method == 'POST':
            subject=request.POST['subject']
            message=request.POST['message']
            job=request.POST['job']
            data = json.loads(request.POST.get('data'))
            file_name = 'emails/'+str(uuid.uuid4())+'.csv'
            try:
                with open('media/'+file_name,'w') as f:
                    write = csv.writer(f)
                    write.writerows(data['data'])
                    cron=AsyncCronMail.objects.create(subject=subject, message=message, uploaded_by=request.user, status=False, ers_job_id=job)
                    cron.csvfile.name = file_name
                    cron.save()
                    return JsonResponse({'status':True,'success_url':request.build_absolute_uri('/cron/mail_list_create')})
            except:
                return JsonResponse({'status':False,'success_url':None})
    return JsonResponse({'status':False,'success_url':None})