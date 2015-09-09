from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist

def get_or_create_user(instance, password=None):
	user = None
	instance.email = instance.email.lower()
	instance.username = instance.email
	instance.firstname = instance.firstname.upper()
	instance.lastname = instance.lastname.upper()
	instance.save()
	flag = 0
	try:
		user = User.objects.get(email=instance.email)
	except ObjectDoesNotExist:
		user = User.objects.create_user(instance.email, instance.email, instance.firstname)
		flag = 1
	if user:
		user.first_name = instance.firstname
		user.last_name = instance.lastname
		user.save()
		if password:
			user.set_password(password)
		try:
			student_group = Group.objects.get(name = 'Student')
			user.groups.add(student_group)
		except:
			pass
	return instance, flag, user
	
def revoke_student_permission(sender, instance, *args, **kwargs):
  try:
    group = instance.user.groups.get(name='Student')
    group.user_set.remove(instance.user)
  except:
    pass
