from django.db import models
from django.contrib.auth.models import User
from .helpers import GENDER_CHOICES, PAY_FOR_CHOICES
from creation.models import FossCategory, Language
import uuid

class Payment(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    country = models.CharField(max_length=50,null=True)
    state = models.CharField(max_length=50,null=True)
    city =  models.CharField(max_length=75,null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    key = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expiry = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User,on_delete=models.PROTECT,related_name="payment_user" )
 
class CdFossLanguages(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT,related_name="payment_foss")
    lang = models.ForeignKey(Language)

class PaymentTransaction(models.Model):
    paymentdetail = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="payment_transaction" )
    requestType = models.CharField(max_length=2)
    amount = models.CharField(max_length=20)
    reqId = models.CharField(max_length=50)
    transId = models.CharField(max_length=100)
    refNo = models.CharField(max_length=50)
    provId = models.CharField(max_length=50)
    status = models.CharField(max_length=2)
    msg = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)