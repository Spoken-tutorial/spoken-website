from django import template

register = template.Library()
from events.models import StudentBatch, StudentMaster

@register.filter
def can_add_student(student_batch, user):
  return student_batch.can_add_student(user.organiser.id)

@register.filter
def get_student_master(batch_id, student_id):
  return StudentMaster.objects.get(batch_id=batch_id, student_id=student_id)
