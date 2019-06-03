
# Third Party Stuff
from django.contrib.auth.models import User
from django.db import models

class CredentialsModel(models.Model):
    id = models.OneToOneField(User, primary_key=True, on_delete=models.PROTECT )
    credential = models.TextField(null=True)
