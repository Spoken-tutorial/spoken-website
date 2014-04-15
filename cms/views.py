from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.http import Http404
from cms.models import *
from cms.forms import *
import random, string

def dispatcher(request, permalink=''):
	if permalink == '':
		permalink = 'home'
	page_content = get_object_or_404(Page, permalink=permalink)
	context = {
		'page': page_content,
	}
	return render_to_response('cms/templates/page.html', context)

def account_register(request):
	context = {}
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			email = request.POST['email']
			user = User.objects.create_user(username, email, password)
			user.is_active = False
			user.save()
			confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
			p = Profile(user=user, confirmation_code=confirmation_code)
			p.save()
			send_registration_confirmation(user)
			return HttpResponseRedirect('/')
		context = {'form':form}
		return render_to_response('cms/templates/register.html', context, context_instance = RequestContext(request))
	else:
		form = RegisterForm()
		context = {
			'form': form
		}
		context.update(csrf(request))
		return render_to_response('cms/templates/register.html', context)

def send_registration_confirmation(user):
	p = Profile.objects.get(user=user)
	title = "CMS account confirmation"
	content = "http://www.sample.com/confirm/" + str(p.confirmation_code) + "/" + user.username
	#send_mail(title, content, 'no-reply@sample.com', [user.email], fail_silently=False)
	

def confirm(request, confirmation_code, username):
	try:
		user = User.objects.get(username=username)
		profile = Profile.objects.get(user=user)
		if profile.confirmation_code == confirmation_code and user.date_joined > (timezone.now()-timezone.timedelta(days=1)):
			user.is_active = True
			user.save()
			user.backend='django.contrib.auth.backends.ModelBackend' 
			login(request,user)
			return HttpResponseRedirect('/')
	except:
		return HttpResponseRedirect('/')

def account_login(request):
	if request.user.is_anonymous():
		form = LoginForm()
		context = {
			'form' : form
		}
		if request.method == 'POST':
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					if request.GET and request.GET['next']:
						return HttpResponseRedirect(request.GET['next'])
					return HttpResponseRedirect('/')
				else:
					context['info'] = 'Your account is disabled.'
			else:
				context['error'] = 'Invalid username / password'
				return render(request, 'cms/templates/login.html', context)
		context.update(csrf(request))
		return render_to_response('cms/templates/login.html', context)
	return HttpResponseRedirect('/')

def account_logout(request):
	context = RequestContext(request)
	logout(request)
	return HttpResponseRedirect('/')

def account_profile(request, username):
	#todo: validation
	#todo: store location, state and etc.. ids
	if request.method == 'POST':
		user = User.objects.get(username=username)
		form = ProfileForm(request.POST, user = request.user, instance = Profile.objects.get(user = user))
		if form.is_valid():
			user.first_name = request.POST['first_name']
			user.last_name = request.POST['last_name']
			user.save()
			
			profile = Profile.objects.get(user=user)
			profile.street = request.POST['street']
			profile.location = request.POST['location']
			profile.district = request.POST['district']
			profile.city = request.POST['city']
			profile.state = request.POST['state']
			profile.country = request.POST['country']
			profile.pincode = request.POST['pincode']
			profile.phone = request.POST['phone']
			profile.save()
			return HttpResponseRedirect("/accounts/profile/"+username+"/")
		
		context = {'form':form}
		return render_to_response('cms/templates/profile.html', context, context_instance = RequestContext(request))
	#if username:
	#	try:
	user = User.objects.get(username=username)
	context = {}
	context['form'] = ProfileForm(user = request.user, instance = Profile.objects.get(user = user))
	context.update(csrf(request))
	return render(request, 'cms/templates/profile.html', context)
	#	except:
	#		raise Http404('Page not found')
	#else:
	#	raise Http404('Page not found')
