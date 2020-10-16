from events.models import AcademicKey, StudentBatch
from datetime import datetime,date

EVENT_TYPE_CHOICES =(
	('', '-----'), ('FDP', 'Paid FDP'), ('Workshop', 'Blended Mode Workshop'),('sdp', 'Student Training Programme'),('TPDP', 'Teachers Professional Development Program'
), ('SSDP', 'School Students  Development Program')
	)

EVENT_AMOUNT = {
     'FDP': '500', 'Workshop': '1000'
    }

REGISTRATION_TYPE_CHOICES =(
    ('', '-----'),  (1, 'Subscribed College'),(2, 'Manual Registration')
    )

def is_user_paid(user_obj, academic_id):
    try:
        idcase = AcademicKey.objects.get(academic_id=academic_id)
        user_paid = [True, user_obj.organiser.academic] if (idcase.expiry_date >= date.today()) else [False]
        return user_paid
    except:
        user_paid = [False]
    try:
        idcase = AcademicKey.objects.get(academic_id=academic_id)
        user_paid = [True, user_obj.invigilator.academic] if (idcase.expiry_date >= date.today()) else [False]
        return user_paid
    except:
        user_paid = [False]
    return user_paid

def user_college(user_obj):
    college = ''
    try:
        college = user_obj.organiser.academic
    except Exception as e1:
        try:
             college = user_obj.invigilator.academic
        except Exception as e2:
             #try:
             #      studentbatch_id = user_obj.student.studentmaster_set.values('batch_id')
             #      batch = StudentBatch.objects.get(id=studentbatch_id)
             #      college = batch.academic
             #except:
             #      #user is not associated with any college
             pass
    return college

def handle_uploaded_file(request):
    return "successfull"


def is_college_paid(college_id):
    try:
        idcase = AcademicKey.objects.get(academic_id=college_id)
        college_paid = True if (idcase.expiry_date >= date.today()) else False
        return college_paid
    except:
        college_paid = False
    
    return college_paid
