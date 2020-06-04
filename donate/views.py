from django.shortcuts import render
from creation.models import FossCategory, Language
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template.context_processors import csrf
from donate.forms import PaymentForm
from donate.models import *
from django import forms
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from cdcontent.forms import CDContentForm
from django.contrib import messages

@csrf_exempt
def donatehome(request):
    form = PayeeForm(initial={'country': 'India'})
    if request.method=='POST':
          type = request.POST.get("type", "")
          amount = request.POST.get("amount", "")
          if type == 'initiate':
               form.fields['amount'].widget = forms.NumberInput(attrs={'min': amount,'step': 50.00})
               form.initial = {'amount': amount}
    else:
        form = PayeeForm(initial={'country': 'India','amount':50.00})
        form.fields['amount'].widget = forms.NumberInput(attrs={'min': 50.00,'step': 50.00})

    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'donate/templates/donate_home.html', context)

class PaymentController(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name = 'cdcontent/templates/cdcontent_home.html'
    model = Payment
    form_class = PaymentForm
    success_url = reverse_lazy('cdcontent:cdcontenthome')

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        foss_id = form.cleaned_data.get('foss_id')
        language_id = form.cleaned_data.get('language_id')
        self.object.foss = FossCategory.objects.get(pk=foss_id)
        self.object.user = self.request.user
        self.object.status = False
        self.object.save()
        self.object.language = Language.objects.filter(pk__in = language_id)
        form.save_m2m()
        return super(PaymentController, self).form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        messages.warning(self.request, 'Invalid form payment request.')
        return redirect('cdcontent:cdcontenthome')