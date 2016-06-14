# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Third Party Stuff
from django.db import models


class WStates(models.Model):
    id = models.IntegerField(primary_key=True)
    code = models.CharField(max_length=5)
    name = models.CharField(max_length=200)
    latitude = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    image_map_area = models.TextField()

    class Meta:
        db_table = 'states'


class WAcademicCenter(models.Model):
    id = models.IntegerField(primary_key=True)
    state_code = models.CharField(max_length=5)
    academic_code = models.CharField(unique=True, max_length=10)
    school_college = models.IntegerField()
    institution_name = models.CharField(max_length=200)
    street = models.TextField()
    city = models.CharField(max_length=75)
    pincode = models.CharField(max_length=10)
    resource_center = models.IntegerField()
    star_rating = models.IntegerField()
    contact_details = models.TextField()
    remarks = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'academic_center'


class WDepartments(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=200)

    class Meta:
        db_table = 'departments'


class WInvigilator(models.Model):
    id = models.IntegerField(primary_key=True)
    invigilator_id = models.IntegerField()
    academic_code = models.CharField(unique=True, max_length=10)
    invigilator_name = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'invigilator'


class WLiveWorkshopParticipants(models.Model):
    id = models.IntegerField(primary_key=True)
    pname = models.CharField(max_length=100)
    workshop_code = models.IntegerField()
    foss_category = models.IntegerField()
    email = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    institution = models.CharField(max_length=255)
    rate_workshop = models.IntegerField()
    rate_workshop_why = models.TextField()
    content = models.IntegerField()
    logical_arrangement = models.IntegerField()
    clarity = models.IntegerField()
    understandable = models.IntegerField()
    included_examples = models.IntegerField()
    instruction_sheet = models.IntegerField()
    assignments = models.IntegerField()
    pace_tutorial = models.IntegerField()
    useful_thing = models.TextField()
    weakness_duration = models.IntegerField()
    weakness_narration = models.IntegerField()
    weakness_understand = models.IntegerField()
    other_weakness = models.TextField()
    workshop_language = models.IntegerField()
    info_received = models.IntegerField()
    if_yes = models.TextField()
    comfortable_learning = models.IntegerField()
    working_computers = models.IntegerField()
    audio_quality = models.IntegerField()
    video_quality = models.IntegerField()
    orgn_wkshop = models.IntegerField()
    facil_learning = models.IntegerField()
    motiv_learning = models.IntegerField()
    time_mgmt = models.IntegerField()
    soft_klg = models.IntegerField()
    prov_expn = models.IntegerField()
    ans_cln = models.IntegerField()
    help_lern = models.IntegerField()
    exec_effly = models.IntegerField()
    ws_improved = models.TextField()
    recomm_wkshop = models.IntegerField()
    reason_why = models.TextField()
    general_comment = models.TextField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'live_workshop_participants'


class WOrganiser(models.Model):
    id = models.IntegerField(primary_key=True)
    organiser_id = models.IntegerField()
    academic_code = models.CharField(max_length=10)
    organiser_name = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'organiser'


class WResourcePerson(models.Model):
    id = models.IntegerField(primary_key=True)
    user_uid = models.IntegerField()
    rp_fname = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    states = models.CommaSeparatedIntegerField(max_length=200)
    state_code = models.CommaSeparatedIntegerField(max_length=200)

    class Meta:
        db_table = 'resource_person'


class WStudentDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    workshop_code = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=30)

    class Meta:
        db_table = 'student_detail'


class WTestDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    test_code = models.CharField(max_length=10)
    batch_no = models.BigIntegerField()
    no_of_participants = models.IntegerField()
    invigilator = models.CharField(max_length=200)
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'test_details'


class WTestRequests(models.Model):
    id = models.IntegerField(primary_key=True)
    test_code = models.CharField(max_length=20)
    academic_code = models.CharField(unique=True, max_length=10)
    organiser_id = models.IntegerField()
    department = models.CharField(max_length=100)
    invigilator_id = models.IntegerField()
    pref_test_date = models.DateField()
    cfm_test_date = models.DateField()
    pref_test_time = models.TimeField()
    cfm_test_time = models.TimeField()
    foss_category = models.CharField(max_length=100)
    status = models.IntegerField()
    workshop_code = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'test_requests'


class WAttendanceRegister(models.Model):
    id = models.IntegerField(primary_key=True)
    moodle_uid = models.IntegerField()
    test_code = models.CharField(max_length=10)
    status = models.IntegerField()

    class Meta:
        db_table = 'attendance_register'


class WWorkshopDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    workshop_code = models.CharField(max_length=10)
    no_of_participants = models.IntegerField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'workshop_details'


class WWorkshopFeedback(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    workshop_code = models.CharField(max_length=10)
    # foss_category = models.CharField(max_length=100)
    rate_workshop = models.IntegerField()
    rate_workshop_why = models.TextField()
    content = models.IntegerField()
    logical_arrangement = models.IntegerField()
    clarity = models.IntegerField()
    understandable = models.IntegerField()
    included_examples = models.IntegerField()
    instruction_sheet = models.IntegerField()
    assignments = models.IntegerField()
    pace_tutorial = models.IntegerField()
    useful_thing = models.TextField()
    weakness_duration = models.IntegerField()
    weakness_narration = models.IntegerField()
    weakness_understand = models.IntegerField()
    other_weakness = models.TextField()
    workshop_language = models.CharField(max_length=100)
    info_received = models.IntegerField()
    if_yes = models.TextField()
    comfortable_learning = models.IntegerField()
    working_computers = models.IntegerField()
    audio_quality = models.IntegerField()
    video_quality = models.IntegerField()
    orgn_wkshop = models.IntegerField()
    facil_learning = models.IntegerField()
    motiv_learning = models.IntegerField()
    time_mgmt = models.IntegerField()
    soft_klg = models.IntegerField()
    prov_expn = models.IntegerField()
    ans_cln = models.IntegerField()
    help_lern = models.IntegerField()
    exec_effly = models.IntegerField()
    ws_improved = models.TextField()
    recomm_wkshop = models.IntegerField()
    reason_why = models.TextField()
    general_comment = models.TextField()
    updated_at = models.DateTimeField()

    class Meta:
        db_table = 'workshop_feedback'


class WWorkshopRequests(models.Model):
    id = models.IntegerField(primary_key=True)
    workshop_code = models.CharField(max_length=10)
    academic_code = models.CharField(max_length=10)
    organiser_id = models.IntegerField()
    department = models.CharField(max_length=100)
    pref_wkshop_date = models.DateField()
    cfm_wkshop_date = models.DateField()
    pref_wkshop_time = models.TimeField()
    cfm_wkshop_time = models.TimeField()
    foss_category = models.CharField(max_length=100)
    pref_language = models.CharField(max_length=100)
    status = models.IntegerField()
    skype_request = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    school_standard = models.IntegerField()

    class Meta:
        db_table = 'workshop_requests'
