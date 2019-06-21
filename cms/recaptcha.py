# Standard Library
import urllib.request, urllib.parse, urllib.error

# Third Party Stuff
from django.conf import settings
from django.contrib import messages
import requests, json
''' reCAPTCHA validation '''
def recaptcha_valdation(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = settings.GOOGLE_RECAPTCHA_SITEVERIFY
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }

    content = requests.post(
        url,
        data={
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
        }
    ).content
    # Will throw ValueError if we can't parse Google's response
    content = json.loads( content )

    if not 'success' in content or not content['success']:
        messages.error(request, 'Invalid reCAPTCHA. Please try again.')
    return recaptcha_result['success']

def get_recaptcha_context():
    return { 'SITE_KEY' : settings.GOOGLE_RECAPTCHA_SITE_KEY }
