# Standard Library
import base64
import pickle

# Third Party Stuff
from django.contrib.auth.models import User
from django.db import models
from oauth2client.django_orm import CredentialsField, FlowField


class CredentialsModel(models.Model):
    id = models.OneToOneField(User, primary_key=True)
    credential = CredentialsField()
