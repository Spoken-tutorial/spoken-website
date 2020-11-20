# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime
from django.db.models import Q
from donate.models import Payee, PaymentTransaction
from django.conf import settings
from django.utils import timezone
import requests
from spoken.config import RECONCILIATION_URL, CHANNEL_ID, CHANNEL_KEY
from events import display

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        print('>> updating reconciliation transactions...')
        pt = PaymentTransaction.objects.values_list('paymentdetail_id').all().distinct()
        reqids = Payee.objects.values_list('reqId').exclude(pk__in = pt).exclude(reqId='')
        if reqids.count() > 0 and reqids.count() <= 100:
            reqids = ",".join(r[0] for r in reqids )
            data = {
                "channelId" : CHANNEL_ID,
                "reqIds" : reqids,
                "token"  : display.value(reqids+CHANNEL_KEY)
            }
            try:
                r=requests.post(RECONCILIATION_URL, data = data)
                if r.status_code == 200:
                    json_data = r.json()
                    count=0
                    for row in json_data:
                        
                        if row["responseType"].strip() == 'NULL':
                            continue
                        try:
                            payeeid = int(row["purpose"].split('NEW')[-1])
                        except ValueError:
                            continue
                        try:
                            payee = Payee.objects.get(id=payeeid)
                        except Payee.DoesNotExist:
                            continue
                        if payee:
                            try:
                                PaymentTransaction.objects.get(paymentdetail=payee, requestType=row["responseType"], amount=row["amount"].strip())
                            except PaymentTransaction.DoesNotExist:
                                time = row["transactionDate"].strip()
                                date=timezone.make_aware(datetime.strptime(time[:-2], '%Y-%m-%d %H:%M:%S'))
                                paymenttrans = PaymentTransaction()
                                paymenttrans.paymentdetail = payee
                                paymenttrans.requestType = row["responseType"].strip()
                                paymenttrans.amount = row["amount"].strip()
                                paymenttrans.reqId = row["requestId"].strip()
                                paymenttrans.transId = row["transactionId"].strip() if "transactionId" in row else ""
                                paymenttrans.refNo = row["referenceId"].strip()
                                paymenttrans.provId = row["providerId"].strip()
                                paymenttrans.status = row["status"].strip()
                                paymenttrans.msg = row["message"].strip() if "message" in row else ""
                                paymenttrans.save()
                                paymenttrans.created = date
                                paymenttrans.save()
                                if paymenttrans.status == "S":
                                    payee.status = 1
                                elif paymenttrans.status == "F":
                                    payee.status =2
                                payee.save()
                                count+=1
                    print(('Script Completed. Transaction added',count))
            except:
                print("Request Failed.")
        else:
            print("Request ids should not be less than 0 or greater than 100. Request Id count = ", reqids.count())
