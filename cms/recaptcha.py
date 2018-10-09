# Standard Library
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse

# Third Party Stuff
from django.conf import settings
from django.contrib import messages

''' reCAPTCHA validation '''
def recaptcha_valdation(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = settings.GOOGLE_RECAPTCHA_SITEVERIFY
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values)
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    recaptcha_result = json.load(response)
    if not recaptcha_result['success']:
        messages.error(request, 'Invalid reCAPTCHA. Please try again.')
    return recaptcha_result['success']

def get_recaptcha_context():
    return { 'SITE_KEY' : settings.GOOGLE_RECAPTCHA_SITE_KEY }
