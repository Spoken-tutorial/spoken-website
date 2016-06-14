from django.db import models


class MdlUser(models.Model):
    id = models.BigIntegerField(primary_key=True)
    auth = models.CharField(max_length=60)
    confirmed = models.IntegerField()
    # policyagreed = models.IntegerField()
    # deleted = models.IntegerField()
    gender = models.CharField(max_length=100, null=True, blank=True, default='0')
    age_range = models.CharField(max_length=100, null=True, blank=True, default='0')
    academic_code = models.CharField(max_length=100, null=True, blank=True, default='0')
    organizer = models.CharField(max_length=100, null=True, blank=True, default='0')
    invigilator = models.CharField(max_length=100, null=True, blank=True, default='0')
    flag = models.CharField(max_length=100, null=True, blank=True, default='0')

    # suspended = models.IntegerField()
    mnethostid = models.BigIntegerField(unique=True)
    username = models.CharField(unique=True, max_length=255)
    password = models.CharField(max_length=96)
    idnumber = models.CharField(max_length=765)
    firstname = models.CharField(max_length=300)
    lastname = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    # emailstop = models.IntegerField()
    icq = models.CharField(max_length=45)
    skype = models.CharField(max_length=150)
    yahoo = models.CharField(max_length=150)
    aim = models.CharField(max_length=150)
    msn = models.CharField(max_length=150)
    phone1 = models.CharField(max_length=60)
    phone2 = models.CharField(max_length=60)
    institution = models.CharField(max_length=120)
    department = models.CharField(max_length=90)
    address = models.CharField(max_length=210)
    city = models.CharField(max_length=360)
    country = models.CharField(max_length=6)
    # lang = models.CharField(max_length=90)
    theme = models.CharField(max_length=150)
    timezone = models.CharField(max_length=300)
    # firstaccess = models.BigIntegerField()
    # lastaccess = models.BigIntegerField()
    # lastlogin = models.BigIntegerField()
    # currentlogin = models.BigIntegerField()
    lastip = models.CharField(max_length=135)
    secret = models.CharField(max_length=45)
    # picture = models.BigIntegerField()
    url = models.CharField(max_length=765)
    description = models.TextField(blank=True)
    # descriptionformat = models.IntegerField()
    # mailformat = models.IntegerField()
    # maildigest = models.IntegerField()
    # maildisplay = models.IntegerField()
    # htmleditor = models.IntegerField()
    # autosubscribe = models.IntegerField()
    # trackforums = models.IntegerField()
    # timecreated = models.BigIntegerField()
    # timemodified = models.BigIntegerField()
    # trustbitmask = models.BigIntegerField()
    imagealt = models.CharField(max_length=765, blank=True)

    class Meta:
        db_table = u'mdl_user'


class MdlQuizGrades(models.Model):
    id = models.BigIntegerField(primary_key=True)
    quiz = models.BigIntegerField()
    userid = models.BigIntegerField()
    grade = models.DecimalField(max_digits=12, decimal_places=5)
    timemodified = models.BigIntegerField()

    class Meta:
        db_table = u'mdl_quiz_grades'


class MdlQuizAttempts(models.Model):
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
    timecheckstate = models.BigIntegerField(null=True, blank=True)
    sumgrades = models.DecimalField(null=True, max_digits=12, decimal_places=5, blank=True)
    needsupgradetonewqe = models.IntegerField()

    class Meta:
        db_table = u'mdl_quiz_attempts'


class MdlUserEnrolments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    status = models.BigIntegerField()
    enrolid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timestart = models.BigIntegerField()
    timeend = models.BigIntegerField()
    modifierid = models.BigIntegerField()
    timecreated = models.BigIntegerField()
    timemodified = models.BigIntegerField()

    class Meta:
        db_table = u'mdl_user_enrolments'


class MdlEnrol(models.Model):
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

    class Meta:
        db_table = u'mdl_enrol'


class MdlRoleAssignments(models.Model):
    id = models.BigIntegerField(primary_key=True)
    roleid = models.BigIntegerField()
    contextid = models.BigIntegerField()
    userid = models.BigIntegerField()
    timemodified = models.BigIntegerField()
    modifierid = models.BigIntegerField()
    component = models.CharField(max_length=300)
    itemid = models.BigIntegerField()
    sortorder = models.BigIntegerField()

    class Meta:
        db_table = u'mdl_role_assignments'
