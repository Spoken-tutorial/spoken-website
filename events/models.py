from django.db import models

#import auth user models
from django.contrib.auth.models import User

#creation app models
from creation.models import FossCategory, Language, FossAvailableForWorkshop, FossAvailableForTest
from mdldjango.models import *

#validation
from django.core.exceptions import ValidationError

# Create your models here.
class State(models.Model):
    users = models.ManyToManyField(User, related_name="resource_person", through='ResourcePerson')
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length = 100)
    latitude = models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)
    longtitude = models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)
    img_map_area = models.TextField()
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("code","name"),)

class District(models.Model):
    state = models.ForeignKey(State)
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        unique_together = (("state", "code","name"),)
        #unique_together = (("state_id","name"),)

class City(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        unique_together = (("name","state"),)

class Location(models.Model):
    district = models.ForeignKey(District)
    name = models.CharField(max_length=200)
    pincode = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        unique_together = (("name","district","pincode"),)
    

class ResourcePerson(models.Model):
    user = models.ForeignKey(User)
    state = models.ForeignKey(State)
    assigned_by = models.PositiveIntegerField()
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name = "Resource Person"
        unique_together = (("user","state"),)

class University(models.Model):
    name = models.CharField(max_length=200)
    state = models.ForeignKey(State)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        unique_together = (("name","state"),)
        
class InstituteCategory(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        verbose_name = "Institute Categorie"
        
class InstituteType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        unique_together = (("name"),)
        
class AcademicCenter(models.Model):
    user = models.ForeignKey(User)
    state = models.ForeignKey(State)
    institution_type = models.ForeignKey(InstituteType)
    institute_category = models.ForeignKey(InstituteCategory)
    university = models.ForeignKey(University)
    academic_code = models.CharField(max_length=100, unique = True)
    institution_name = models.CharField(max_length=200)
    district = models.ForeignKey(District)
    location = models.ForeignKey(Location, null=True)
    city = models.ForeignKey(City)
    address = models.TextField()
    pincode = models.PositiveIntegerField()
    resource_center = models.BooleanField()
    rating = models.PositiveSmallIntegerField()
    contact_person = models.TextField()
    remarks = models.TextField()
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    class Meta:
        verbose_name = "Academic Center"
        #unique_together = (("institution_name","district"), ("institution_name","university"))
        
    def __unicode__(self):
        return self.institution_name
        
class Organiser(models.Model):
    user = models.OneToOneField(User, related_name = 'organiser')
    appoved_by = models.ForeignKey(User, related_name = 'organiser_approved_by', blank=True, null=True)
    academic = models.ForeignKey(AcademicCenter, blank=True, null=True)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.user.username

class Invigilator(models.Model):
    user = models.OneToOneField(User)
    appoved_by = models.ForeignKey(User, related_name = 'invigilator_approved_by', blank=True, null=True)
    academic = models.ForeignKey(AcademicCenter)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.user.username

class Department(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        unique_together = (("name"),)
        
class TrainingExtraFields(models.Model):
    paper_name = models.CharField(max_length = 200)
    approximate_hour = models.PositiveIntegerField(default = 0)
    online_test = models.PositiveIntegerField(default = 0)
    is_tutorial_useful = models.BooleanField(default = 0)
    future_training = models.BooleanField(default = 0)
    recommend_to_others = models.BooleanField(default = 0)
    no_of_lab_session = models.CharField(max_length = 30, null=True)
    
    
class Training(models.Model):
    organiser = models.ForeignKey(Organiser)
    appoved_by = models.ForeignKey(User, related_name = 'training_approved_by', null=True)
    academic = models.ForeignKey(AcademicCenter)
    course = models.ForeignKey(Course)
    training_type = models.PositiveIntegerField(default=0)
    training_code = models.CharField(max_length=100, null=True)
    department = models.ManyToManyField(Department)
    language = models.ForeignKey(Language)
    foss = models.ForeignKey(FossCategory)
    tdate = models.DateField()
    ttime = models.TimeField()
    skype = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0) #{0:request done, 1: attendance submit, 2: training manger approved, 3: mark attenda done, 4: complete, 5: rejected}
    extra_fields = models.OneToOneField(TrainingExtraFields, null = True)
    participant_count = models.PositiveIntegerField(default=0)
    trusted = models.BooleanField(default=1)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = (("organiser", "academic", "foss", "tdate", "ttime"),)

class TrainingAttendance(models.Model):
    training = models.ForeignKey(Training)
    mdluser_id = models.PositiveIntegerField(null=True, blank=True)
    firstname = models.CharField(max_length = 100, null=True)
    lastname = models.CharField(max_length = 100, null=True)
    gender = models.CharField(max_length=10, null=True)
    email = models.EmailField(null=True)
    password = models.CharField(max_length = 100, null=True)
    count = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name = "Training Attendance"
        #unique_together = (("training", "mdluser_id"))

'''class SchoolTrainingAttendance(models.Model):
    training = models.ForeignKey(Training)
    firstname = models.CharField(max_length = 100)
    lastname = models.CharField(max_length = 100)
    gender = models.CharField(max_length=10)
    email = models.EmailField(null=True)
    status = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name = "School Training Attendance"
'''
class TrainingLog(models.Model):
    user = models.ForeignKey(User)
    training = models.ForeignKey(Training)
    academic = models.ForeignKey(AcademicCenter)
    role = models.PositiveSmallIntegerField() #{0:'organiser', 1:'ResourcePerson', 2: 'Event Manager'}
    status = models.PositiveSmallIntegerField() #{0:'new', 1:'approved', 2:'completed', 3: 'rejected', 4:'update',  5:'Offline-Attendance submited', 6:'Marked Attendance'}
    created = models.DateTimeField(auto_now_add = True)
    
class TestCategory(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    
    def __unicode__(self):
        return self.name
        
class Test(models.Model):
    organiser = models.ForeignKey(Organiser, related_name = 'test_organiser')
    test_category = models.ForeignKey(TestCategory, related_name = 'test_category')
    appoved_by = models.ForeignKey(User, related_name = 'test_approved_by', null=True)
    invigilator = models.ForeignKey(Invigilator, related_name = 'test_invigilator', null=True)
    academic = models.ForeignKey(AcademicCenter)
    department = models.ManyToManyField(Department)
    training = models.ForeignKey('Training', null=True)
    foss = models.ForeignKey(FossCategory)
    test_code = models.CharField(max_length=100)
    tdate = models.DateField()
    ttime = models.TimeField()
    status = models.PositiveSmallIntegerField(default=0)
    participant_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = "Test Categorie"
        unique_together = (("organiser", "academic", "foss", "tdate", "ttime"),)

class TestAttendance(models.Model):
    test = models.ForeignKey(Test)
    mdluser_firstname = models.CharField(max_length = 100)
    mdluser_lastname = models.CharField(max_length = 100)
    mdluser_id = models.PositiveIntegerField()
    mdlcourse_id = models.PositiveIntegerField(default=0)
    mdlquiz_id = models.PositiveIntegerField(default=0)
    mdlattempt_id = models.PositiveIntegerField(default=0)
    password = models.CharField(max_length = 100, null=True)
    count = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name = "Test Attendance"
        unique_together = (("test", "mdluser_id"))

class TestLog(models.Model):
    user = models.ForeignKey(User)
    test = models.ForeignKey(Test)
    academic = models.ForeignKey(AcademicCenter)
    role = models.PositiveSmallIntegerField(default=0) #{0:'organiser', 1:'invigilator', 2:'ResourcePerson', 3: 'Event Manager'}
    status = models.PositiveSmallIntegerField(default=0) #{0:'new', 1:'RP-approved', 2:'Inv-approved', 3: 'ongoing', 4:'completed', 5:'Rp-rejected', 6:'Inv-rejected', 7:'Update', 8:'Attendance submited', 9:'Marked Attendance'}
    created = models.DateTimeField(auto_now_add = True)
    
class PermissionType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    def __unicode__(self):
        return self.name
        
class Permission(models.Model):
    permissiontype = models.ForeignKey(PermissionType)
    user = models.ForeignKey(User, related_name = 'permission_user')
    state = models.ForeignKey(State, related_name = 'permission_state')
    district = models.ForeignKey(District, related_name = 'permission_district', null=True)
    university = models.ForeignKey(University, related_name = 'permission_iniversity', null=True)
    institute_type = models.ForeignKey(InstituteType, related_name = 'permission_institution_type', null=True)
    institute = models.ForeignKey(AcademicCenter, related_name = 'permission_district', null=True)
    assigned_by = models.ForeignKey(User, related_name = 'permission_assigned_by')
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
class FossMdlCourses(models.Model):
    foss = models.ForeignKey(FossCategory)
    mdlcourse_id = models.PositiveIntegerField()
    mdlquiz_id = models.PositiveIntegerField()

class EventsNotification(models.Model):
    user = models.ForeignKey(User)
    role = models.PositiveSmallIntegerField(default=0) #{0:'organiser', 1:'invigilator', 2:'ResourcePerson', 3: 'Event Manager'}
    academic = models.ForeignKey(AcademicCenter)
    category = models.PositiveSmallIntegerField(default=0) #{'workshop', 'training', 'test'}
    categoryid = models.PositiveIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0) #{0:'new', 1:'update', 2:'approved', 3:'attendance', 4: 'completed', 5:'rejected'}
    message = models.CharField(max_length = 255)
    created = models.DateTimeField(auto_now_add = True)

class TrainingFeedback(models.Model):
    training = models.ForeignKey(Training)
    mdluser_id = models.PositiveIntegerField()
    rate_workshop = models.PositiveSmallIntegerField()
    
    content = models.PositiveSmallIntegerField()
    sequence = models.PositiveSmallIntegerField()
    clarity = models.PositiveSmallIntegerField()
    interesting = models.PositiveSmallIntegerField()
    appropriate_example = models.PositiveSmallIntegerField()
    instruction_sheet = models.PositiveSmallIntegerField()
    assignment = models.PositiveSmallIntegerField()
    
    pace_of_tutorial = models.PositiveSmallIntegerField()
    workshop_learnt = models.TextField()
    weakness_workshop = models.BooleanField()
    weakness_narration = models.BooleanField()
    weakness_understand = models.BooleanField()
    other_weakness = models.TextField()
    tutorial_language = models.PositiveSmallIntegerField()
    apply_information = models.PositiveSmallIntegerField()
    if_apply_information_yes = models.TextField()
    
    setup_learning = models.PositiveSmallIntegerField()
    computers_lab = models.PositiveSmallIntegerField()
    audio_quality = models.PositiveSmallIntegerField()
    video_quality = models.PositiveSmallIntegerField()

    workshop_orgainsation = models.PositiveSmallIntegerField()
    faciliate_learning = models.PositiveSmallIntegerField()
    motivate_learners = models.PositiveSmallIntegerField()
    time_management = models.PositiveSmallIntegerField()

    knowledge_about_software = models.PositiveSmallIntegerField()
    provide_clear_explanation = models.PositiveSmallIntegerField()
    answered_questions = models.PositiveSmallIntegerField()
    interested_helping = models.PositiveSmallIntegerField()
    executed_workshop = models.PositiveSmallIntegerField()
    workshop_improved = models.TextField()
    
    recommend_workshop = models.PositiveSmallIntegerField()
    reason_why = models.TextField()
    other_comments = models.TextField()
    created = models.DateTimeField(auto_now_add = True)
    class Meta:
        unique_together = (("training", "mdluser_id"))

class TrainingLanguageFeedback(models.Model):
    training = models.ForeignKey(Training)
    mdluser_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    medium_of_instruction = models.PositiveIntegerField()
    gender = models.BooleanField()
    language_prefered = models.ForeignKey(Language, null=True)
    tutorial_was_useful = models.PositiveIntegerField()
    learning_experience = models.PositiveIntegerField()
    satisfied_with_learning_experience = models.PositiveIntegerField()
    concept_explain_clearity = models.PositiveIntegerField()
    overall_learning_experience = models.PositiveIntegerField()
    user_interface = models.PositiveIntegerField()
    understanding_difficult_concept = models.PositiveIntegerField()
    curious_and_motivated = models.PositiveIntegerField()
    similar_tutorial_with_other_content = models.PositiveIntegerField()
    foss_tutorial_was_mentally_demanding = models.PositiveIntegerField()
    side_by_side_method_is_understood = models.PositiveIntegerField(default=0)
    
    compfortable_learning_in_language = models.PositiveIntegerField()
    confidence_level_in_language = models.PositiveIntegerField()
    preferred_language = models.PositiveIntegerField()
    preferred_language_reason = models.TextField()
    prefer_translation_in_mother_tongue = models.PositiveIntegerField()
    prefer_translation_in_mother_tongue_reason = models.TextField()
    side_by_side_method_meant = models.PositiveIntegerField()
    side_by_side_method_is_beneficial = models.PositiveIntegerField()
    side_by_side_method_is_beneficial_reason = models.TextField()
    limitations_of_side_by_side_method = models.TextField()
    
    content_information_flow = models.PositiveIntegerField()
    content_appropriate_examples = models.PositiveIntegerField()
    content_ease_of_understanding = models.PositiveIntegerField()
    content_clarity_of_instruction_sheet = models.PositiveIntegerField()
    content_ease_of_performing_assignment = models.PositiveIntegerField()
    content_best_features = models.TextField()
    content_areas_of_improvement = models.TextField()
    
    video_audio_video_synchronization = models.PositiveIntegerField()
    video_attractive_color_features = models.PositiveIntegerField()
    video_text_readable = models.PositiveIntegerField()
    video_best_features = models.TextField()
    video_areas_of_improvement = models.TextField()
    
    audio_pleasant_speech_and_accent = models.PositiveIntegerField()
    audio_soothing_and_friendly_tone = models.PositiveIntegerField()
    audio_understandable_and_clear_speech = models.PositiveIntegerField()
    audio_best_features = models.TextField()
    audio_areas_of_improvement = models.TextField()
    
    side_by_side_method_is_effective = models.PositiveIntegerField(default=0)
    side_by_side_method_is = models.PositiveIntegerField(default=0)
    
    created = models.DateTimeField(auto_now_add = True)
    class Meta:
        unique_together = (("training", "mdluser_id"))
    

class Testimonials(models.Model):
    user = models.ForeignKey(User, related_name = 'testimonial_created_by')
    approved_by = models.ForeignKey(User, related_name = 'testimonial_approved_by', null=True)
    user_name = models.CharField(max_length=200)
    actual_content = models.TextField()
    minified_content = models.TextField()
    short_description = models.TextField()
    source_title = models.CharField(max_length=200, null=True)
    source_link = models.URLField(null = True)
    status = models.PositiveSmallIntegerField(default = 0)
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)

class TrainingLiveFeedback(models.Model):
    training = models.ForeignKey(Training)
    
    rate_workshop = models.PositiveSmallIntegerField()
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    branch = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    
    content = models.PositiveSmallIntegerField()
    sequence = models.PositiveSmallIntegerField()
    clarity = models.PositiveSmallIntegerField()
    interesting = models.PositiveSmallIntegerField()
    appropriate_example = models.PositiveSmallIntegerField()
    instruction_sheet = models.PositiveSmallIntegerField()
    assignment = models.PositiveSmallIntegerField()
    
    pace_of_tutorial = models.PositiveSmallIntegerField()
    workshop_learnt = models.TextField()
    weakness_workshop = models.BooleanField()
    weakness_narration = models.BooleanField()
    weakness_understand = models.BooleanField()
    other_weakness = models.TextField()
    tutorial_language = models.PositiveSmallIntegerField()
    apply_information = models.PositiveSmallIntegerField()
    if_apply_information_yes = models.TextField()
    
    setup_learning = models.PositiveSmallIntegerField()
    computers_lab = models.PositiveSmallIntegerField()
    audio_quality = models.PositiveSmallIntegerField()
    video_quality = models.PositiveSmallIntegerField()

    workshop_orgainsation = models.PositiveSmallIntegerField()
    faciliate_learning = models.PositiveSmallIntegerField()
    motivate_learners = models.PositiveSmallIntegerField()
    time_management = models.PositiveSmallIntegerField()

    knowledge_about_software = models.PositiveSmallIntegerField()
    provide_clear_explanation = models.PositiveSmallIntegerField()
    answered_questions = models.PositiveSmallIntegerField()
    interested_helping = models.PositiveSmallIntegerField()
    executed_workshop = models.PositiveSmallIntegerField()
    workshop_improved = models.TextField()
    
    recommend_workshop = models.PositiveSmallIntegerField()
    reason_why = models.TextField()
    other_comments = models.TextField()
    created = models.DateTimeField(auto_now_add = True)
    class Meta:
        unique_together = (("training", "email"))

class OrganiserNotification(models.Model):
    user = models.ForeignKey(User)
