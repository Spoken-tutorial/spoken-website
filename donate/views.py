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
        self.object.user = self.request.user
        self.object.status = False
        self.object.save()
        payment_obj = self.object;

        foss_ids = form.cleaned_data.get('foss_id')
        languages = form.cleaned_data.get('language_id')
        fosses = foss_ids.split(',')
        foss_languages = languages.split(',|')

        payment_id = payment_obj.pk
        
        for i in range(len(fosses)):
            foss_category = FossCategory.objects.get(pk=int(fosses[i]))  
            languages = foss_languages[i].split(',')
            for language in languages:
                if language!='':
                    foss_language = Language.objects.get(pk=int(language))
                    cd_foss_langs = CdFossLanguages()
                    cd_foss_langs.payment = Payment.objects.get(pk=payment_id)
                    cd_foss_langs.foss = foss_category
                    cd_foss_langs.lang = foss_language
                    cd_foss_langs.save()

        form.save_m2m()
        return super(PaymentController, self).form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        messages.warning(self.request, 'Invalid form payment request.')
        return redirect('cdcontent:cdcontenthome')