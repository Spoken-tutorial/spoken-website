from events.models import AcademicKey, StudentBatch
from datetime import datetime,date

EVENT_TYPE_CHOICES =(
	('', '-----'), ('FDP', 'Paid FDP'), ('Workshop', 'Blended Mode Workshop'),('sdp', 'Student Training Programme')
	)

EVENT_AMOUNT = {
     'FDP': '500', 'Workshop': '1000'
    }

REGISTRATION_TYPE_CHOICES =(
    ('', '-----'),  ('1', 'Subscribed College'),('2', 'Manual Registration')
    )

def is_user_paid(user_obj):
    try:
        idcase = AcademicKey.objects.get(academic_id=user_obj.organiser.academic_id)
        user_paid = [True, user_obj.organiser.academic] if (idcase.expiry_date >= date.today()) else [False]
        return user_paid
    except:
        user_paid = [False]
    try:
        idcase = AcademicKey.objects.get(academic_id=user_obj.invigilator.academic_id)
        user_paid = [True, user_obj.invigilator.academic] if (idcase.expiry_date >= date.today()) else [False]
        return user_paid
    except:
        user_paid = [False]
    return user_paid

def user_college(request):
    college = ''
    try:
        college = request.user.organiser.academic
    except Exception as e1:
        try:
             college = request.user.invigilator.academic
        except Exception as e2:
             try:
                   studentbatch_id = request.user.student.studentmaster_set.values('batch_id')
                   batch = StudentBatch.objects.get(id=studentbatch_id)
                   college = batch.academic
             except:
                   #user is not associated with any college
                   pass
    return college

def handle_uploaded_file(request):
    return "successfull"

