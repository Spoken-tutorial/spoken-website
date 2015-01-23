from django.db import models

# Create your models here.

class Learner(models.Model):
    fname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    roll_no = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    class Meta:
        unique_together = (("email"),)
