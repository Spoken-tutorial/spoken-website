from django.dispatch import receiver
from django.db.models.signals import post_save
from events.models import AcademicKey
from donate.models import Payee
from cms.management.commands.populate_subscription_data import update_subscription,get_users_from_acad
from cms.management.commands.populate_ilw_data import get_fosses,get_ilw_users, set_user_type_ilw

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
    d = get_fosses(obj)
    users = get_ilw_users(obj)
    set_user_type_ilw(users,d)