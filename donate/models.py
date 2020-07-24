from django.db import models
from django.contrib.auth.models import User
from .helpers import GENDER_CHOICES, PAY_FOR_CHOICES
from creation.models import FossCategory, Language, Level
import uuid
from datetime import datetime
from pytz import timezone
import json

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
    amount = models.CharField(max_length=20)
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