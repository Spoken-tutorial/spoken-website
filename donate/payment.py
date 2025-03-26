from django.core.urlresolvers import reverse
from django.conf import settings

from events.models import AcademicCenter
from .subscription import generate_hashed_order_id
from .models import PayeeHdfcTransaction

from training.models import TrainingEvents
from donate.models import Payee
import requests

def save_ilw_hdfc_session_data(session_response):
    transaction_data = {}
    transaction_data['transaction_id'] = session_response.get("id")
    transaction_data['order_id'] = session_response.get("order_id")
    sdk_payload = session_response.get("sdk_payload")
    transaction_data['requestId'] = sdk_payload.get("requestId")
    transaction_data['amount'] = sdk_payload.get("payload").get("amount")
    transaction = PayeeHdfcTransaction.objects.create(**transaction_data)
    return transaction

def save_ilw_hdfc_success_data(order_id, data):
    transaction = PayeeHdfcTransaction.objects.get(order_id=order_id)
    transaction.order_status = data.get('status')
    transaction.amount = data.get('amount')
    transaction.udf1 = data.get('udf1')
    transaction.udf2 = data.get('udf2')
    transaction.udf3 = data.get('udf3')
    transaction.udf4 = data.get('udf4')
    transaction.udf5 = data.get('udf5')
    transaction.save()

    #populate participant payee status
    try:
        payee = Payee.objects.get(transaction__order_id=order_id)
        payee.status = 1 if data.get('status') =='CHARGED' else 2
        payee.save()
    except:
        pass

def save_ilw_hdfc_error_data(order_id, data):
    transaction = PayeeHdfcTransaction.objects.get(order_id=order_id)
    transaction.error_code = data.get('error_code', '-')
    transaction.error_message = data.get('error_message', '-')
    transaction.save()

def get_ilw_session_payload(request, payee_obj_new, participant ):
    return_url = request.build_absolute_uri(reverse('ilw_payment_callback'))
    email = payee_obj_new.email
    phone = request.POST.get('phone')
    payload = {
        "order_id": generate_hashed_order_id(email),
        "amount":str(payee_obj_new.amount),
        "customer_id": email,
        "customer_email": email,
        "customer_phone": phone,
        "payment_page_client_id": settings.CLIENT_ID,
        "action": "paymentPage",
        "return_url": return_url,
        "description": "",
        "udf3": payee_obj_new.name,
        "udf4": payee_obj_new.state,
    }
    ac = AcademicCenter.objects.get(id=participant.college_id)
    payload['udf1'] = ac.institution_name
    payload['udf2'] = ac.academic_code
    purpose = payee_obj_new.purpose
    if  purpose == 'cdcontent':
        payload['udf5'] = 'cdcontent'
    else:
        payload['udf5'] = TrainingEvents.objects.get(id=purpose).event_name
    return payload
    
def make_hdfc_session_request(payee_obj_new, headers, payload):
    try:
        response = requests.post(settings.HDFC_API_URL, json=payload, headers=headers)
        response_data = response.json()
    except requests.exceptions.RequestException as e:
        # messages.add_message(request, messages.ERROR, "An error occurred. Please try later")
        # return render(request, template, context=context)
        return None
    if response.status_code == 200:
        payment_links = response_data.get("payment_links", {})
        payment_link = payment_links.get("web")
        if not payment_link:
            # messages.error(request, "Payment link is missing. Please contact support.")
            # return render(request, template, context=context)
            return None
        transaction = save_ilw_hdfc_session_data(response_data)
        payee_obj_new.transaction = transaction
        payee_obj_new.save()
        return payment_link
    else:
        transaction = save_ilw_hdfc_session_data(response_data, payee_obj_new.amount)
        payee_obj_new.transaction = transaction
        payee_obj_new.save()
        return None
    return None