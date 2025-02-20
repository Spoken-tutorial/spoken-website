from django.conf import settings
from django.core.urlresolvers import reverse
from events.models import Organiser, Accountexecutive, AcademicCenter, \
AcademicKey, AcademicPaymentStatus
from .models import AcademicSubscription, HDFCTransactionDetails
from django.http import JsonResponse
import hashlib
import time
from datetime import date
import base64
# import urllib.parse
import requests
import urllib
import hmac


def generate_hashed_order_id(email):
    data = f"{email}{int(time.time())}"
    hashed_id = hashlib.sha256(data.encode()).hexdigest()[:15]  # order id is restricted to max 21 characters
    return hashed_id.upper()
 
def get_request_headers(email):
    # Encode API Key for Basic Auth
    encoded_api_key = base64.b64encode(f"{settings.HDFC_API_KEY}:".encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_api_key}",
        "Content-Type": "application/json",
        "x-merchantid": settings.MERCHANT_ID,
        "x-customerid": email
    }
    return headers

def get_session_payload(request, email, data, academic):
    return_url = request.build_absolute_uri(reverse('payment_callback'))
    payload = {
            "order_id": generate_hashed_order_id(email),
            "amount": str(data.get('subscription_amount')),
            "customer_id": email,
            "customer_email": data.get('email'),
            "customer_phone": data.get("phone"),
            "payment_page_client_id": settings.CLIENT_ID,
            "action": "paymentPage",
            "return_url": return_url,
            "description": "Complete Academic Subscription Payment.....",
            "udf3": data.get('name'),
            "udf4": data.get('state')
        }
    udf1 = ""
    udf2 = ""
    for ac in academic:
        values = AcademicCenter.objects.filter(id__in=academic).values('institution_name', 'academic_code')
        ac_name = []
        ac_code = []
        for item in values:
            ac_name.append(item.get('institution_name'))
            ac_code.append(item.get('academic_code'))
    udf1 = ' ** '.join(ac_name)
    udf2 = ' ** '.join(ac_code)
    payload["udf1"] = udf1
    payload["udf2"] = udf2
    return payload

# def get_session_data(session_response):
def save_hdfc_session_data(session_response):
    transaction_data = {}
    transaction_data['transaction_id'] = session_response.get("id")
    transaction_data['order_id'] = session_response.get("order_id")
    sdk_payload = session_response.get("sdk_payload")
    transaction_data['requestId'] = sdk_payload.get("requestId")
    transaction_data['amount'] = sdk_payload.get("payload").get("amount")
    transaction = HDFCTransactionDetails.objects.create(**transaction_data)
    return transaction

def save_hdfc_session_error(response_data, subscription_amount):
    data = {
                'transaction_id': response_data.get('id', ''),
                'session_error_code': response_data.get('error_code'),
                'session_error_msg': response_data.get('error_message', '-'),
                'amount': subscription_amount
            }
    transaction = HDFCTransactionDetails.objects.create(**data)
    return transaction

def get_order_status_data(order_status_response):
    transaction_data = {}
    transaction_data['transaction_id'] = order_status_response.get("id")


def get_failed_session_data(session_response):
    transaction_data = {}
    transaction_data['transaction_id'] = session_response.get("id")
    transaction_data['session_status'] = session_response.get("status")
    transaction_data['error_code'] = session_response.get("error_code")
    transaction_data['error_message'] = session_response.get("error_message", "-")
    return transaction_data

def fulfill_order(transaction):
    "This is required as existing active institution logic is based on the process of AcademicKey."
    subscription = AcademicSubscription.objects.get(transaction=transaction)
    data = {
        "state" : subscription.academic,
        "academic": subscription.academic,
        "name_of_the_payer": f"{subscription.user.first_name} {subscription.user.last_name}",
        "email": subscription.user.email,
        "phone": subscription.phone,
        "amount": subscription.amount,
        "subscription": "365",
        "transactionid": "",
        "payment_date": date.today(),
        "payment_status": "", #
        "college_type": "",
        "pan_number": "",
        "gst_number": "",
        "customer_id": "",
        "invoice_no": "",
        "remarks": "",
        "entry_date": date.today(),
        "entry_user" : subscription.user.id
    }
    obj = AcademicPaymentStatus.objects.create(**data)
    ak = AcademicKey.objects.create(ac_pay_status=obj,academic=subscription.academic,\
                               u_key="", hex_key="",  expiry_date=subscription.expiry )

def verify_hmac_signature(params):
    """
    Verifies the HMAC signature from the provided parameters.
    Returns True if the signature is valid, otherwise False.
    """
    key = settings.RESPONSE_KEY.encode()
    # Extract and Remove `signature` & `signature_algorithm`
    data = params.copy()
    signature_algorithm = data.pop('signature_algorithm', None)
    signature = data.pop('signature', None)
    if signature:
        signature = signature[0]
    else:
        return False
    # Sort and Encode Parameters
    encoded_params = {}
    # Percentage Encode Each Key & Value
    for k in data.keys():
        encoded_key = urllib.parse.quote_plus(str(k))
        encoded_value = urllib.parse.quote_plus(str(data[k]))
        encoded_params[encoded_key] = encoded_value
    encoded_values = []
    for k in sorted(encoded_params.keys()):
        encoded_values.append(f"{k}={encoded_params[k]}")
    encoded_string = '&'.join(encoded_values)
    p_encoded_string = urllib.parse.quote_plus(encoded_string)
    # Generate HMAC Signature Using SHA-256
    dig = hmac.new(key, msg=p_encoded_string.encode(), digestmod=hashlib.sha256).digest()
    computed_sign = base64.b64encode(dig).decode() # Base64 encode the result
    return computed_sign == signature
    

def poll_payment_status(order_id, email, sub_amount):
    """
    Polls the HDFC API every 15 seconds to check the payment status.
    Stops polling when:
      - The status is "charged" or "failed"
      - The max attempts is reached
    """
    HDFC_STATUS_URL = f"{settings.ORDER_STATUS_URL}{order_id}"
    headers = get_request_headers(email)
    max_attempts = settings.HDFC_POLL_MAX_RETRIES 
    wait_time = settings.HDFC_POLL_INTERVAL # Wait before polling again
    attempt = 0
    while attempt < max_attempts:
        try:
            response = requests.get(HDFC_STATUS_URL, headers=headers)
            data = response.json()
            if response.status_code == 200 and "status" in data:
                order_status = data.get('status', '')
                amount = data.get('amount', '')
                order_id = data.get('order_id', '')
                if order_status == 'CHARGED' and amount == sub_amount:
                    transaction= HDFCTransactionDetails.objects.get(order_id=order_id)
                    # fulfill_order(transaction) # Todo 
                    save_hdfc_success_data(order_id, data)
                    return {"status": order_status}
                elif order_status in ["AUTHENTICATION_FAILED", "AUTHORIZATION_FAILED"]:
                    save_hdfc_error_data()
                    return {"status": order_status}
            attempt+=1
            time.sleep(wait_time)
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}
    return {"status": "TIMEOUT", "message": "Max attempts reached, payment is still pending."} 

def save_hdfc_success_data(order_id, data):
    transaction = HDFCTransactionDetails.objects.get(order_id=order_id)
    transaction.order_status = data.get('status')
    transaction.amount = data.get('amount')
    transaction.udf1 = data.get('udf1')
    transaction.udf2 = data.get('udf2')
    transaction.udf3 = data.get('udf3')
    transaction.udf4 = data.get('udf4')
    transaction.save()

def save_hdfc_error_data(order_id, data):
    transaction = HDFCTransactionDetails.objects.get(order_id=order_id)
    transaction.error_code = data.get('error_code', '-')
    transaction.error_message = data.get('error_message', '-')
    transaction.save()

def get_display_transaction_details(transaction):
    data = {}
    data['customer_email'] = transaction.get('customer_email', '')
    data['customer_phone'] = transaction.get('customer_phone', '')
    data['id'] = transaction.get('id', '')
    data['amount'] = transaction.get('amount', '')
    data['udf1'] = transaction.get('udf1', '')
    data['udf2'] = transaction.get('udf2', '')
    data['udf3'] = transaction.get('udf3', '')
    data['udf4'] = transaction.get('udf4', '')
    data['order_id'] = transaction.get('order_id', '')
    return data

def get_academic_centers(request):
    stateId = request.GET.get('stateId')
    if stateId:
        ac = AcademicCenter.objects.filter(state_id=stateId).order_by('institution_name').values('id', 'institution_name', 'academic_code')
        return JsonResponse(list(ac), safe=False)
    return JsonResponse([])

