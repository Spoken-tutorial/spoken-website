from django.db import models
from django.contrib.auth.models import User
from .helpers import *
from creation.models import FossCategory, Language, Level
import uuid
from datetime import datetime
from pytz import timezone
import json
from events.models import City, State, AcademicCenter
from django.core.validators import RegexValidator, MinLengthValidator

class Payee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    country = models.CharField(max_length=50,null=True)
    state = models.CharField(max_length=50,null=True)
    city =  models.CharField(max_length=75,null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    key = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expiry = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User,on_delete=models.PROTECT,related_name="payment_user" )
    purpose = models.CharField(max_length=255, null=True)
    reqId = models.CharField(max_length=100, default='')
    source = models.CharField(max_length=25, null=True, default=None)
    def get_selected_foss(self):
        selected_foss = {}
        c = 0
        cd_foss_langs = CdFossLanguages.objects.filter(payment=self.id).order_by("lang_id").values('foss_id','lang_id','level_id')
        for foss,langs,level in cd_foss_langs:
            foss_json = json.dumps(cd_foss_langs[c][foss])
            langs_json = json.dumps(cd_foss_langs[c][langs])
            if not cd_foss_langs[c][level]:
                 level_json = 0
            else:
                 level_json = cd_foss_langs[c][level]
            if foss_json in selected_foss.keys():
                 selected_foss[foss_json][0].append(langs_json)
            else:
                 selected_foss[foss_json] = [[langs_json],level_json]
            c= c+1
        return json.dumps(selected_foss)

    @property
    def is_past_due(self):
        now_utc = datetime.now(timezone('UTC'))
        return now_utc <= self.expiry

      
class CdFossLanguages(models.Model):
    payment = models.ForeignKey(Payee, on_delete=models.PROTECT)
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT,related_name="payment_foss")
    lang = models.ForeignKey(Language)
    level = models.ForeignKey(Level,null=True,blank=True)

class PaymentTransaction(models.Model):
    paymentdetail = models.ForeignKey(Payee, on_delete=models.PROTECT, related_name="payment_transaction" )
    requestType = models.CharField(max_length=2)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    reqId = models.CharField(max_length=50)
    transId = models.CharField(max_length=100)
    refNo = models.CharField(max_length=50)
    provId = models.CharField(max_length=50)
    status = models.CharField(max_length=2)
    msg = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('paymentdetail','requestType','amount')

# abstract base class
class TransactionCommonInfo(models.Model):
    requestType = models.CharField(max_length=2)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    reqId = models.CharField(max_length=50)
    transId = models.CharField(max_length=100)
    refNo = models.CharField(max_length=50)
    provId = models.CharField(max_length=50)
    status = models.CharField(max_length=2)
    msg = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# abstract base class 
class PayeeCommonInfo(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6)
    contact = models.CharField(max_length=255)
    address = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    country = models.CharField(max_length=6, choices=COUNTRY, default='India')
    reqId = models.CharField(max_length=100, default='')
    class Meta:
        abstract = True

class DonationPayee(PayeeCommonInfo):
    pass
   
    
class DonationTransaction(TransactionCommonInfo):
    paymentdetail = models.ForeignKey(DonationPayee, on_delete=models.PROTECT, related_name="donation_payment_transaction" )


class Goodies(PayeeCommonInfo):
    item = models.CharField(max_length=6, choices=ITEM_CHOICES, default='tshirt')
    size = models.CharField(max_length=6, choices=SIZE_CHOICES, default='m')

class GoodiesTransaction(TransactionCommonInfo):
    paymentdetail = models.ForeignKey(Goodies, on_delete=models.PROTECT, related_name="goodie_payment_transaction" )
    

class SchoolDonation(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    contact = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    address = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField()
    reqId = models.CharField(max_length=100, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    mail_status = models.BooleanField(default=False)
    mail_response = models.CharField(max_length=250)


class SchoolDonationTransactions(TransactionCommonInfo):
    paymentdetail = models.ForeignKey(SchoolDonation, on_delete=models.PROTECT)


class HDFCTransactionDetails(models.Model):
    transaction_id = models.CharField(max_length=255) # "id" from the order status response
    requestId = models.CharField(max_length=255)
    order_id = models.CharField(max_length=21)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    session_error_code = models.CharField(max_length=255)
    session_error_msg = models.CharField(max_length=255)
    order_status = models.CharField(max_length=255) #order status like charged, failed etc
    order_error_code = models.CharField(max_length=255)
    order_error_msg = models.CharField(max_length=255)
    customer_id = models.CharField(max_length=50)
    udf1 = models.TextField() # academic center name
    udf2 = models.TextField() # academic center code
    udf3 = models.CharField(max_length=150) # payee name
    udf4 = models.CharField(max_length=50) # academic center state name

class AcademicSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    transaction = models.ForeignKey(HDFCTransactionDetails, on_delete=models.PROTECT, blank=True, null=True)
    expiry_date = models.DateField()
    subscription_amount = models.DecimalField(max_digits=10,decimal_places=2)
    num_academic_center = models.IntegerField() #Total number of academic centers to be paid for
    subscription_days = models.IntegerField()
    subscription_start_date = models.DateField()
    phone = models.CharField(max_length=20)
    response_status = models.CharField(max_length=3) # stores the session api response status code
    error_code = models.CharField(max_length=3, blank=True, null=True) # stores the session api response error_code code
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

class AcademicSubscriptionDetail(models.Model):
    academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT)
    subscription_end_date = models.DateField() # This varies from expiry date in case if institute gets extention or grace period from ST team
    subscription = models.ForeignKey(AcademicSubscription, on_delete=models.CASCADE, related_name='academic_details')