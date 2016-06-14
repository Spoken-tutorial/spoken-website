# Standard Library
import time

# Third Party Stuff
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

# Spoken Tutorial Stuff
from events.models import *


def nemail(request):
    plaintext = get_template('email-template/email-template.txt')
    htmly = get_template('email-template/email-template.html')
    d = Context({'username': 'username'})
    text_content = plaintext.render(d)
    html_content = htmly.render(d)
    organisers = Organiser.objects.filter(status=1).exclude(
        user_id__in=OrganiserNotification.objects.all().values_list('user_id'))
    sent = 0
    notsent = 0
    count = 0
    tot_count = organisers.count()

    subject = "Spoken Tutorial Software Training Program"

    for organiser in organisers:
        to = [organiser.user.email]
        email = EmailMultiAlternatives(subject, text_content, 'no-reply@spoken-tutorial.org',
                                       to=to, headers={"Content-type": "text/html"})
        email.attach_alternative(html_content, "text/html")
        count = count + 1
        try:
            email.send(fail_silently=False)
            sent += 1
            OrganiserNotification.objects.create(user=organiser.user)
            if sent % 10 == 0:
                time.sleep(5)
            print to, " => sent (", str(count), "/", str(tot_count), ")"
        except Exception, e:
            print e
            print to, " => not sent (", count, "/", tot_count, ")"

    print "--------------------------------"
    print "Total sent mails:", sent
    print "Total not sent mails:", notsent
    print "--------------------------------"
    return HttpResponse("Done!")
