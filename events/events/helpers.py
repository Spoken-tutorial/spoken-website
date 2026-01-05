# Standard Library
from builtins import str
from builtins import range
import datetime as dt
from donate.forms import *
from donate.models import CdFossLanguages
from django.core.mail import send_mail
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

def get_updated_form(transaction, form_type):
    if form_type == 'CD-Events':
        form = TransactionForm()
        form.fields['expiry'].initial =  transaction.paymentdetail.expiry
        if transaction.status == 'S':
            form.fields[ 'selected_foss'].initial = transaction.paymentdetail.get_selected_foss()
    if form_type == 'Donate':
        form = DonationTransactionForm()
    if form_type == 'Goodie':
        form = GoodieTransactionForm()
    form.fields['name'].initial = transaction.paymentdetail.name
    form.fields['email'].initial =  transaction.paymentdetail.email
    form.fields['country'].initial =  transaction.paymentdetail.country
    form.fields['amount'].initial  = transaction.amount
    form.fields['reqId'].initial = transaction.reqId
    form.fields['transId'].initial =  transaction.transId
    form.fields['refNo'].initial =  transaction.refNo
    form.fields['provId'].initial =  transaction.provId
    form.fields['msg'].initial =  transaction.msg
    form.fields['status'].initial = transaction.status
        
    return form

def send_bulk_student_reset_mail(ac, batches, count, new_password, user):
    batch_names = ", ".join([f"{x.id} - {x.batch_name}" for x in batches])
    subject = "Password Reset Notification"
    message = f"""
        Dear {user.first_name},

        Please find below the details of the recent student password update: 
        Academic Center: {ac.institution_name}
        Batches: {batch_names}
        Total student count: {count}
        New password: {new_password}
        Changed by: {user.email}
    
        For security reasons, please inform students to change your password immediately after login.

        Regards,
        Admin Team
    """

    from_email  = settings.ADMINISTRATOR_EMAIL
    recipient_list = [user.email, settings.DEVELOPER_EMAIL]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)