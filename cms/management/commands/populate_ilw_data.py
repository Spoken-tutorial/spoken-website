from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q
from donate.models import Payee, CdFossLanguages
from cms.models import UserType
from collections import defaultdict
from training.models import TrainingEvents
from training.models import Participant
from django.conf import settings

def set_user_type_ilw(user_lst,foss={}):
    for user in user_lst:
        try:
            ut=UserType.objects.get(user_id=user)
        except UserType.DoesNotExist:
            ut=UserType.objects.create(user_id=user)
        if ut.ilw != foss:
            ut.ilw = foss
            ut.save()

def get_fosses(payee):
    foss_lang = CdFossLanguages.objects.filter(payment=payee)
    d = defaultdict(list)
    for item in foss_lang:
        d[str(item.foss.id)].append(item.lang.id)
    return d

def get_ilw_users(payee): 
    purpose = payee.purpose
    if purpose == getattr(settings, 'EVENT_CD_CONTENT', 'cdcontent'): # users : individual payee
        users = [payee.user_id]
        return users
    else:
        try:
            event = TrainingEvents.objects.get(id=purpose)    
            participants = [x for x in Participant.objects.filter(event=event).values_list('user_id',flat=True)]
            event_users = [x.id for x in User.objects.filter(Q(email=event.event_coordinator_email) | Q(id=event.entry_user_id))] #Event coordinator & Training Manager
            #return users who are participants /coordinator / Training Manager of the ILW event 
            return participants+event_users
        except Exception as e:
            print(f"event failed: {purpose:>15} \n{e}")
    

class Command(BaseCommand):
    help = 'Populate cms_usertype table from donate_payee. It populates data for individual cd content download users,organizers, invigilators and participants for specific paid fosses.'

    def handle(self, *args, **options):
        # Your code goes here
        self.stdout.write('Starting populate_ilw_data command...')
        payee_list = Payee.objects.all()
        for payee in payee_list:
            d = get_fosses(payee)
            users = get_ilw_users(payee)
            set_user_type_ilw(users,d)
        self.stdout.write('Ending populate_ilw_data command...')
