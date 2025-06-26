# Third Party Stuff
from builtins import object
from django.db import models
from django.core.exceptions import ValidationError
import ipaddress

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

class WhitelistedIP(models.Model):
    ip_address = models.CharField(max_length=43, unique=True, help_text="Enter an IP address or CIDR range (IPv4/IPv6)")  
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.ip_address

    def clean(self):
        try:
            ipaddress.ip_network(self.ip_address, strict=False)
        except ValueError:
            raise ValidationError({'ip_address': "Invalid IP or CIDR notation."})
