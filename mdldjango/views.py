from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from models import MdlUser
from events.models import WorkshopAttendance
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from forms import *
import xml.etree.cElementTree as etree
# Create your views here.
import hashlib

def authenticate(username = None, password = None):
	try:
		print " i am in moodle auth"
		user = MdlUser.objects.get(username=username)
		print user
		pwd = user.password
		p = hashlib.md5(password)
		pwd_valid =  (pwd == p.hexdigest())
		#print pwd
		#print "------------"
		#print p.hexdigest()
		if user and pwd_valid:
			return user
	except Exception, e:
		print e
		print "except ---"
		return None

def mdl_logout(request):
	del request.session['mdluserid']
	request.session.save()
	print "logout !!"
	return HttpResponseRedirect("/moodle/login")
	
def mdl_login(request):
	messages = {}
	if request.POST:
		username = request.POST["username"]
		password = request.POST["password"]
		if not username or not password:
			messages['error'] = "Please enter valide Username and Password!"
			#return HttpResponseRedirect("/moodle/login")
		user = authenticate(username = username, password = password)
		if user:
			request.session['mdluserid'] = user.id
			request.session['mdluseremail'] = user.email
			request.session['mdluserinstitution'] = user.institution
			request.session.save()
			request.session.modified = True
		else:
			messages['error'] = "Username or Password Doesn't match!"

	if request.session.get('mdluserid'):
		print "Current user is ", request.session.get('mdluserid')
		return HttpResponseRedirect("/moodle/index")
		
	context = {'message':messages}
	context.update(csrf(request))
	return render(request, 'mdl/templates/mdluser_login.html', context)

def index(request):
	if not request.session.get('mdluserid'):
		return HttpResponseRedirect("/moodle/login")
	print "MDL User id = ", request.session.get('mdluserid')
	
@login_required
def offline_details(request):
	user = request.user
	form = OfflineDataForm(user = request.user)
	if request.method == 'POST':
		form = OfflineDataForm(user, request.POST, request.FILES)
		if form.is_valid():
			xmlDocData = form.cleaned_data['xml_file'].read()
			xmlDocTree = etree.XML(xmlDocData)

			for studentDetails in xmlDocTree.iter('detail'):
				firstname = studentDetails[0].text
				lastname = studentDetails[1].text
				gender =  studentDetails[2].text
				age = studentDetails[3].text
				email = studentDetails[4].text
				permanent_address = studentDetails[5].text
				city = studentDetails[6].text
				country = studentDetails[7].text
				department = studentDetails[8].text
				password = hashlib.md5(studentDetails[0].text)
				password = password.hexdigest()
				try:
					mdluser = MdlUser.objects.get(email = email)
					
				except Exception, e:
					mdluser = MdlUser()
					mdluser.firstname = firstname
					mdluser.username = firstname
					mdluser.lastname = lastname
					mdluser.password = password
					mdluser.email = email
					mdluser.save()
					mdluser = MdlUser.objects.filter(email = email, firstname= firstname, username=firstname, password=password).first()
				
				try:
					wa = WorkshopAttendance.objects.get(workshop_id = form.cleaned_data['workshop_code'], mdluser_id = mdluser.id)
				except Exception, e:
					wa = WorkshopAttendance()
					wa.workshop_id = form.cleaned_data['workshop_code']
					wa.status = 1
					wa.mdluser_id = mdluser.id
					wa.save()

	#return HttpResponse('XML file read Done!')
	messages = {}
	context = {
		'form': form,
		'message':messages,
	}
	context.update(csrf(request))
	return render(request, 'mdl/templates/offline_details.html', context)

