from django import template

register = template.Library()
from events.models import StudentBatch

@register.filter
def can_add_student(student_batch, user):
  return student_batch.can_add_student(user.organiser.id)
