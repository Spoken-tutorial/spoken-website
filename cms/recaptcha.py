from django.conf import settings
from django.contrib import messages
import urllib
import urllib2
import json

''' reCAPTCHA validation '''
def recaptcha_valdation(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = settings.GOOGLE_RECAPTCHA_SITEVERIFY
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    recaptcha_result = json.load(response)
    if not recaptcha_result['success']:
        messages.error(request, 'Invalid reCAPTCHA. Please try again.')
    return recaptcha_result['success']

def get_recaptcha_context():
    return { 'SITE_KEY' : settings.GOOGLE_RECAPTCHA_SITE_KEY }
