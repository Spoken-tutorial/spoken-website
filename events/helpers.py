# Standard Library
from builtins import str
from builtins import range
import datetime as dt
from donate.forms import TransactionForm

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
    form.initial = {
        'name' : transaction.paymentdetail.name,
        'email' :  transaction.paymentdetail.email,
        'country' :  transaction.paymentdetail.country,
        'key' : transaction.paymentdetail.key,
        'amount' : transaction.amount,
        'expiry' :  transaction.paymentdetail.expiry,
        'reqId' : transaction.reqId,
        'transId' :  transaction.transId,
        'refNo' :  transaction.refNo,
        'provId' :  transaction.provId,
        'msg' :  transaction.msg,
        'status': transaction.status
        }
        if transaction.status == "S":
            form.initial = {
            'selected_foss': get_selected_foss(transaction.paymentdetail.id)
            }
    return form

def get_selected_foss(paymentdetail_id):
    selected_foss = {}
    c = 0
    cd_foss_langs = CdFossLanguages.objects.filter(payment=paymentdetail_id).values('foss_id','lang_id')
    for key,value in cd_foss_langs:
        if t[c][key] in selected_foss.keys():
           t[c][key].append([t[c][value]])
        else:
           t[c][key] = [t[c][value]]
        c= c+1
    return selected_foss
