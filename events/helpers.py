# Standard Library
from builtins import str
from builtins import range
import datetime as dt
from donate.forms import TransactionForm
from donate.models import CdFossLanguages

# Third Party Stuff
from django.conf import settings


def get_academic_years(default=settings.ACADEMIC_DURATION):
    current_year = dt.datetime.now().year
    year_choice = [('', '-----')]
    for i in range(current_year - default, current_year + 1):
        year_choice.append((i, i))
    return year_choice


def get_prev_semester_duration(semester_type, year):
    if semester_type.lower() == 'even':
        start = dt.datetime.strptime(str(year) + '-01-01', '%Y-%m-%d').date()
        end = dt.datetime.strptime(str(year) + '-06-30', '%Y-%m-%d').date()
        return start, end
    if semester_type.lower() == 'odd':
        start = dt.datetime.strptime(str(year) + '-07-01', '%Y-%m-%d').date()
        end = dt.datetime.strptime(str(year) + '-12-31', '%Y-%m-%d').date()
        return start, end
    raise Exception("Invalid semester type, it must be either odd or even")

def get_updated_form(transaction):
    form = TransactionForm()
    
    form.fields['name'].initial = transaction.paymentdetail.name
    form.fields['email'].initial =  transaction.paymentdetail.email
    form.fields['country'].initial =  transaction.paymentdetail.country
    form.fields['amount'].initial  = transaction.amount
    form.fields['expiry'].initial =  transaction.paymentdetail.expiry
    form.fields['reqId'].initial = transaction.reqId
    form.fields['transId'].initial =  transaction.transId
    form.fields['refNo'].initial =  transaction.refNo
    form.fields['provId'].initial =  transaction.provId
    form.fields['msg'].initial =  transaction.msg
    form.fields['status'].initial = transaction.status
        
    
    if transaction.status == 'S':
        form.fields[ 'selected_foss'].initial = transaction.paymentdetail.get_selected_foss()
        
    return form