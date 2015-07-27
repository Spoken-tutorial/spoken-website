import os, sys
import random, string

# setting django environment
from django.core.wsgi import get_wsgi_application
sys.path.append("/websites_dir/django_spoken/spoken")
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

# importing config and other packages needed
from config import *
from cms.models import Profile
from django.db.models import Q
from django.contrib.auth.models import Group, User

# users = User.objects.filter(is_active=True).exclude(id__in=Profile.objects.all().values_list('user_id'))
users = User.objects.exclude(id__in=Profile.objects.all().values_list('user_id')).all()
print '*********************'
print ' ', users.count()
print '*********************'
for user in users:
  confirmation_code = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(33))
  print 'processing user:', user.id, confirmation_code
  p = Profile(user=user, confirmation_code=confirmation_code)
  p.save()
