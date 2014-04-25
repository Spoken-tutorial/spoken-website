import hashlib
from django.contrib.auth.models import User, check_password
from models import MdlUser

class MdlBackend:
	supports_object_permissions = False
	supports_anonymous_user = False
	supports_inactive_user = False

	def authenticate(self, username=None, password=None):
		try:
			print " i am in moodle auth"
			user = MdlUser.objects.get(username=username)
			print "************"
			
			print user
			
			print "************"
			pwd = user.password
			uid = user.id
			firstname = user.firstname
			lastname = user.lastname
			email = user.email
			institute = user.institution
			department = user.department
			roll_number = user.idnumber
			p = hashlib.md5(password)
			pwd_valid =  (pwd == p.hexdigest())
			#print pwd
			#print "------------"
			#print p.hexdigest()
			if user and pwd_valid:
				#print " iam in auth2"
				#try:
				#	user = User.objects.get(username=username)
				#	return user
				#except Exception, e:
				#	new_user=User(id=uid, username=username, password=pwd, first_name=firstname, last_name=lastname, email=email)
				#	#new_user.save()
				#	print "No user here"
				#	#return new_user
				return user
		except Exception, e:
			print e
			print "except ---"
			return None

	def get_user(self, user_id):
		try:
			return User.objects.using('moodle').get(pk=user_id)
		except Exception, e:
			return None
