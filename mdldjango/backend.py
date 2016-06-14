# Standard Library
import hashlib

# Third Party Stuff
from django.contrib.auth.models import User
from models import MdlUser


class MdlBackend:
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        try:
            user = MdlUser.objects.get(username=username)
            pwd = user.password
            p = hashlib.md5(password)
            pwd_valid = (pwd == p.hexdigest())
            if user and pwd_valid:
                return user
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.using('moodle').get(pk=user_id)
        except Exception:
            return None
