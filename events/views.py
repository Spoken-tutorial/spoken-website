from django.shortcuts import render, render_to_response
#template
from django.template import RequestContext
#return without view
from django.http import HttpResponse, HttpResponseRedirect
#group
from django.contrib.auth.models import Group
#form token
from django.core.context_processors import csrf
#
from django.views.decorators.csrf import csrf_exempt
#json
import json
#permission denied
from django.http import Http404
#display message
from django.contrib import messages
#auth login_required
from django.contrib.auth.decorators import login_required
# Create your views here.
# Models
from models import *
#custom forms
from forms import *

#web scraping
import urllib,urllib2
from BeautifulSoup import BeautifulSoup

def update_college(request):
	def read_url(link = None):
		print "Reading --:",link
		try:
			conn=urllib2.urlopen(link)
			contents = conn.read()
			return BeautifulSoup(contents)
		except:
			return 0
	
	def get_page_link(link = None, links = None):
		try:
			soup = read_url(link)
			pages = soup.find('p',{"class":"pagination"})
			page = pages.findAll('a') 
			collegelink = ''
			for p in page:
				#print p['href']
				if p['href'] not in links:
					#print len(links)
					links.append(p['href'])
			return links
		except:
			links = [link]
			#print "dddd",link 
			#print "hhhhhh",links
			return links
	
	#print links
	#completed_state[]
	rstates = State.objects.filter(code='AP')
	for rstate in rstates:
		ctypes = Institute_type.objects.all()
		for ctype in ctypes:
			links = []
			state = rstate.id
			scode = rstate.code
			record_count = 0
			toread_link = "http://www.studyguideindia.com/Colleges/"+ctype.name.replace(" & ", "-").replace(" ", "-")+"/default.asp?State="+scode
			#print "yes"
			links = get_page_link(toread_link, links)
			#print len(links)
			if len(links) == 10:
				links = get_page_link(links[9], links)
			
			#print links
			
			for link in links:
				institution_type = ctype.id
				location = 150031
				city = 189
				
				soup = read_url(link)
				if not soup:
					continue
					
				#print soup
				table = soup.find('table',{"align":"center", "width":"99%"}) 
				rows= table.findAll('tr')
				error=[]
				university = ''
				for row in rows:
					collegelink = ''
					#print row
					# Get the college name
					td=row.findAll('td',{"align":"left", "valign":"top", "height":"30"})
					if not td:
						continue
						
					for t in td:
						try:
							#print '--------------'
							college_name = t.a.text.split(',')[0]
							print "College name :", college_name
							
							#print '--------------'
							collegelink = t.a['href']
							#print collegelink 
							soup = read_url(collegelink)
							table = soup.findAll("table",{"class":"altcolor1","border":"0", "cellpadding":"10", "cellspacing":"0" ,"width":"100%"})
							t= table[0]
							crows= t.findAll('tr')
							#print crows
							i=True
							#print "---------------------"
							for crow in crows:
								if i:
									output=''
									tdc=crow.findAll('td', {"align":"left"})
									try:
										if tdc[0].text == "Affiliated to":
											university = tdc[1].text.strip()
											print "Affiliated to : ", university
									except:
										print " No Affiliated to !!!: "
						except:
							error.append(t)
					#Get the District
					td=row.findAll('td',{"align":"left", "valign":"middle"})
					i = 0
					for t in td:
						if(i % 2 == 0):
							try:
								district = t.text.split('&nbsp;')[0].strip()
								try:
									d = District.objects.get(state = state, name = district)
									district = d.id
								except:
									district = 652
							except:
								error.append(t)
						i = i + 1
					
					#insert in to db
					
					#find the university
					if university:
						try:
							#print "+++++++++", university
							u = University.objects.get(name = university, state_id = state)
							unid = u.id
							#print "University already exits !!"
						except:
							u = University(user_id = 1, state_id = state, name = university)
							u.save()
							unid = u.id
							print "University Inserted !!"
					else:
						unid = 1
					
					#return HttpResponse('Done!')
					#insert college
					#print "University : ", unid
					#print "collage Name : ", college_name
					#print "District : ", district
					
					# find the academic code available number
					try:
						ac = Academic_center.objects.filter(state = state).order_by('-academic_code')[:1].get()
					except:
						#print "This is first record!!!"
						ac = None
						academic_code = 1
						
					if ac:
						code_range = int(ac.academic_code.split('-')[1])
						available_code_range = []
						for i in range(code_range):
							available_code_range.insert(i, i+1)
						
						#find the existing numbers
						ac = Academic_center.objects.filter(state = state).order_by('-academic_code')
						for record in ac:
							a = int(record.academic_code.split('-')[1])-1
							available_code_range[a] = 0
						
						academic_code = code_range + 1
						#print available_code_range
						#finding Missing number
						for code in available_code_range:
							if code != 0:
								academic_code = code
								break

					# Generate academic code
					if academic_code < 10:
						ac_code = '0000'+str(academic_code)
					elif academic_code <= 99:
						ac_code = '000'+str(academic_code)
					elif academic_code <= 999:
						ac_code = '00'+str(academic_code)
					elif academic_code <= 9999:
						ac_code = '0'+str(academic_code)
					
					#get state code
					state_code = State.objects.get(pk = state).code
					academic_code = state_code +'-'+ ac_code
					#insert college
					print "University : ", unid
					print "collage Name : ", college_name
					print "District : ", district
					print "Academic Code : ", academic_code
					if unid and district and college_name:
						try:
							p = Academic_center(user_id = 1, state_id = state, university_id = unid, academic_code = academic_code, institution_type_id = institution_type, institution_name = college_name, district_id = district, location_id = location, city_id = city, street = ' ', pincode = 0, resource_center = 0, rating = 1, contact_person = ' ', status=0)
							#print p
							p.save()
							print "Updated !!"
							record_count = record_count +1
						except:
							print "College already Exits !!!"
					else:
						print "Not inserted"
					
					#return HttpResponse('Done!')
					print "==================================================================================="
			print "Total Record updated : ", record_count
	return HttpResponse('Done!')
def update_district(request):
	
	#with proxy
	#proxy = urllib2.ProxyHandler({'http': 'http://username:password@netmon.iitb.ac.in:80'})
	#auth = urllib2.HTTPBasicAuthHandler()
	#opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
	#urllib2.install_opener(opener)
	#conn=urllib2.urlopen("http://en.wikipedia.org/wiki/List_of_districts_of_India#Andaman_and_Nicobar_.28AN.29")
	
	#get the state and district
	conn=urllib2.urlopen("http://en.wikipedia.org/wiki/List_of_districts_of_India#Andaman_and_Nicobar_.28AN.29")
	contents = conn.read()
	soup = BeautifulSoup(contents)
	
	disttables = soup.findAll("table", attrs={'cellspacing':'1', 'cellpadding':'1'})
	#print len(disttables)
	states = soup.findAll('span', attrs={'class':'mw-headline'})
	#print len(states)
	#display all states
	print '#############################'
	print "  Update State and District "
	print '#############################'
	for k in range(len(disttables)):
		#get state code
		tmp = states[k+3].text.split('(')
		statecode = tmp[1].replace(')','')
		statename = tmp[0]
		#try:
		#	p = State(code=statecode.strip(), name=statename.strip())
		#	p.save()
		#	print statecode,' - ',statename,' - Updated!!!'
		#except:
		#	print statecode,' - ',statename,' - Already exits!!!'

		#find the stateid
		scode = State.objects.get(code=statecode)

		disttr = disttables[k].findAll('tr', attrs = {'bgcolor':'#F4F9FF'});
		for j in range(len(disttr)):
			disttd = disttr[j].findAll('td');
			distname = disttd[1].text
			distcode =disttd[0].text
			try:
				p = District(state_id=scode.id, code=distcode.strip(), name=distname.strip())
				p.save()
				print scode.id,' - ',scode.name,' - ',distcode,' - ',distname,' - Updated!!!'
			except:
				print scode.id,' - ',scode.name,' - ',distcode,' - ',distname,' - Already exits!!!'
				
	#update city
	###
	"""print '################'
	print "  Update City "
	print '################'
	conn=urllib2.urlopen("http://en.wikipedia.org/wiki/List_of_municipal_corporations_of_India")
	contents = conn.read()
	soup = BeautifulSoup(contents)
	citytables = soup.findAll("table", attrs={'cellspacing':'0','cellpadding':'5'})
	cityrow = citytables[0].findAll("tr")
	for c in range(len(cityrow)):
		city = cityrow[c].findAll('td')
		#print '--------------------'
		#print city
		#print '----------------'
		if city:
			tmp = city[1].text
			statename = tmp.replace(']', '').replace('[', '')
			cityname = city[0].text
			scode = State.objects.get(name=statename)
			try:
				p = City(state_id=scode.id, name=cityname.strip())
				p.save()
				print statename,' - ',scode.id,' - ',scode.name,' - ',cityname,' - Updated'
			except:
				print statename,' - ',scode.id,' - ',scode.name,' - ',cityname,' - Alreay exits'
	  """		  
	return HttpResponse('Done!')
	###
def check_district(request):
	states = State.objects.all()
	for state in states:
		#Get all district from state
		state_id = state.id
		state = state.name.replace(" ", "-")
		conn=urllib2.urlopen("http://www.mapsofindia.com/pincode/india/"+state)
		#print "Reading ", state
		contents = conn.read()
		soup = BeautifulSoup(contents)
		citytables = soup.findAll("table", attrs={'cellspacing':'0', 'cellpadding':'4'})
		cityrow = citytables[0].findAll("tr")
		print "===================="
		print "	 "+state
		print "===================="
		#print cityrow
		for c in range(len(cityrow)):
			#print cityrow[c]
			city = cityrow[c].findAll('td')
			#print city
			district_url = (city[0].text).replace(" ", "-")
			district = city[0].text
			if district_url == 'District':
				continue
			#print "--- district --",district
			#db: get the district id
			try:
				districtid = District.objects.get(name=district, state_id=state_id)
				#print district,"!!!!"
			except:
				#print state
				#print "-------------"
				print "--- district --: ",district
				#p = District(state_id = state_id, name = district.strip())
				#p.save()
				#districtid = District.objects.get(name=district, state_id=state_id)

	return HttpResponse('Done!')

def update_location(request):
	def read_url(link = None):
		print "Reading --:",link
		conn=urllib2.urlopen(link)
		contents = conn.read()
		return BeautifulSoup(contents)
	
	#completed_state = ['Andaman and Nicobar islands', 'Andhra Pradesh','Arunachal Pradesh', 'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh', 'Dadra and Nagar Haveli','Daman and Diu', 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Lakshadweep', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Orissa', 'Pondicherry', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Tripura', 'Uttar Pradesh', '']
	completed_state = []
	states = State.objects.all()
	for state in states:
		#Get all district from state
		state_id = state.id
		if state.name in completed_state:
			continue
		state = state.name.replace(" ", "-")
		#print state
		#print completed_state
		#return HttpResponse('Done!')
		soup = read_url("http://www.mapsofindia.com/pincode/india/"+state)
		citytables = soup.findAll("table", attrs={'cellspacing':'0', 'cellpadding':'4'})
		cityrow = citytables[0].findAll("tr")
		print "-------------------"
		print "	"+state
		print "-------------------"
		#print cityrow
		for c in range(len(cityrow)):
			print "=========="
			#print cityrow[c]
			city = cityrow[c].findAll('td')
			#print city
			district_url = (city[0].text).replace(" (", "-").replace(")", "").replace(" ", "-").strip()
			district = city[0].text
			if district_url == 'District':
				continue
			print "--- district --",district
			#db: get the district id
			try:
				districtid = District.objects.get(name=district, state_id=state_id)
			except:
				error = state_id," - ",state," - ",district
				p = Error(name=error)
				p.save()
				#districtid = District.objects.get(name=district, state_id=state_id)
			
			#print district_url
			#print "============"
			#print district
			#print districtid.id
			#get all area from district
			if district_url:
				url = "http://www.mapsofindia.com/pincode/india/"+state+'/'+district_url
				#print "Reading url ..:",url
				soup = read_url(url)
				location = soup.findAll("table", attrs={'cellspacing':'0', 'cellpadding':'4'})
				location = location[0].findAll("tr")
				for l in range(len(location)):
					area_code = location[l].findAll('td')
					area = area_code[0].text
					code = area_code[1].text
					if area == 'Location':
						continue
						
					try:
						p = Location(district_id = districtid.id, name = area.strip(), pincode = code.strip())
						p.save()
						print area,' - ',districtid.id,' - ',code,' - Updated'
					except:
						print area,' - ',districtid.id,' - ',code,' - Already exits!!'
						
	return HttpResponse('Done!')

#user roles
def is_event_manager(user):
	"""Check if the user is having event manger  rights"""
	if user.groups.filter(name='Event Manager').count() == 1:
		return True
		
def is_resource_person(user):
	"""Check if the user is having resource person  rights"""
	if user.groups.filter(name='Resource Person').count() == 1:
		return True
		
def is_organiser(user):
	"""Check if the user is having organiser rights"""
	if user.groups.filter(name='Organiser').count() == 1:
		return True

def is_invigilator(user):
	"""Check if the user is having invigilator rights"""
	if user.groups.filter(name='Invigilator').count() == 1:
		return True

@login_required
def state(request):
	""" State index page """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user):
	#	raise Http404('You are not allowed to view this page!')
	context = {}
	context['collection'] = State.objects.all
	context['model'] = "state"
	context.update(csrf(request))
	return render(request, 'events/templates/states/index.html', context)

@login_required
def new_state(request):
	""" Create a new state """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user):
	#	raise Http404('You are not allowed to view this page!')
	
	if request.method == 'POST':
		form = StateForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect("/events/states/")
		
		context = {'form':form}
		return render(request, 'events/templates/states/form.html', context)
	else:
		context = {}
		context.update(csrf(request))
		context['form'] = StateForm()
		return render(request, 'events/templates/states/form.html', context)

@login_required
def edit_state(request, rid = None):
	""" Edit states """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user):
	#	raise Http404('You are not allowed to view this page!')
		
	if request.method == 'POST':
		contact = State.objects.get(id = rid)
		form = StateForm(request.POST, instance=contact)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect("/events/states")
		context = {'form':form}
		return render(request, 'events/templates/states/form.html', context)
	else:
		author = State.objects.get(id = rid)
		context = {}
		context['form'] = StateForm(instance=author)
		context['edit'] = rid
		context.update(csrf(request))
		return render(request, 'events/templates/states/form.html', context)

""" User roles Roles """
@login_required
def new_roles_rp(request):
	""" Assign a new state """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user):
	#	raise Http404('You are not allowed to view this page!')
	
	if request.method == 'POST':
		form = RpForm(request.POST)
		if form.is_valid():
			form_data = form.save(commit=False)
			form_data.assigned_by = user.id
			form_data.save()
			return HttpResponseRedirect("/events/roles/rp")
		
		context = {'form':form}
		return render(request, 'events/templates/rp/form.html', context)
	else:
		context = {}
		context.update(csrf(request))
		context['form'] = RpForm()
		return render(request, 'events/templates/rp/form.html', context)
	return HttpResponse('RP!')

@login_required
def edit_roles_rp(request, rid = None):
	""" Edit Resource_person """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user):
	#	raise Http404('You are not allowed to view this page!')
		
	if request.method == 'POST':
		contact = Resource_person.objects.get(id = rid)
		form = RpForm(request.POST, instance=contact)
		if form.is_valid():
			if form.save():
				return HttpResponseRedirect("/events/roles/rp")
		context = {'form':form}
		return render(request, 'events/templates/rp/form.html', context)
	else:
		try:
			record = Resource_person.objects.get(id = rid)
			context = {}
			context['form'] = RpForm(instance = record)
			context['edit'] = rid
			context.update(csrf(request))
			return render(request, 'events/templates/rp/form.html', context)
		except:
			raise Http404('Page not found')

@login_required
def roles_rp(request):
	""" Resource_person index page """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user):
	#	raise Http404('You are not allowed to view this page!')
		
	context = {}
	context['collection'] = Resource_person.objects.order_by('state')
	context['model'] = "state"
	context.update(csrf(request))
	return render(request, 'events/templates/rp/index.html', context)

@login_required
def new_ac(request):
	""" Create new academic center. Academic code generate by autimatic.
		if any code missing in between first assign that code then continue the serial
	"""
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')
		
	if request.method == 'POST':
		form = AcademicForm(user, request.POST)
		if form.is_valid():
			form_data = form.save(commit=False)
			form_data.user_id = user.id
			
			state = form.cleaned_data['state']
			# find the academic code available number
			try:
				ac = Academic_center.objects.filter(state = state).order_by('-academic_code')[:1].get()
			except:
				#print "This is first record!!!"
				ac = None
				academic_code = 1
				
			if ac:
				code_range = int(ac.academic_code.split('-')[1])
				available_code_range = []
				for i in range(code_range):
					available_code_range.insert(i, i+1)
				
				#find the existing numbers
				ac = Academic_center.objects.filter(state = state).order_by('-academic_code')
				for record in ac:
					a = int(record.academic_code.split('-')[1])-1
					available_code_range[a] = 0
				
				academic_code = code_range + 1
				#finding Missing number
				for code in available_code_range:
					if code != 0:
						academic_code = code
						break

			# Generate academic code
			if academic_code < 10:
				ac_code = '0000'+str(academic_code)
			elif academic_code <= 99:
				ac_code = '000'+str(academic_code)
			elif academic_code <= 999:
				ac_code = '00'+str(academic_code)
			elif academic_code <= 9999:
				ac_code = '0'+str(academic_code)
			
			#get state code
			state_code = State.objects.get(pk = state.id).code
			academic_code = state_code +'-'+ ac_code
			
			form_data.academic_code = academic_code
			form_data.save()
			return HttpResponseRedirect("/events/ac/")
		
		context = {'form':form}
		return render(request, 'events/templates/ac/form.html', context)
	else:
		context = {}
		context.update(csrf(request))
		context['form'] = AcademicForm(user=request.user)
		return render(request, 'events/templates/ac/form.html', context)

@login_required
def edit_ac(request, rid = None):
	""" Edit academic center """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')
		
	if request.method == 'POST':
		contact = Academic_center.objects.get(id = rid)
		form = AcademicForm(request.user, request.POST, instance=contact)
		if form.is_valid():
			if form.save():
				return HttpResponseRedirect("/events/ac/")
		context = {'form':form}
		return render(request, 'events/templates/ac/form.html', context)
	else:
		try:
			record = Academic_center.objects.get(id = rid)
			context = {}
			context['form'] = AcademicForm(user=request.user, instance = record)
			context['edit'] = rid
			context.update(csrf(request))
			return render(request, 'events/templates/ac/form.html', context)
		except:
			raise Http404('Page not found')

@login_required
def ac(request):
	""" Academic index page """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')
		
	context = {}
	context['collection'] = Academic_center.objects.all
	context['model'] = "Academic Center"
	context.update(csrf(request))
	return render(request, 'events/templates/ac/index.html', context)
	return HttpResponse('RP!')
	
@login_required
def organiser_request(request, username):
	""" request to bacome a new organiser """
	user = request.user
	#if not user.is_authenticated():
	#	raise Http404('You are not allowed to view this page!')
		
	if username == request.user.username:
		user = User.objects.get(username=username)
		if request.method == 'POST':
			form = OrganiserForm(request.POST)
			if form.is_valid():
				user.groups.add(Group.objects.get(name='Organiser'))
				organiser = Organiser()
				organiser.user_id=request.user.id
				organiser.academic_id=request.POST['college']
				organiser.save()
				return HttpResponseRedirect("/events/organiser/"+user.username+"/")
			context = {'form':form}
			return render(request, 'events/templates/organiser/form.html', context)
		else:
			try:
				organiser = Organiser.objects.get(user=user)
				#todo: send status message
				if organiser.status:
					print "you have already organiser role !!"
					return HttpResponseRedirect("/events/organiser/"+user.username+"/")
				else:
					print "Organiser not yet approve !!"
					return HttpResponseRedirect("/events/organiser/"+user.username+"/")
			except:
				context = {}
				context.update(csrf(request))
				context['form'] = OrganiserForm()
				return render(request, 'events/templates/organiser/form.html', context)
	else:
		raise Http404('You are not allowed to view this page!')

@login_required
def organiser_view(request, username):
	""" view organiser details """
	user = request.user
	#if not user.is_authenticated() or not is_organiser(user) or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')
		
	if username == request.user.username or is_resource_person(request.user):
		user = User.objects.get(username=username)
		context = {}
		organiser = Organiser.objects.get(user=user)
		context['record'] = organiser
		try:
			profile = organiser.user.profile_set.get()
		except:
			profile = ''
		context['profile'] = profile
		return render(request, 'events/templates/organiser/view.html', context)
	else:
		raise Http404('You are not allowed to view this page!')

@login_required
def organiser_edit(request, username):
	""" view organiser details """
	#todo: confirm event_manager and resource_center can edit organiser details
	user = request.user
	#if not user.is_authenticated() or not is_organiser(user) or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')
		
	if username == request.user.username:
		user = User.objects.get(username=username)
		if request.method == 'POST':
			form = OrganiserForm(request.POST)
			if form.is_valid():
				organiser = Organiser.objects.get(user=user)
				organiser.user_id=request.user.id
				organiser.academic_id=request.POST['college']
				organiser.save()
				return HttpResponseRedirect("/events/organiser/"+user.username+"/")
			context = {'form':form}
			return render(request, 'events/templates/organiser/form.html', context)
		else:
				#todo : if any workshop and test under this organiser disable the edit
				record = Organiser.objects.get(user=user)
				context = {}
				context['form'] = OrganiserForm(instance = record)
				context.update(csrf(request))
				return render(request, 'events/templates/organiser/form.html', context)
	else:
		raise Http404('You are not allowed to view this page!')

@login_required
def rp_organiser_inactive(request):
	""" Resource person: List all inactive organiser under resource person states """
	#todo: filter to diaplay block and active user
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')
		
	user = User.objects.get(pk=user.id)
	try:
		organiser = Organiser.objects.filter(academic=Academic_center.objects.filter(state=State.objects.filter(resource_person__user_id=user)), status=0)
	except:
		organiser = {}
	context = {}
	context['collection'] = organiser
	context['active'] = False
	return render(request, 'events/templates/rp/organiser.html', context)

@login_required
def rp_organiser_confirm(request, code, userid):
	""" Resource person: active organiser """
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')

	try:
		if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
			organiser = Organiser.objects.get(user_id = userid)
			organiser.appoved_by_id = request.user.id
			organiser.status = 1
			organiser.save()
			return HttpResponseRedirect('/events/organiser/active/')
		else:
			raise Http404('Page not found !!')
	except:
		raise Http404('You are not allowed to view this page!')

@login_required
def rp_organiser_block(request, code, userid):
	""" Resource person: block organiser """
	#todo: if user block, again he trying to register, display message your accout blocked by rp contact rp
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')

	try:
		if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
			organiser = Organiser.objects.get(user_id = userid)
			organiser.appoved_by_id = request.user.id
			organiser.status = 2
			organiser.save()
			return HttpResponseRedirect('/events/organiser/active/')
		else:
			raise Http404('Page not found !!')
	except:
		raise Http404('You are not allowed to view this page!')

@login_required
def rp_organiser_active(request):
	""" Resource person: List all active organiser under resource person states """
	#todo: filter and pagination
	user = request.user
	#if not user.is_authenticated() or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')

	user = User.objects.get(pk=user.id)
	try:
		organiser = Organiser.objects.filter(academic=Academic_center.objects.filter(state=State.objects.filter(resource_person__user_id=user)), status=1)
	except:
		organiser = {}
	context = {}
	context['collection'] = organiser
	context['active'] = True
	return render(request, 'events/templates/rp/organiser.html', context)

@login_required
def invigilator_request(request, username):
	""" Request to bacome a invigilator """
	user = request.user
	#if not user.is_authenticated():
	#	raise Http404('You are not allowed to view this page!')

	if username == user.username:
		user = User.objects.get(username=username)
		if request.method == 'POST':
			form = InvigilatorForm(request.POST)
			if form.is_valid():
				user.groups.add(Group.objects.get(name='invigilator'))
				invigilator = Invigilator()
				invigilator.user_id=request.user.id
				invigilator.academic_id=request.POST['college']
				invigilator.save()
				return HttpResponseRedirect("/events/invigilator/"+user.username+"/")
			context = {'form':form}
			return render(request, 'events/templates/invigilator/form.html', context)
		else:
			try:
				invigilator = Invigilator.objects.get(user=user)
				#todo: send status message
				if invigilator.status:
					print "you have already invigilator role !!"
					return HttpResponseRedirect("/events/invigilator/"+user.username+"/")
				else:
					print "invigilator not yet approve !!"
					return HttpResponseRedirect("/events/invigilator/"+user.username+"/")
			except:
				context = {}
				context.update(csrf(request))
				context['form'] = InvigilatorForm()
				return render(request, 'events/templates/invigilator/form.html', context)
	else:
		raise Http404('You are not allowed to view this page!')

@login_required
def invigilator_view(request, username):
	""" Invigilator view page """
	user = request.user
	#if not user.is_authenticated() or not is_invigilator(user) or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')
		
	if username == request.user.username or is_resource_person(request.user):
		user = User.objects.get(username=username)
		context = {}
		invigilator = Invigilator.objects.get(user=user)
		context['record'] = invigilator
		try:
			profile = invigilator.user.profile_set.get()
		except:
			profile = ''
		context['profile'] = profile
		return render(request, 'events/templates/invigilator/view.html', context)
	else:
		raise Http404('You are not allowed to view this page!')

@login_required
def invigilator_edit(request, username):
	""" Invigilator edit page """
	user = request.user
	#if not user.is_authenticated() or not is_invigilator(user) or not is_event_manager(user) or not is_resource_person(user):
	#	raise Http404('You are not allowed to view this page!')
		
	if username == user.username:
		user = User.objects.get(username=username)
		if request.method == 'POST':
			form = InvigilatorForm(request.POST)
			if form.is_valid():
				invigilator = Invigilator.objects.get(user=user)
				invigilator.user_id=request.user.id
				invigilator.academic_id=request.POST['college']
				invigilator.save()
				return HttpResponseRedirect("/events/invigilator/"+user.username+"/")
			context = {'form':form}
			return render(request, 'events/templates/invigilator/form.html', context)
		else:
				#todo : if any workshop and test under this invigilator disable the edit
				record = Invigilator.objects.get(user=user)
				context = {}
				context['form'] = InvigilatorForm(instance = record)
				context.update(csrf(request))
				return render(request, 'events/templates/invigilator/form.html', context)
	else:
		raise Http404('You are not allowed to view this page!')

#Ajax Request and Responces
@csrf_exempt
def ajax_ac_state(request):
	""" Ajax: Get University, District, City based State selected """
	if request.method == 'POST':
		state = request.POST.get('state')
		university = University.objects.filter(state=state)
		district = District.objects.filter(state=state)
		city = City.objects.filter(state=state)
		#state
		tmp = ''
		data = []
		for i in university:
			tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
		
		if(tmp):
			data.append('<option value = None> -- None -- </option>'+tmp)
		else:
			data.append(tmp)
			
		tmp = ''
		for i in district:
			tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
			
		if(tmp):
			data.append('<option value = None> -- None -- </option>'+tmp)
		else:
			data.append(tmp)
		
		tmp = ''
		for i in city:
			tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
			
		if(tmp):
			data.append('<option value = None> -- None -- </option>'+tmp)
		else:
			data.append(tmp)
		
		return HttpResponse(json.dumps(data), mimetype='application/json')
		
@csrf_exempt
def ajax_ac_location(request):
	""" Ajax: Get the location based on district selected """
	if request.method == 'POST':
		district = request.POST.get('district')
		location = Location.objects.filter(district=district)
		tmp = '<option value = None> -- None -- </option>'
		for i in location:
			tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
		return HttpResponse(json.dumps(tmp), mimetype='application/json')

@csrf_exempt
def ajax_ac_pincode(request):
	""" Ajax: Get the pincode based on location selected """
	if request.method == 'POST':
		location = request.POST.get('location')
		location = Location.objects.get(pk=location)
		return HttpResponse(json.dumps(location.pincode), mimetype='application/json')

@csrf_exempt
def ajax_district_collage(request):
	""" Ajax: Get the Colleges (Academic) based on District selected """
	if request.method == 'POST':
		district = request.POST.get('district')
		collages = Academic_center.objects.filter(district=district)
		tmp = '<option value = None> -- None -- </option>'
		for i in collages:
			tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
		return HttpResponse(json.dumps(tmp), mimetype='application/json')
