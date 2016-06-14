# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Third Party Stuff
from django.db import models

# Spoken Tutorial Stuff
from creation.models import FossCategory


class Learner(models.Model):
    fname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    foss = models.ForeignKey(FossCategory, null=True)
    roll_no = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = (("email"),)
