# Third Party Stuff
from builtins import object
from django.db import models

# Spoken Tutorial Stuff
from creation.models import FossCategory


class Learner(models.Model):
    fname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    foss = models.ForeignKey(FossCategory, null=True, on_delete=models.PROTECT )
    roll_no = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    class Meta(object):
        unique_together = (("email"),)
