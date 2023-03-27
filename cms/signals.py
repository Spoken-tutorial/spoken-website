from django.dispatch import receiver
from django.db.models.signals import post_save
from cms.models import UserType
from events.models import AcademicPaymentStatus, AcademicKey, Organiser, Invigilator, StudentBatch, StudentMaster, Student
from donate.models import Payee, CdFossLanguages
from training.models import TrainingEvents
from django.contrib.auth.models import User
from collections import defaultdict
from cms.management.commands.populate_subscription_data import update_subscription,get_users_from_acad
from cms.management.commands.populate_ilw_data import get_users_from_event,get_fosses,get_ilw_users, set_user_type_ilw

@receiver(post_save, sender=AcademicKey)
def update_user_type_sub(sender, **kwargs):
    # users : organizers, invigilators, students
    obj = kwargs['instance']
    academic_id = obj.academic_id
    expiry_date = obj.expiry_date
    users = get_users_from_acad(academic_id)
    update_subscription(users,expiry_date)
    
@receiver(post_save, sender=Payee)
def update_user_type_ilw(sender, **kwargs):
    obj = kwargs['instance']
    purpose = obj.purpose
    d = get_fosses(obj)
    users = get_ilw_users(obj)
    set_user_type_ilw(users,d)