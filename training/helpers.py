from events.models import AcademicKey, StudentBatch

EVENT_TYPE_CHOICES =(
	('', '-----'), ('FDP', 'FDP'), ('SDP', 'SDP'), ('Workshop', 'Workshop'),
	)


def is_user_paid(request):
    try:
        idcase = AcademicKey.objects.get(academic_id=request.user.organiser.academic_id)
        user_paid = [True, request.user.organiser.academic] if (idcase.expiry_date >= date.today()) else [False]
    except:
        user_paid = [False]
    try:
        idcase = AcademicKey.objects.get(academic_id=request.user.invigilator.academic_id)
        user_paid = [True,request.user.invigilator.academic] if (idcase.expiry_date >= date.today()) else [False]
    except:
        user_paid = [False]
    return user_paid


def user_college(request):
    college = ''
    try:
        college = request.user.organiser.academic_id
    except Exception as e1:
        print("e1",e1)
        try:
             college = request.user.invigilator.academic_id
        except Exception as e2:
             print("e2",e2)
             try:
                   studentbatch_id = request.student.studentmaster_set.values('batch_id')
                   batch = StudentBatch.objects.get(id=studentbatch_id)
                   college = batch.academic
             except Exception as e3:
                   print("e3",e3)
    return college

