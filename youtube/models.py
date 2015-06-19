import pickle
import base64

from django.db import models
from django.contrib.auth.models import User

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField


class CredentialsModel(models.Model):
    id = models.OneToOneField(User, primary_key=True)
    credential = CredentialsField()

