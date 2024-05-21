from django.core.management.base import BaseCommand
from django.db.models import Max
from events.models import Organiser, AcademicKey, StudentBatch, StudentMaster, Student, Invigilator
from cms.models import UserType
from django.utils import timezone

def update_subscription(users,expiry_date):
    for user in users:
        try:
            ut = UserType.objects.get(user_id=user)
            if ut.subscription != expiry_date:
                ut.subscription = expiry_date
                ut.save()
        except UserType.DoesNotExist:
            try:
                ut = UserType.objects.create(user_id=user,subscription=expiry_date)
            except Exception as e:
                print(f"failed for user: {user:>10}\n{e}")
        except Exception as e:
            print(f"\033[93mException update_subscription for user : {user} : {e}  \033[0m")
        
def get_users_from_acad(academic_id):
    organisers = [x for x in Organiser.objects.filter(academic_id=academic_id).values_list('user',flat=True)]
    invigilators = [x for x in Invigilator.objects.filter(academic_id=academic_id).values_list('user',flat=True)]
    student_batch = StudentBatch.objects.filter(academic_id=academic_id)
    student_ids = [x for x in StudentMaster.objects.filter(batch__in=student_batch).values_list('student_id',flat=True)]
    students = [x for x in Student.objects.filter(id__in=student_ids).values_list('user',flat=True)]
    # return users who are organisers, invigilators or students of the given academic center
    users_from_acad = organisers + invigilators + students
    unique_users_from_acad = list(set(users_from_acad))
    return unique_users_from_acad 
    
class Command(BaseCommand):
    help = 'Populate cms_usertype table from events_academickey. It populates data for organisers, invigilators and students for paid academic centers with check on expiry date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month', type=int, help='Filter Academic Key objects by month of expiry_date'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Starting subscription management command...')
        today = timezone.now().date()
        acad_keys = AcademicKey.objects.filter(expiry_date__gte=today).values('academic_id').annotate(latest_expiry_date=Max('expiry_date'))
        month = options.get('month')
        if month:
            acad_keys = acad_keys.filter(expiry_date__month=month)
        for key in acad_keys:
            expiry_date = key['latest_expiry_date']
            users = get_users_from_acad(key['academic_id'])
            try:
                update_subscription(users,expiry_date)
                self.stdout.write(f"academic_id passed: {key['academic_id']:>10}")
            except Exception as e:
                self.stdout.write(f"academic_id failed: {key['academic_id']:>10} \n{e}")
                
        self.stdout.write('Ending populate_subscription_data.')
