# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime,timedelta
from django.db.models import Q
from donate.models import *
import os
import csv
from django.conf import settings


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
                        paymenttrans.created = row[8].strip()
                        paymenttrans.save()
                        print(row)
                        count+=1
        print(('>> Script Completed. data added',count))
