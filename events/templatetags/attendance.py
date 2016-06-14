# Third Party Stuff
from django import template

# Spoken Tutorial Stuff
from events.models import TrainingAttend

register = template.Library()


@register.filter
def is_attendance_marked(training, student):
    if TrainingAttend.objects.filter(training=training, student=student).exists():
        return True
    return False


@register.filter
def get_attendance(training, student):
    if TrainingAttend.objects.filter(training=training, student=student).exists():
        return TrainingAttend.objects.filter(training=training, student=student).first()
    if training.batch_id:
        return True
    return False


@register.filter
def get_langid(training, student):
    try:
        training_attend = TrainingAttend.objects.get(training=training, student=student)
        return training_attend.language_id
    except:
        pass
    return False


@register.filter
def is_attendance_allowed(training, student):
    # checking existing attendance for course
    if TrainingAttend.objects.filter(student=student,
                                     training__course=training.course).exclude(training=training).exists():
        return False
    return True
