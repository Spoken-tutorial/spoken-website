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
            kwargs['task'] = AsyncCronMail.objects.all()
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
        return self.request.user.is_superuser

@user_passes_test(lambda u: u.is_superuser)
def run_cron_mail(request):
    if 'submit' in request.POST:
        submit = request.POST['submit']
        if submit == 'Run':
            cron_id = request.POST['cron_id']
            task = AsyncCronMail.objects.get(pk=cron_id)
            task.started_at = timezone.now()
            task.save()
            async_bulk_email.delay(cron_id)
            messages.success(request, "We are processing your request. Please wait a moment and refresh this page.")
            return redirect('cron:mail_list_create')
        else:
            messages.success(request, "Invalid Request.")
            return redirect('cron:mail_list_create')
    else:
        return redirect('cron:mail_list_create')




@user_passes_test(lambda u: u.is_superuser)
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
