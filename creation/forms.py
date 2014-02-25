from django import forms
from django.core.validators import RegexValidator
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.db.models import Q

from creation.models import *

class ContributorRoleForm(forms.ModelForm):
	user = forms.ModelChoiceField(cache_choices = True, queryset = User.objects.filter(Q(groups__name = 'Contributor')).order_by('username'), help_text = "", error_messages = {'required':'User field required.'})
	foss_category = forms.ModelChoiceField(cache_choices = True, queryset = Foss_Category.objects.order_by('foss'), empty_label = "----------", help_text = "", error_messages = {'required':'FOSS category field required.'})
	language = forms.ModelChoiceField(cache_choices =True, queryset = Language.objects.order_by('name'), empty_label = "----------", help_text = "", error_messages = {'required':'Language field required.'})
	status = forms.BooleanField(required = False)

	class Meta:
		model = Contributor_Role
		exclude = ['created', 'updated']

class DomainReviewerRoleForm(forms.ModelForm):
	user = forms.ModelChoiceField(cache_choices = True, queryset = User.objects.filter(Q(groups__name = 'Domain-Reviewer')).order_by('username'), help_text = "", error_messages = {'required':'User field required.'})
	foss_category = forms.ModelChoiceField(cache_choices = True, queryset = Foss_Category.objects.order_by('foss'), empty_label = "----------", help_text = "", error_messages = {'required':'FOSS category field required.'})
	language = forms.ModelChoiceField(cache_choices =True, queryset = Language.objects.order_by('name'), empty_label = "----------", help_text = "", error_messages = {'required':'Language field required.'})
	status = forms.BooleanField(required = False)

	class Meta:
		model = Domain_Reviewer_Role
		exclude = ['created', 'updated']

class QualityReviewerRoleForm(forms.ModelForm):
	user = forms.ModelChoiceField(cache_choices = True, queryset = User.objects.filter(Q(groups__name = 'Quality-Reviewer')).order_by('username'), help_text = "", error_messages = {'required':'User field required.'})
	foss_category = forms.ModelChoiceField(cache_choices = True, queryset = Foss_Category.objects.order_by('foss'), empty_label = "----------", help_text = "", error_messages = {'required':'FOSS category field required.'})
	language = forms.ModelChoiceField(cache_choices =True, queryset = Language.objects.order_by('name'), empty_label = "----------", help_text = "", error_messages = {'required':'Language field required.'})
	status = forms.BooleanField(required = False)

	class Meta:
		model = Quality_Reviewer_Role
		exclude = ['created', 'updated']

class UploadTutorialForm(forms.Form):
	#foss_category = forms.CharField(widget = forms.Select(choices = fosschoices), required = True)
	tutorial_name = forms.CharField(widget = forms.Select(choices = [('', ''),], attrs = {'disabled': 'disabled'}), required = True, error_messages = {'required':'Tutorial Name field is required.'})
	language = forms.CharField(widget = forms.Select(choices = [('', ''),], attrs = {'disabled': 'disabled'}), required = True, error_messages = {'required':'Language field is required.'})
	def __init__(self, user, *args, **kwargs):
		super(UploadTutorialForm, self).__init__(*args, **kwargs)
		foss_list = list(Foss_Category.objects.filter(id__in=Contributor_Role.objects.filter(user_id=user.id).values_list('foss_category_id')).values_list('id', 'foss'))
		foss_list.insert(0, ('', ''))
		self.fields['foss_category'] = forms.ChoiceField(choices=foss_list, error_messages = {'required':'FOSS category field is required.'})
		print self.fields['foss_category']

