from django import forms
from django.db.models import Q
from django.db.models import Count
from events.models import Testimonials
from creation.models import FossCategory, Language, TutorialResource

class KeywordSearchForm(forms.Form):
    q = forms.CharField(required=True)

class TutorialSearchForm(forms.Form):
    try:
        foss_list = TutorialResource.objects.filter(Q(status = 1) | Q(status = 2), language__name = 'English').values('tutorial_detail__foss__foss').annotate(Count('id')).order_by('tutorial_detail__foss__foss').values_list('tutorial_detail__foss__foss', 'id__count').distinct()
        choices = [('', '-- All Courses --'),]
        for foss_row in foss_list:
            choices.append((str(foss_row[0]), str(foss_row[0]) + ' (' + str(foss_row[1]) + ')'))
        search_foss = forms.ChoiceField(
            choices = choices,
            widget=forms.Select(),
            required = False,
        )
        lang_list = TutorialResource.objects.filter(Q(status = 1) | Q(status = 2)).values('language__name').annotate(Count('id')).order_by('language').values_list('language__name', 'id__count').distinct()
        choices = [('', '-- All Languages --'),]
        for lang_row in lang_list:
            choices.append((str(lang_row[0]), str(lang_row[0]) + ' (' + str(lang_row[1]) + ')'))
        search_language = forms.ChoiceField(
            choices = choices,
            widget = forms.Select(),
            required = False,
        )
    except:
        pass

class TestimonialsForm(forms.ModelForm):
    actual_content = forms.CharField(widget=forms.Textarea(attrs={'cols': 10, 'rows': 4}))
    minified_content = forms.CharField(widget=forms.Textarea(attrs={'cols': 10, 'rows': 4}))
    source_title = forms.CharField(required =  False)
    source_link = forms.CharField(required =  False)
    status = forms.BooleanField(required = False)
    compn_type = forms.ChoiceField(widget=forms.Select, choices = [('none','---------'),('doc', 'Document'), ('audio', 'Audio'), ('video', 'Video')], required = True)
    source = forms.FileField(label = 'Select a file', required = False)
    class Meta:
        model = Testimonials
        exclude = ['approved_by', 'user']
        
    def clean(self):
        super(TestimonialsForm, self).clean()
        ct = self.cleaned_data['compn_type']
        content = self.cleaned_data['source']
	if content:
        	extension = self.cleaned_data['source'].name.split('.')[-1]
        if (ct == "audio" or ct == "video" or ct == ""):
            try :
                content.content_type
            except :
                raise forms.ValidationError("Please upload the selected component. Upload the file")
                
        if ct == "audio" and content.name.split('.')[-1] != "ogg" and content.name.split('.')[-1] != "mp3" and content.name.split('.')[-1] != "amr":
            raise forms.ValidationError("Audio file format mis-match!!. Only .ogg file allowed")
        elif ct == "video" and content.name.split('.')[-1] != "ogv" and content.name.split('.')[-1] != "avi" and content.name.split('.')[-1] != "webm" and content.name.split('.')[-1] != 'flv':
            raise forms.ValidationError("Video file format mis-match!!. Only .ogv file allowed")
        elif ct == "doc" and self.cleaned_data['source'].name.split('.')[-1] != "pdf":
            raise forms.ValidationError("Document file format mis-match!!. Only .pdf file allowed")
	#elif ct == "none" and content.content_type is not None:
	#    raise forms.ValidationError("Please select proper component type.")
        return self.cleaned_data
