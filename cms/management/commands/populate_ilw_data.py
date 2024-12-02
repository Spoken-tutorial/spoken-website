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
    print(f"\033[95m user_lst : {len(user_lst)} \033[0m")
    for user in user_lst:
        try:
            ut=UserType.objects.get(user_id=user)
            if ut.ilw != foss:
                ut.ilw = foss
                ut.save()
        except UserType.DoesNotExist:
            ut=UserType.objects.create(user_id=user, ilw=foss)
        except Exception as e:
            print(f"Exception in set_user_type_ilw {user} : {e}")

def get_fosses(payee):
    foss_lang = CdFossLanguages.objects.filter(payment=payee)
    d = defaultdict(list)
    for item in foss_lang:
        d[str(item.foss.id)].append(item.lang.id)
    return d

def get_ilw_users(payee): 
    if payee.status == 1:
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
                unique_users = list(set(participants+event_users))
                return unique_users
            except TrainingEvents.DoesNotExist:
                print(f"\033[93m TrainingEvent not found: {purpose} \n \033[0m")
            except Exception as e:
                print(f"\033[93m get_ilw_users exception: {purpose} \n{e} \033[0m")
    return []
    

class Command(BaseCommand):
    help = 'Populate cms_usertype table from donate_payee. It populates data for individual cd content download users,organizers, invigilators and participants for specific paid fosses.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year', type=int, help='Filter Payee objects by year of date_updated'
        )
    
    def handle(self, *args, **options):
        # Your code goes here
        self.stdout.write('Starting populate_ilw_data command...')
        year = options.get('year')
        payee_list = Payee.objects.filter(status=1)
        if year:
            payee_list = payee_list.filter(updated__year=year)
        for payee in payee_list:
            d = get_fosses(payee)
            users = get_ilw_users(payee)
            if users:
                set_user_type_ilw(users,d)
        self.stdout.write('Ending populate_ilw_data command...')
