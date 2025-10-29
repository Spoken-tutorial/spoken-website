from django.db import models

class ILWMdlUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=96)
    idnumber = models.CharField(max_length=765)
    firstname = models.CharField(max_length=300)
    lastname = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    class Meta(object):
        db_table = 'mdl_user'
        
class ILWMdlQuizGrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    quiz = models.BigIntegerField()
    userid = models.BigIntegerField()
    grade = models.DecimalField(max_digits=12, decimal_places=5)
    timemodified = models.BigIntegerField()
    class Meta(object):
        db_table = 'mdl_quiz_grades'

class ILWMdlQuizAttempts(models.Model):
    id = models.BigIntegerField(primary_key=True)
    quiz = models.BigIntegerField()
    userid = models.BigIntegerField()
    attempt = models.IntegerField(unique=True)
    uniqueid = models.BigIntegerField(unique=True)
    layout = models.TextField()
    currentpage = models.BigIntegerField()
    preview = models.IntegerField()
    state = models.CharField(max_length=48)
    timestart = models.BigIntegerField()
    timefinish = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    timemodifiedoffline = models.BigIntegerField()
    timecheckstate = models.BigIntegerField(null=True, blank=True)
    sumgrades = models.DecimalField(null=True, max_digits=12, decimal_places=5, blank=True)
    class Meta(object):
        db_table = 'mdl_quiz_attempts'

class ILWMdlUserEnrolments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    status = models.BigIntegerField()
    enrolid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timestart = models.BigIntegerField()
    timeend = models.BigIntegerField()
    modifierid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    class Meta(object):
        db_table = 'mdl_user_enrolments'

class ILWMdlEnrol(models.Model):
    id = models.BigIntegerField(primary_key=True)
    enrol = models.CharField(max_length=60)
    status = models.BigIntegerField()
    courseid = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    name = models.CharField(max_length=765, blank=True)
    enrolperiod = models.BigIntegerField(null=True, blank=True)
    enrolstartdate = models.BigIntegerField(null=True, blank=True)
    enrolenddate = models.BigIntegerField(null=True, blank=True)
    expirynotify = models.IntegerField(null=True, blank=True)
    expirythreshold = models.BigIntegerField(null=True, blank=True)
    notifyall = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=150, blank=True)
    cost = models.CharField(max_length=60, blank=True)
    currency = models.CharField(max_length=9, blank=True)
    roleid = models.BigIntegerField(null=True, blank=True)
    customint1 = models.BigIntegerField(null=True, blank=True)
    customint2 = models.BigIntegerField(null=True, blank=True)
    customint3 = models.BigIntegerField(null=True, blank=True)
    customint4 = models.BigIntegerField(null=True, blank=True)
    customint5 = models.BigIntegerField(null=True, blank=True)
    customint6 = models.BigIntegerField(null=True, blank=True)
    customint7 = models.BigIntegerField(null=True, blank=True)
    customint8 = models.BigIntegerField(null=True, blank=True)
    customchar1 = models.CharField(max_length=765, blank=True)
    customchar2 = models.CharField(max_length=765, blank=True)
    customchar3 = models.CharField(max_length=3999, blank=True)
    customdec1 = models.DecimalField(null=True, max_digits=14, decimal_places=7, blank=True)
    customdec2 = models.DecimalField(null=True, max_digits=14, decimal_places=7, blank=True)
    customtext1 = models.TextField(blank=True)
    customtext2 = models.TextField(blank=True)
    customtext3 = models.TextField(blank=True)
    customtext4 = models.TextField(blank=True)
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    class Meta(object):
        db_table = 'mdl_enrol'

class ILWMdlRoleAssignments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    roleid = models.BigIntegerField()
    contextid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    modifierid = models.BigIntegerField()
    component = models.CharField(max_length=300)
    itemid = models.BigIntegerField()
    sortorder = models.BigIntegerField()
    class Meta(object):
        db_table = 'mdl_role_assignments'
