
# Third Party Stuff
from django.contrib.auth.models import User
from django.db import models
#from oauth2client.contrib.django_util import CredentialsField
from oauthlib.oauth2 import ClientCredentialsGrant

class CredentialsModel(models.Model):
    id = models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT )
    credential = ClientCredentialsGrant()
