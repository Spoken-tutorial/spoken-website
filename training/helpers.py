from events.models import AcademicKey

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