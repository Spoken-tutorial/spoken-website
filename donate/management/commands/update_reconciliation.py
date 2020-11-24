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
        total = reqids.count()
        print("Total = ", total)
        flr = total // 100
        rem = total % 100
        if total > 100:
            for f in range(1, flr+1):
                self.run_reconciliation(reqids[(100*(f-1)):(100*f)])
            if rem > 0:
                self.run_reconciliation(reqids[(100*flr):((100*flr)+rem)])
        else:
            self.run_reconciliation(reqids)

    
    def run_reconciliation(self, reqids):
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
                    if "responseType" not in row:
                        continue
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
        except requests.ConnectionError as e:
            print("Request Failed.", e)