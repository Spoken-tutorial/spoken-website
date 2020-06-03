from django.db import models
from django.contrib.auth.models import User
from .helpers import GENDER_CHOICES, PAY_FOR_CHOICES
from creation.models import FossCategory, Language


class Corporate(models.Model):
    name = models.CharField(max_length=255)	
    state = models.CharField(max_length=255)
    deparment = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)

class PaymentDetails(models.Model):
    user = models.ForeignKey(User,blank=True,on_delete=models.PROTECT,related_name='paying_user')
    amount = models.CharField(max_length=20)
    purpose = models.CharField(max_length=20, null=True)
    status = models.PositiveIntegerField()
    description = models.CharField(max_length=20, null=True)
    gstno = models.CharField(max_length=15,null=True)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now_add = True)


class Payee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    country = models.CharField(max_length=50,null=True)
    state = models.CharField(max_length=50,null=True)
#    city =  models.CharField(max_length=75,null=True)
    gender = models.CharField(max_length=6)
    amount = models.DecimalField(max_digits=5,decimal_places=2)
    foss = models.ManyToManyField(FossCategory)
    language = models.ManyToManyField(Language)
    key = models.CharField(max_length=255)
#    st_user = models.ForeignKey(User,blank=True,null=True,on_delete=models.PROTECT)
#    pay_for = models.CharField(max_length=1,choices=PAY_FOR_CHOICES)
#    contact = models.CharField(max_length=100)
#    corporate = models.ForeignKey(Corporate,blank=True,null=True,on_delete=models.PROTECT)
#    payment =  models.ForeignKey(PaymentDetails,on_delete=models.PROTECT)
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now_add = True)
 

class PaymentTransactionDetails(models.Model):
    paymentdetail = models.ForeignKey(PaymentDetails, on_delete=models.PROTECT )
    requestType = models.CharField(max_length=2)
    userId = models.ForeignKey(User, blank=True,on_delete=models.PROTECT,related_name="payingtransaction_user" )
    amount = models.CharField(max_length=20)
    reqId = models.CharField(max_length=50)
    transId = models.CharField(max_length=100)
    refNo = models.CharField(max_length=50)
    provId = models.CharField(max_length=50)
    status = models.CharField(max_length=2)
    msg = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now_add = True)