from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.shortcuts import render
from django.conf import settings
from shutil import copyfile
import random, string
import datetime
#from datetime import date, datetime, time, timedelta
import os, sys

from workshop.models import *
from events.models import *
from cms.models import Profile

def get_dept(dept):
    getDept = {
        ###
        'CSE' : 'Computer Science and Engineering',
        'cse' : 'Computer Science and Engineering',
        'cse ' : 'Computer Science and Engineering',
        'Dept. of Computer Science and Engineering' : 'Computer Science and Engineering',
        'Computer Science & Engineering' : 'Computer Science and Engineering',
        'DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING' : 'Computer Science and Engineering',
        'Computer Science Engineering' : 'Computer Science and Engineering',
        'Computer Science Engineering ' : 'Computer Science and Engineering',
        'Computer Science Engg.' : 'Computer Science and Engineering',
        'DEPARTMENT OF COMPUTER ENGINEERING' : 'Computer Science and Engineering',
        'Department of Computer Engineering' : 'Computer Science and Engineering',
        'Computer Engineering ' : 'Computer Science and Engineering',
        'Computer Engineering' : 'Computer Science and Engineering',
        'computer engineering' : 'Computer Science and Engineering',
        'COMPUTER ENGINEERING' : 'Computer Science and Engineering',
        'Computer engineering' : 'Computer Science and Engineering',
        'Department of Computer Science' : 'Computer Science and Engineering',
        'Department of Computer Science and Engineering' : 'Computer Science and Engineering',
        'Computer Sc and Engg' : 'Computer Science and Engineering',
        'Computer science and engineering department' : 'Computer Science and Engineering',
        'COMPUTER SCIENCE AND ENGINEERING DEPARTMENT' : 'Computer Science and Engineering',
        'CSE Department' : 'Computer Science and Engineering',
        'COMPUTER ENGG' : 'Computer Science and Engineering',
        
        ###
        'CST' : 'Computer Science and Technology',
        'Department of Computer Science and Technology' : 'Computer Science and Technology',
        
        ###
        'Information Tehnology' : 'Information Technology',
        'COMPUTER INFORMATION TECHNOLOGY' : 'Information Technology',
        'Department of Technology' : 'Information Technology',
        'IT' : 'Information Technology',
        'Department of IT' : 'Information Technology',
        'Department of Information Technology' : 'Information Technology',
        'computers and information technology' : 'Information Technology',
        'INFORMATION TECH' : 'Information Technology',
        
        ###
        'Department of Computer Application' : 'Computer Applications',
        'Department of Computer Applications' : 'Computer Applications',
        'Computer Applications' : 'Computer Applications',
        'BCA' : 'Computer Applications',
        'BCA-III Students' : 'Computer Applications',
        'Master of Computer' : 'Computer Applications',
        'BCA' : 'Computer Applications',
        'MCA' : 'Computer Applications',
        
        ###
        'Computer' : 'Computer Science',
        'Computer GU' : 'Computer Science',
        'cs' : 'Computer Science',
        'CS' : 'Computer Science',
        'School of Computer Science' : 'Computer Science',
        'School Of Computer Science' : 'Computer Science',
        'ComputerScience' : 'Computer Science',
        'computer Science Dept' : 'Computer Science',
        'Computer Scince' : 'Computer Science',
        'COMPUTERS' : 'Computer Science',
        'School of computer science' : 'Computer Science',
        'SCHOOL OF COMPUTER SCIENCE' : 'Computer Science',
        
        
        ###
        'ELECTRONICS AND COMMUNICATION ENGINEERING DEPARTME' : 'Electronics and Communication Engineering',
        'Dept. of Electronics and Communication Engineering' : 'Electronics and Communication Engineering',
        'ECE' : 'Electronics and Communication Engineering',
        'Electrical and Communication Engineering' : 'Electronics and Communication Engineering',
        'EC' : 'Electronics and Communication Engineering',
        'ELECTRONICS AND COMMUNICATION' : 'Electronics and Communication Engineering',
        'EC Department' : 'Electronics and Communication Engineering',
        'EXTC' : 'Electronics and Communication Engineering',
        'EECE' : 'Electronics and Communication Engineering',
        'Electronics and Communication' : 'Electronics and Communication Engineering',
        
        ###
        'EEE' : 'Electrical and Electronics Engineering',
        'Department of Electrical and Electronics Engineeri' : 'Electrical and Electronics Engineering',
        'electrical and electronics' : 'Electrical and Electronics Engineering',
        'ELECTRONICCS' : 'Electrical and Electronics Engineering',
        'electronics' : 'Electrical and Electronics Engineering',
        'Electronics' : 'Electrical and Electronics Engineering',
        
        ###
        'ETC' : 'Electronics and Telecommunication',
        
        ###
        #'Electrical Engineering'
        
        ###
        'INSTRUMENTATION AND CONTROL' : 'Electronics and instrumentation Engineering',
        'INSTRUMENTATION ENGINEERING' : 'Electronics and instrumentation Engineering',
        
        ###
        'ME' : 'Mechanical Engineering',
        ' PRODUCTION ENGINEERING' : 'Mechanical Engineering',
        'Mechanical' : 'Mechanical Engineering',
        'MECHANICAL' : 'Mechanical Engineering',
        
        ###
        'Civil' : 'Civil Engineering',
        'CIVIL' : 'Civil Engineering',
        'CE' : 'Civil Engineering',
        
        ###
        'AERONAUTICAL' : 'Aeronautical Engineering',
        
        ###
        'E&TC' : 'Electronics and Telecommunication',
        'Electronics & Telecomunication' : 'Electronics and Telecommunication',
        'E&TC ENGINEERING' : 'Electronics and Telecommunication',
        
        ###
        'EE' : 'Electronics Engineering',
        'Department of Electronics' : 'Electronics Engineering',
        'ELECTRONIC ' : 'Electronics Engineering',
        
        ###
        'FDP' : 'Faculty Development Program',
        'All(Faculity Members, FDP)' : 'Faculty Development Program',
        'Central Library KKHSOU' : 'Faculty Development Program',
        'Central Library' : 'Faculty Development Program',
        'Faculty' : 'Faculty Development Program',
        'Library' : 'Faculty Development Program',
        'THE FUTURE COMPUTER SCIENCE COLLEGE' : 'Faculty Development Program',
        'Sowdambika Polytechnic College ' : 'Faculty Development Program',
        'Future Computer Science College' : 'Faculty Development Program',
        'Kamani Science College' : 'Faculty Development Program',
        'P S HIRPARA MAHILA COLLEGE' : 'Faculty Development Program',
        'MCA staff and faculty' : 'Faculty Development Program',
        'Administrative' : 'Faculty Development Program',
        'Telecommunication and Engineering ' : 'Telecommunication Engineering',
        'GYANBHARTI COMPUTER SCIENCE COLLEGE' : 'Faculty Development Program',
        'G K C K BOSAMIYA COLLEGE' : 'Faculty Development Program',
        'VARMORA COLLEGE' : 'Faculty Development Program',
        'GAJERA SANKUL' : 'Faculty Development Program',
        'Morigaon College' : 'Faculty Development Program',
        
        ###
        #Chemical Engineering
        
        ###
        'MATHEMATICS' : 'Applied Mathematics',
        'DEPARTMENT OF MATHEMATICS' : 'Applied Mathematics',
        'Mathematics' : 'Applied Mathematics',
        
        ###
        'BTECH' : 'Batchelor of Tehchnology',
        
        ###
        'Department of Physics' : 'Physics',
        'Physics' : 'Physics',
        
        ###
        'Information Science' : 'Information Science',
        
        ###
        'ECE, IT, CSE, EEE, MCA' : 'ECE,IT,CSE,EEE,MCA',
        'CSE & IT' : 'CSE,IT',
        'E&TC and CS' : 'ECE,CS',
        'CSE MCA' : 'CSE,MCA',
        'CSEIT' : 'CSE,IT',
        'ECE CIVIL CSE' : 'ECE,CIVIL,CSE',
        'CSE IT ' : 'CSE,IT',
        'CSE IT MCA' : 'CSE,IT,MCA',
        'EEE ECE' : 'EEE,ECE',
        'EEE ECE' : 'EEE,ECE',
        'MAC BTECH' : 'MCA,BTECH',
        'Civil Mech' : 'Civil,Mechanical',
        'Civil Mechanical' : 'Civil,Mechanical',
        'Computer and IT Department' : 'CS,IT',
        'Information Technology and Computer science and en' : 'IT,CSE',
        'IT and Computer Science' : 'IT,CS',
        'School of Elect. Engg and IT': 'EE,IT',
        'BCA B.Com B.SC' : 'BCA,Commerce and Management,CS',
        'School of Chemical and Biotechnology' : 'Chemical Engineering,Biotechnology',
        'Computational Biology and Bioinformatics' : 'Biology,Bioinformatics',
        
        ### Uncategorized
        '50' : 'Others',
        'Common to all Branches - 1st semester' : 'Others',
        'Linux' : 'Others',
        'BSH' : 'Others',
        'KTurtle Pilot Workshop for class VII students' : 'Others',
        'COPA' : 'Others',
        'TechFest-2013 participants' : 'Others',
        'CSI-IT2020 Participants' : 'Others',
        'Open to All' : 'Others',
        'ALL' : 'Others',
        'Others' : 'Others',
        'others' : 'Others',
        'Oceanography' : 'Oceanography',
        '' : 'Others',
    }
    #print "**********************"
    #print dept
    #print getDept[dept]
    #print "**********************"
    return getDept[dept]
    
def department(request):
    wd = WDepartments.objects.all().values_list('name')
    wwrd = WWorkshopRequests.objects.exclude(department__in = wd).values_list('department').distinct()
    #print list(wwrd)
    newDept = [
        'Batchelor of Tehchnology',
        'Others',
        'Electronics Engineering',
        'Faculty Development Program',
        'Physics',
        'Oceanography',
        'Information Science',
        'Computer Applications',
        'Computer Science and Technology',
        'Biotechnology',
        'Bioinformatics',
        'Biology'
    ]
    for dept in newDept:
        try:
            Department.objects.get(name = dept)
        except Exception, e:
            Department.objects.create(name = dept)
            print e
    
    return HttpResponse("Department migration complted!")

def states(request):
    wstate = WStates.objects.all()
    for ws in wstate:
        try:
            s = State.objects.get(name=ws.name)
            s.code = ws.code.upper()
            s.latitude = ws.latitude
            s.longitude = ws.longitude
            s.image_map_area = ws.image_map_area
            s.save()
        except Exception, e:
            print e
            State.objects.create(code = ws.code, name = ws.name)
            print "created => ", ws.name
    return HttpResponse("States migration complted!")

def academic_center(request):
    state_list = {'' : 36L, 'ANP' : 2L, 'ANR' : 1L, 'ARP' : 3L, 'ASM' : 4L, 'BHR' : 5L, 'CHG' : 6L, 'CTG' : 7L, 'DDU' : 9L, 'DEL' : 10L, 'DNG' : 8L, 'GOA' : 11L, 'GUJ' : 12L, 'HAR' : 13L, 'HMP' : 14L, 'INL' : 37L, 'JHD' : 16L, 'JNK' : 15L, 'KAR' : 17L, 'KER' : 18L, 'LKD' : 19L, 'MAH' : 21L, 'MAN' : 22L, 'MDP' : 20L, 'MEG' : 23L, 'MIZ' : 24L, 'NAG' : 25L, 'ODI' : 26L, 'PCY' : 27L, 'PJB' : 28L, 'RAJ' : 29L, 'SIK' : 30L, 'TAM' : 31L, 'TRP' : 32L, 'UTK' : 34L, 'UTP' : 33L, 'WBN' : 35L}
    wacs = WAcademicCenter.objects.all()
    for wac in wacs:
        try:
            ac = AcademicCenter.objects.get(academic_code = wac.academic_code)
            #print "Already exits => ", wac.academic_code
        except Exception, e:
            #print e,
            #print " Not exits =>", wac.academic_code
            try:
                #print "Create new Academic Center .."
                it = InstituteType.objects.get(name="Uncategorized")
                ic = InstituteCategory.objects.get(name="Uncategorized")
                u = University.objects.get(name="Uncategorized")
                d = District.objects.get(name="Uncategorized")
                c = City.objects.get(name="Uncategorized")
                
                ac = AcademicCenter()
                ac.user_id = 1
                ac.state_id = state_list[str(wac.state_code)]
                ac.academic_code = wac.academic_code.upper()
                ac.school_college = wac.school_college
                ac.institution_name = wac.institution_name.strip()
                ac.address = wac.street
                ac.resource_center = wac.resource_center
                ac.rating = wac.star_rating
                ac.contact_person = wac.contact_details
                ac.remarks = wac.remarks
                
                ac.institution_type_id = it.id
                ac.institute_category_id = ic.id
                ac.university_id = u.id
                ac.district_id = d.id
                ac.city_id = c.id
                ac.status = 1
                
                if wac.pincode:
                    ac.pincode = wac.pincode
                else:
                    ac.pincode = 0
                
                if wac.created_at:
                    ac.created = wac.created_at
                    ac.updated = wac.updated_at
                else:
                    ac.created = datetime.datetime.now()
                    ac.updated = datetime.datetime.now()
                    
                ac.save()
            except Exception, e:
                print "********************"
                print e
                print "Failed while creating ...", wac.academic_code
                print "********************"
                
    return HttpResponse("AcademicCenter migration complted!")

def organiser(request):
    worganisers = WOrganiser.objects.all()
    for wo in worganisers:
        try:
            o = Organiser.objects.get(user_id  = wo.organiser_id)
            print "Organiser Already Exits!", wo.organiser_id
            continue
        except Exception, e:
            #print e
            #print "*********** => 1"
            try:
                #find academic_id
                if 'ANR' in wo.academic_code:
                    continue
                
                try:
                    ac = AcademicCenter.objects.get(academic_code = wo.academic_code)
                except Exception, e:
                    print e
                    print "******* Getting workshop academic code *********"
                    wwr = WWorkshopRequests.objects.filter(organiser_id = wo.organiser_id).first()
                    if not wwr:
                        print "******* workshop academic code not there ******", wo.organiser_id
                        continue
                    ac = AcademicCenter.objects.get(academic_code = wwr.academic_code)
                #profile
                try:
                    p = Profile.objects.get(user_id = wo.organiser_id)
                except Exception, e:
                    #print e
                    #print "*********** => 2"
                    try:
                        confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
                        p = Profile()
                        p.user_id = wo.organiser_id
                        p.confirmation_code = confirmation_code
                        p.address = wo.address
                        p.phone = wo.phone
                        p.save()
                    except Exception, e:
                        print "User not exits", wo.organiser_id
                        sys.exit(0)
                    
                #save organiser name ad user first name
                try:
                    u = User.objects.get(pk = wo.organiser_id)
                    u.first_name = wo.organiser_name
                    u.save()
                    try:
                        u.groups.add(Group.objects.get(name='Organiser'))
                    except Exception, e:
                        print e
                        
                except Exception, e:
                    print e
                    print "*********** => 3", wo.organiser_id
                    #print "User not exits => ", wo.organiser_id
                try:
                    o = Organiser()
                    o.user_id  = wo.organiser_id
                    o.academic_id = ac.id
                    o.status = 1
                    if wo.created_at:
                        o.created = wo.created_at
                        o.updated = wo.updated_at
                    else:
                        o.created = datetime.datetime.now()
                        o.updated = datetime.datetime.now()
                    
                    o.save()
                except Exception, e:
                    print e
                    #print "******** 4 "
                    
            except Exception, e:
                print e
                print "*********** => 5 => ", wo.organiser_id
                print "Something went wrong"
                
    return HttpResponse("Organiser migration Done!")

def invigilator(request):
    winvigilators = WInvigilator.objects.all()
    for wo in winvigilators:
        try:
            o = Invigilator.objects.get(user_id  = wo.invigilator_id)
            print "Invigilator Already Exits!", wo.invigilator_id
            continue
        except Exception, e:
            #print e
            #print "*********** => 1"
            try:
                #find academic_id
                if 'ANR' in wo.academic_code:
                    continue
                
                try:
                    ac = AcademicCenter.objects.get(academic_code = wo.academic_code)
                except Exception, e:
                    print e
                    print "******* Getting workshop academic code *********"
                    wwr = WTestRequests.objects.filter(invigilator_id = wo.invigilator_id).first()
                    if not wwr:
                        print "******* workshop academic code not there ******", wo.invigilator_id
                        continue
                    ac = AcademicCenter.objects.get(academic_code = wwr.academic_code)
                #profile
                try:
                    p = Profile.objects.get(user_id = wo.invigilator_id)
                except Exception, e:
                    #print e
                    #print "*********** => 2"
                    try:
                        confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
                        p = Profile()
                        p.user_id = wo.invigilator_id
                        p.confirmation_code = confirmation_code
                        p.address = wo.address
                        p.phone = wo.phone
                        p.save()
                    except Exception, e:
                        print "User not exits", wo.invigilator_id
                        sys.exit(0)
                    
                #save invigilator name ad user first name
                try:
                    u = User.objects.get(pk = wo.invigilator_id)
                    u.first_name = wo.invigilator_name
                    u.save()
                    try:
                        u.groups.add(Group.objects.get(name='Invigilator'))
                    except Exception, e:
                        print e
                        
                except Exception, e:
                    print e
                    print "*********** => 3", wo.invigilator_id
                    #print "User not exits => ", wo.invigilator_id
                try:
                    o = Invigilator()
                    o.user_id  = wo.invigilator_id
                    o.academic_id = ac.id
                    o.status = 1
                    if wo.created_at:
                        o.created = wo.created_at
                        o.updated = wo.updated_at
                    else:
                        o.created = datetime.datetime.now()
                        o.updated = datetime.datetime.now()
                    
                    o.save()
                except Exception, e:
                    print e
                    #print "******** 4 "
                    
            except Exception, e:
                print e
                print "*********** => 5 => ", wo.invigilator_id
                print "Something went wrong"
                
    return HttpResponse("Invigilator migration Done!")

#MAH-00029 Live workshop
def workshop(request):
    workshop_status = 1
    if workshop_status == 2:
        wwrs = WWorkshopRequests.objects.filter(status = workshop_status)
    elif workshop_status == 1:
        wwrs = WWorkshopRequests.objects.filter(status = workshop_status, pref_wkshop_date__gte = datetime.datetime.today())
    else:
        wwrs = WWorkshopRequests.objects.filter(status = workshop_status, pref_wkshop_date__gte = datetime.datetime.today())
        
    for wwr in wwrs:
        #Save department
        try:
            
            # Save Workshop
            w = None
            try:
                w = Training.objects.get(training_code = wwr.workshop_code)
                #print "Already exits !"
                continue
            except Exception, e:
                if not wwr.workshop_code and wwr.status == 2:
                    continue
                if not wwr.workshop_code:
                    wwr.workshop_code = "WC-"+str(wwr.id)
                print e, " => 3 ", wwr.workshop_code
            #check organiser there or not
            organiser = None
            try:
                organiser = Organiser.objects.get(user_id = wwr.organiser_id)
            except Exception, e:
                #print e
                print "Organiser Not there => ", wwr.organiser_id
                continue
                
            #check dept in WDepartments
            wdept = wwr.department
            try:
                WDepartments.objects.get(name=wdept)
            except Exception, e:
                #print e, " => 1", wwr.workshop_code
                wdept = get_dept(wdept)
            
            # check in Department
            dept = None
            try:
                dept = Department.objects.get(name=wdept)
            except Exception, e:
                print e, " => 2",
                if ',' in wdept:
                    cwdept = wdept.split(',');
                    for d in cwdept:
                        try:
                            d = Department.objects.get(name = d)
                        except Exception, e:
                            print e, " => 2aa ", wwr.workshop_code, " => ", d
                            d = get_dept(d)
                        try:
                            Department.objects.get(name=d)
                        except Exception, e:
                            print e, " => 2ab ", wwr.workshop_code, " => ", d
                            sys.exit(0)
                #dept = Department.objects.create(name = wdept)
            
            #find academic_center id
            ac = None
            try:
                ac = AcademicCenter.objects.get(academic_code = wwr.academic_code)
            except Exception, e:
                #print e, " => 4 ", wwr.academic_code, wwr.workshop_code
                if '-- select ' == wwr.academic_code:
                    o = Organiser.objects.get(organiser_id = wwr.organiser_id)
                    ac = AcademicCenter.objects.get(academic_code = o.academic_code)
                
                #get organiser academic and set to workshop
                try:
                    o  = Organiser.objects.get(user_id = wwr.organiser_id)
                    ac = AcademicCenter.objects.get(pk = o.academic_id)
                except Exception, e:
                    print e, "=> 4aa "
                    
                continue
            
            #find foss_category_id
            foss = None
            try:
                if wwr.foss_category == 'Linux-Ubuntu':
                    wwr.foss_category = 'Linux'
                foss = FossCategory.objects.get(foss = wwr.foss_category.replace("-", " "))
            except Exception, e:
                print e, " => 5 ", wwr.foss_category
                continue
                
             #find language_id
            lang = None
            try:
                lang = Language.objects.get(name = wwr.pref_language)
            except Exception, e:
                print e, " => 6 ", wwr.pref_language
                continue
            
            # get participants count
            if workshop_status == 2:
                wp = None
                try:
                    wp = WWorkshopDetails.objects.get(workshop_code = wwr.workshop_code)
                except Exception, e:
                    print e, " => 7 ", wwr.workshop_code
                    continue
            elif workshop_status == 1:
                try:
                    WWorkshopFeedback.objects.filter(workshop_code = wwf.workshop_code).count()
                    wp = WWorkshopDetails.objects.get(workshop_code = wwr.workshop_code)
                    print "7aaa,  yes yes", wwr.workshop_code
                except Exception, e:
                    pass
            else:
                pass
                
            # new status
            wstatus = {0 : 0, 1 : 0, 2 : 4}
            w = Training()
            w.organiser_id = organiser.id
            w.training_code = wwr.workshop_code.upper()
            w.academic_id = ac.id
            w.foss_id = foss.id
            w.language_id = lang.id
            if workshop_status == 2:
                w.trdate = wwr.cfm_wkshop_date
                w.trtime = wwr.cfm_wkshop_time
            else:
                w.trdate = wwr.pref_wkshop_date
                w.trtime = wwr.pref_wkshop_time
            w.status = wstatus[wwr.status]
            w.skype = wwr.skype_request
            
            if 'MAH-00029' == wwr.academic_code:
                w.training_type = 2
            else:
                w.training_type = 1
            
            w.course_id = 1
            if workshop_status == 2:
                w.participant_counts = wp.no_of_participants
            else:
                w.participant_counts = 0
            
            if wwr.created_at:
                w.created = wwr.created_at
                w.updated = wwr.updated_at
            else:
                w.created = datetime.datetime.now()
                w.updated = datetime.datetime.now()
            try:
                #continue
                w.save()
            except Exception, e:
                print "Duplicate ---", wwr.workshop_code, " => ", wwr.academic_code, wwr.cfm_wkshop_date, wwr.foss_category
                post_time = 5
                for i in range(150):
                    try:
                        post_five_min = datetime.datetime.combine(datetime.date.today(), wwr.cfm_wkshop_time) + datetime.timedelta(minutes=post_time)
                        w.trtime = post_five_min.time()
                        w.save()
                        break
                    except Exception, e:
                        #duplicate because of unique_together
                        print "Duplicate post change time save ******", wwr.workshop_code, " => ", wwr.academic_code, wwr.cfm_wkshop_date, 
                        if i == 149:
                            sys.exit(0)
                        post_time = post_time + 5
                        continue
            
            #save departments
            try:
                try:
                    d = Department.objects.get(name = wdept)
                    w.department.add(d)
                    w.save()
                except Exception, e:
                    if ',' in wdept:
                        cwdept = wdept.split(',');
                        #print "*********", cwdept
                        #w.department.clear()
                        for dept in cwdept:
                            try:
                                dept = Department.objects.get(name = dept)
                            except Exception, e:
                                print e, " => sss ", wwr.workshop_code, " => ", dept
                                dept = get_dept(dept)
                                
                            dept = Department.objects.get(name = dept)
                            w.department.add(dept)
                    w.save()
            
            except Exception, e:
                print e, " => 8", wwr.workshop_code, " => ", wdept
                w.delete()
                sys.exit(0)
            
        except Exception, e:
            print "Something went wrong!"
            print e, " => 9", wwr.id," => ", wwr.workshop_code
            print "Organiser => ", wwr.organiser_id
            #sys.exit(0)
            continue
    return HttpResponse("Workshop migration Done!")
    

def workshop_feedback(request):
    wwfs = WWorkshopFeedback.objects.all()
    for wwf in wwfs:
        #existing record
        try:
            TrainingFeedback.objects.get(training_id = training.id, mdluser_id = wwf.user_id )
            continue
        except:
            pass
        # find the training id
        training = None
        try:
            training = Training.objects.get(training_code = wwf.workshop_code)
        except Exception, e:
            print e, " => 1 ", wwf.workshop_code, " => ", wwf.user_id, " => ", wwf.id
            
            #get the workshop form WWorkshopRequests where status = 3
            wpc = WWorkshopFeedback.objects.filter(workshop_code = wwf.workshop_code).count()
            #if wpc > 0:
            #    training.status = 4
            #    training.participant_counts = wpc
            #    training.save()
            #    print "Workshop Details fil", wwf.workshop_code, " => p ", wpc
            #else:
            continue
            #sys.exit()
        
         #find language_id
        lang = None
        try:
            lang = Language.objects.get(name = wwf.workshop_language)
        except Exception, e:
            #todo: if reginal get language from w
            try:
                if wwf.workshop_language == 'Regional':
                    te = Training.objects.get(training_code = wwf.workshop_code)
                    lang = Language.objects.get(name = te.language)
                else:
                    lang = Language.objects.get(name = 'English')
            except Exception, ee:
                print e, " => 6 ", wwf.workshop_language
                print ee, " => 6aa ", wwf.workshop_language
                continue
                
        try:
            TrainingFeedback.objects.get(training_id = training.id, mdluser_id = wwf.user_id )
            #print "already exits!"
            continue
        except Exception, e:
            print e, " => 2", wwf.workshop_code, " => ", wwf.user_id
            try:
                t = TrainingFeedback()
                t.mdluser_id  = wwf.user_id
                t.training_id  = training.id
                t.rate_workshop  = wwf.rate_workshop
                t.content  = wwf.content
                t.sequence  = wwf.logical_arrangement
                t.clarity  = wwf.clarity
                t.interesting  = wwf.understandable
                t.appropriate_example  = wwf.included_examples
                t.instruction_sheet  = wwf.instruction_sheet
                t.assignment  = wwf.assignments
                t.pace_of_tutorial  = wwf.pace_tutorial
                t.workshop_learnt  = wwf.useful_thing
                t.weakness_workshop  = wwf.weakness_duration
                t.weakness_narration  = wwf.weakness_narration
                t.weakness_understand  = wwf.weakness_understand
                t.other_weakness  = wwf.other_weakness
                t.tutorial_language  = lang.id
                t.apply_information  = wwf.info_received
                t.setup_learning  = wwf.comfortable_learning
                t.computers_lab  = wwf.working_computers
                t.audio_quality  = wwf.audio_quality
                t.video_quality  = wwf.video_quality
                t.workshop_orgainsation  = wwf.orgn_wkshop
                t.faciliate_learning  = wwf.facil_learning
                t.motivate_learners  = wwf.motiv_learning
                t.time_management  = wwf.time_mgmt
                t.knowledge_about_software  = wwf.soft_klg
                t.provide_clear_explanation  = wwf.prov_expn
                t.answered_questions  = wwf.ans_cln
                t.interested_helping  = wwf.help_lern
                t.executed_workshop  = wwf.exec_effly
                t.workshop_improved  = wwf.ws_improved
                t.recommend_workshop  = wwf.recomm_wkshop
                t.use_information  = wwf.reason_why
                t.other_comments  = wwf.general_comment
                
                if wwf.updated_at:
                    t.created  = wwf.updated_at
                else:
                    t.created  = datetime.datetime.now()
                t.save()
                
                #Save training attendance register
                #try:
                #    TrainingAttendance.objects.get()
                #except Exception, e:
                #    pass
            except Exception, e:
                print e, " => 3", wwf.workshop_code, " => ", wwf.user_id
                sys.exit()
    return HttpResponse("Workshop Feedback migration Done!")
    
    
def test(request):
    test_status = 3
    wtrs = WTestRequests.objects.filter(status = test_status)
    for wtr in wtrs:
        #Save department
        try:
            
            # Save Workshop
            w = None
            try:
                w = Test.objects.get(test_code = wtr.test_code)
                #print "Already exits !"
                continue
            except Exception, e:
                print e, " => 3 ", wtr.test_code, wtr.academic_code
                if not wtr.test_code:
                    wtr.test_code = "TC-"+str(wtr.id)
            
            #check organiser there or not
            organiser = None
            try:
                organiser = Organiser.objects.get(user_id = wtr.organiser_id)
            except Exception, e:
                #print e
                print "Organiser Not there => ", wtr.organiser_id
                continue
            
            #check organiser there or not
            invigilator = None
            try:
                invigilator = Invigilator.objects.get(user_id = wtr.invigilator_id)
            except Exception, e:
                print e
                print "Invigilator Not there => ", wtr.invigilator_id
                if not wtr.invigilator_id:
                    try:
                        ac = AcademicCenter.objects.get(academic_code = wtr.academic_code)
                        invigilator = Invigilator.objects.filter(academic_id = ac.id).first()
                        invigilator.id
                        print invigilator, "Invigilator found!"
                    except Exception, e:
                        print e, " => AC ", wtr.academic_code
                        continue
                else:
                    #sys.exit(0)
                    continue
                
            #check dept in WDepartments
            wdept = wtr.department
            try:
                WDepartments.objects.get(name=wdept)
            except Exception, e:
                #print e, " => 1", wtr.test_code
                wdept = get_dept(wdept)
            
            # check in Department
            dept = None
            try:
                dept = Department.objects.get(name=wdept)
            except Exception, e:
                print e, " => 2",
                if ',' in wdept:
                    cwdept = wdept.split(',');
                    for d in cwdept:
                        try:
                            d = Department.objects.get(name = d)
                        except Exception, e:
                            print e, " => 2aa ", wtr.test_code, " => ", d
                            d = get_dept(d)
                        try:
                            Department.objects.get(name=d)
                        except Exception, e:
                            print e, " => 2ab ", wtr.test_code, " => ", d
                            sys.exit(0)
                #dept = Department.objects.create(name = wdept)
            
            #find academic_center id
            ac = None
            try:
                ac = AcademicCenter.objects.get(academic_code = wtr.academic_code)
            except Exception, e:
                #print e, " => 4 ", wtr.academic_code, wtr.test_code
                if '-- select ' == wtr.academic_code:
                    o = Organiser.objects.get(organiser_id = wtr.organiser_id)
                    ac = AcademicCenter.objects.get(academic_code = o.academic_code)
                
                #get organiser academic and set to workshop
                try:
                    o  = Organiser.objects.get(user_id = wtr.organiser_id)
                    ac = AcademicCenter.objects.get(pk = o.academic_id)
                except Exception, e:
                    print e, "=> 4aa "
                    
                continue
            
            #find foss_category_id
            foss = None
            try:
                if wtr.foss_category == 'Linux-Ubuntu':
                    wtr.foss_category = 'Linux'
                foss = FossCategory.objects.get(foss = wtr.foss_category.replace("-", " "))
            except Exception, e:
                print e, " => 5 ", wtr.foss_category
                continue
            
            # get participants count
            wp = None
            try:
                wp =WTestDetails.objects.get(test_code = wtr.test_code)
            except Exception, e:
                print e, " => 7 ", wtr.test_code
                continue
            
                
            # new status
            #wstatus = {0 : 0, 1 : 1, 2 : 4}
            w = Test()
            w.organiser_id = organiser.id
            w.invigilator_id = invigilator.id
            w.test_code = wtr.test_code.upper()
            w.academic_id = ac.id
            w.foss_id = foss.id
            w.tdate = wtr.cfm_test_date
            w.ttime = wtr.cfm_test_time
            w.status = wtr.status
            
            w.test_category_id = 1
            
            w.participant_count = wp.no_of_participants
            
            if wtr.created_at:
                w.created = wtr.created_at
                w.updated = wtr.updated_at
            else:
                w.created = datetime.datetime.now()
                w.updated = datetime.datetime.now()
            try:
                #continue
                w.save()
            except Exception, e:
                print e, "Duplicate ---", wtr.test_code, " => ", wtr.academic_code, wtr.cfm_test_date, wtr.foss_category
                #sys.exit(0)
                post_time = 5
                for i in range(5):
                    try:
                        post_five_min = datetime.datetime.combine(datetime.date.today(), wtr.cfm_test_time) + datetime.timedelta(minutes=post_time)
                        w.ttime = post_five_min.time()
                        w.save()
                        break
                    except Exception, e:
                        #duplicate because of unique_together
                        print e, "Duplicate post change time save ******", wtr.test_code, " => ", wtr.academic_code, wtr.cfm_test_date, 
                        if i == 4:
                            sys.exit(0)
                        post_time = post_time + 5
                        continue
            
            #save departments
            try:
                try:
                    d = Department.objects.get(name = wdept)
                    w.department.add(d)
                    w.save()
                except Exception, e:
                    if ',' in wdept:
                        cwdept = wdept.split(',');
                        #print "*********", cwdept
                        #w.department.clear()
                        for dept in cwdept:
                            try:
                                dept = Department.objects.get(name = dept)
                            except Exception, e:
                                print e, " => sss ", wtr.test_code, " => ", dept
                                dept = get_dept(dept)
                                
                            dept = Department.objects.get(name = dept)
                            w.department.add(dept)
                    w.save()
            
            except Exception, e:
                print e, " => 8", wtr.test_code, " => ", wdept
                w.delete()
                sys.exit(0)
            
        except Exception, e:
            print "Something went wrong!"
            print e, " => 9", wtr.id," => ", wtr.test_code
            print "Organiser => ", wtr.organiser_id
            sys.exit(0)
            continue
    return HttpResponse("Test migration Done!")
    
def test_attendance(request):
    tas = WAttendanceRegister.objects.all()
    for ta in tas:
        #check test
        test = None
        try:
            test = Test.objects.get(test_code = ta.test_code)
        except Exception, e:
            print e, " => ", ta.test_code, ta.moodle_uid
            continue
        
        try:
            TestAttendance.objects.get(test_id = test.id, mdluser_id = ta.moodle_uid)
            print "Already Exits"
            continue
        except Exception, e:
            print e, " => 1", ta.test_code, ta.moodle_uid
            
            t = TestAttendance()
            t.mdluser_id = ta.moodle_uid
            t.test_id = test.id
            t.status = 4
            t.created = datetime.datetime.now()
            t.updated = datetime.datetime.now()
            t.save()
        
    return HttpResponse("Test attendance migration Done!")
    
