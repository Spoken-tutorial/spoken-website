# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime
from django.db.models import Q
from donate.models import *
import os
import csv
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        print('>> updating transaction records')
        count = 0
        csv_file_path = settings.MEDIA_ROOT +"st_transaction_details.csv"
        with open(csv_file_path) as csv_file:
            rows_data = csv.reader(csv_file, delimiter=',')
            for row in rows_data:
                if row[2].strip() == 'NULL':
                    continue
                try:
                    payeeid = int(row[10].split('NEW')[-1])
                except ValueError:
                    continue
                try:
                    payee = Payee.objects.get(id=payeeid)
                except Payee.DoesNotExist:
                    continue
                if payee:
                    try:
                        PaymentTransaction.objects.get(paymentdetail=payee, requestType=row[2].strip(), amount=row[3].strip())
                    except PaymentTransaction.DoesNotExist:
                        if row[8].strip() != "NULL":
                            time = str(row[7].strip().split(" ")[0]+ " "+row[8].strip())
                        else:
                            time = row[7].strip()
                        date=timezone.make_aware(datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
                        paymenttrans = PaymentTransaction()
                        paymenttrans.paymentdetail = payee
                        paymenttrans.requestType = row[2].strip()
                        paymenttrans.amount = row[3].strip()
                        paymenttrans.reqId = row[1].strip()
                        paymenttrans.transId = row[4].strip()
                        paymenttrans.refNo = row[5].strip()
                        paymenttrans.provId = "PAYU"
                        paymenttrans.status = row[6].strip()
                        paymenttrans.msg = row[9].strip()
                        paymenttrans.save()
                        paymenttrans.created = date
                        paymenttrans.updated = date
                        paymenttrans.save()
                        if paymenttrans.status == "S":
                            payee.status = 1
                        elif paymenttrans.status == "F":
                            payee.status =2
                        payee.save()
                        count+=1
        print(('>> Script Completed. data added',count))
