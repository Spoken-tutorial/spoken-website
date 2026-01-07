# Standard Library
from builtins import str
from builtins import range
import datetime as dt
from donate.forms import *
from donate.models import CdFossLanguages
from django.core.mail import send_mail
# Third Party Stuff
from django.conf import settings
from .models import FossMdlCourses

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


def send_bulk_student_reset_mail(school, batches, total_students, new_password, user):
    batch_names = ", ".join([f"{x.id} - {x.batch_name}" for x in batches])

    subject = "Password Reset Notification"
    message = f"""
        Dear {user.first_name},

        Please find below the details of the recent student password update:
        Academic Center: {school.institution_name}
        Batches: {batch_names}
        Total student count: {total_students}
        New password: {new_password}
        Changed by: {user.email}

        For security reasons, please inform students to change their password immediately after login.

        Regards,
        Admin Team
        """

    # Fix: Ensure from_email is properly formatted
    from_email = settings.ADMINISTRATOR_EMAIL
    
    # If ADMINISTRATOR_EMAIL is a tuple/list, get the first email
    if isinstance(from_email, (list, tuple)):
        from_email = from_email[0] if from_email else settings.DEFAULT_FROM_EMAIL
    
    # Ensure it's a string and not empty
    if not from_email or not isinstance(from_email, str):
        from_email = settings.DEFAULT_FROM_EMAIL or 'webmaster@localhost'
    
    # Ensure it's properly formatted
    if '@' in from_email and ' ' not in from_email:
        # If it's just an email without a name, format it properly
        from_email = f"Admin Team <{from_email}>"
    
    # Handle recipient list similarly
    recipient_list = []
    
    # Add user email
    if user.email:
        recipient_list.append(user.email)
    
    # Add developer email
    dev_email = settings.DEVELOPER_EMAIL
    if isinstance(dev_email, (list, tuple)):
        if dev_email:  # Check if not empty
            recipient_list.extend([email for email in dev_email if email])
    elif dev_email and isinstance(dev_email, str):
        recipient_list.append(dev_email)
    
    print("=== SEND BULK RESET MAIL DEBUG ===")
    print("From Email Value:", from_email)
    print("From Email Type :", type(from_email))
    print("Recipient List :", recipient_list)
    print("Recipient Types:", [type(x) for x in recipient_list])
    print("Subject        :", subject)
    print("=================================")
    
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        print(f"Error sending email: {e}")
        # Fallback to default from_email
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)


def get_fossmdlcourse(foss_id, fossmdlmap_id=None):
    if fossmdlmap_id is not None:
        return FossMdlCourses.objects.get(id = fossmdlmap_id)
    try:
        fossmdlcourse = FossMdlCourses.objects.get(foss_id = foss_id)
    except FossMdlCourses.MultipleObjectsReturned:
        advanced=3 #default
        english=22 #default
        try:
            fossmdlcourse = FossMdlCourses.objects.get(foss_id=foss_id, language_id=english, level_id=advanced)
        except FossMdlCourses.DoesNotExist:
            fossmdlcourse = FossMdlCourses.objects.get(foss_id=foss_id, language__isnull=True, level__isnull=True)
    return fossmdlcourse
