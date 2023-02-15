# Third Party Stuff

from builtins import object
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
import uuid
from datetime import timedelta, date

from django.db.models import Q
'''
payment rate
script user == 1300 per 10 min
video user == 700 per 10 min
both == 2000 per 10 min
'''
PAY_PER_SEC = [0, (13.0 / 6), (7.0 / 6.0), (20.0 / 6)]

PAYMENT_STATUS = (
    (0, 'Payment Cancelled'),
    (1, 'Payment Due'),
    (2, 'Payment Initiated'),
)

USER_TYPE = (
    (1, 'Script User'),
    (2, 'Video User'),
    (3, 'Script & Video User'),
)

HONORARIUM_STATUS = (
    (1, 'In Process'),
    (2, 'Forwarded'),
    (3, 'Completed'),
    (4, 'Confirmed'),
    (5, 'Agreement Accepted'),
    (6, 'Receipt Accepted'),
    (11, 'All accepted and closed'),
)

import datetime


@python_2_unicode_compatible
class Language(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    code = models.CharField(max_length=10, default='en')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        ordering = ('name',)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class FossSuperCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    specialisation = models.CharField(max_length=255, default='Programming Language')
    # Some of the Fosses are part of Recommendation System
    part_of_recsys = models.BooleanField(max_length=2, default=False)

    class Meta(object):
        verbose_name = 'FOSS Category'
        verbose_name_plural = 'FOSS Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class FossCategory(models.Model):
    foss = models.CharField(unique=True, max_length=255)
    description = models.TextField()
    status = models.BooleanField(max_length=2)
    is_learners_allowed = models.BooleanField(max_length=2,default=0 )
    is_translation_allowed = models.BooleanField(max_length=2, default=0)
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    category = models.ManyToManyField(FossSuperCategory)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    show_on_homepage = models.PositiveSmallIntegerField(default=0, help_text ='0:Series, 1:Display on home page, 2:Archived')
    available_for_nasscom = models.BooleanField(default=True, help_text ='If unchecked, this foss will not be available for nasscom' )
    available_for_jio = models.BooleanField(default=True, help_text ='If unchecked, this foss will not be available for jio, csc and spoken-tutorial.in' )
    csc_dca_programme = models.BooleanField(default=True, help_text ='If unchecked, this foss will not be available for csc-dca programme' )
    credits = models.PositiveSmallIntegerField(default=0)
    is_fossee = models.BooleanField(default=False)
    class Meta(object):
        verbose_name = 'FOSS'
        verbose_name_plural = 'FOSSes'
        ordering = ('foss', )

    def __str__(self):
        return self.foss


@python_2_unicode_compatible
class BrochureDocument(models.Model):
    foss_course = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    foss_language = models.ForeignKey(Language, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        verbose_name = 'FOSS Brochure'
        verbose_name_plural = 'FOSS Brochures'

    def __str__(self):
        return self.foss_course.foss


class BrochurePage(models.Model):
    brochure = models.ForeignKey(BrochureDocument, related_name='pages', on_delete=models.PROTECT )
    page = models.FileField(upload_to='brochures/')
    page_no = models.PositiveIntegerField()

    class Meta(object):
        ordering = ('page_no', )
        unique_together = (('brochure', 'page_no'),)


@python_2_unicode_compatible
class PlaylistInfo(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    playlist_id = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        verbose_name = 'Playlist Info'
        unique_together = (('foss', 'language'),)

    def __str__(self):
        return self.playlist_id


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(PlaylistInfo, on_delete=models.PROTECT )
    item_id = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        verbose_name = 'Playlist Item'
        unique_together = (('playlist', 'item_id'),)


@python_2_unicode_compatible
class Level(models.Model):
    level = models.CharField(max_length=255)
    code = models.CharField(max_length=10)

    class Meta(object):
        verbose_name = 'Tutorial Level'

    def __str__(self):
        return self.level


@python_2_unicode_compatible
class TutorialDetail(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    tutorial = models.CharField(max_length=255)
    level = models.ForeignKey(Level, on_delete=models.PROTECT )
    order = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        verbose_name = 'Tutorial Detail'
        unique_together = (('foss', 'tutorial', 'level'),)

    def __str__(self):
        return self.tutorial


class TutorialCommonContent(models.Model):
    tutorial_detail = models.OneToOneField(
        TutorialDetail, related_name='tutorial_detail',on_delete=models.PROTECT)
    slide = models.CharField(max_length=255)
    slide_user = models.ForeignKey(User, related_name='slides', on_delete=models.PROTECT )
    slide_status = models.PositiveSmallIntegerField(default=0)

    code = models.CharField(max_length=255)
    code_user = models.ForeignKey(User, related_name='codes', on_delete=models.PROTECT )
    code_status = models.PositiveSmallIntegerField(default=0)

    assignment = models.CharField(max_length=255)
    assignment_user = models.ForeignKey(User, related_name='assignments', on_delete=models.PROTECT )
    assignment_status = models.PositiveSmallIntegerField(default=0)

    prerequisite = models.ForeignKey(
        TutorialDetail, related_name='prerequisite', blank=True, null=True, on_delete=models.PROTECT )
    prerequisite_user = models.ForeignKey(User, related_name='prerequisite', on_delete=models.PROTECT )
    prerequisite_status = models.PositiveSmallIntegerField(default=0)

    additional_material = models.CharField(
        max_length=255, blank=True, null=True)
    additional_material_user = models.ForeignKey(
        User, related_name='additional_material', null=True, default=None, on_delete=models.PROTECT )
    additional_material_status = models.PositiveSmallIntegerField(default=0)

    keyword = models.TextField()
    keyword_user = models.ForeignKey(User, related_name='keywords', on_delete=models.PROTECT )
    keyword_status = models.PositiveSmallIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta(object):
        verbose_name = 'Tutorial Common Content'

    def keyword_as_list(self):
        return self.keyword.split(',')


class TutorialResource(models.Model):
    tutorial_detail = models.ForeignKey(TutorialDetail, on_delete=models.PROTECT )
    common_content = models.ForeignKey(TutorialCommonContent, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )

    outline = models.TextField()
    outline_user = models.ForeignKey(User, related_name='outlines', on_delete=models.PROTECT )
    outline_status = models.PositiveSmallIntegerField(default=0)

    script = models.URLField(max_length=255)
    script_user = models.ForeignKey(User, related_name='scripts', on_delete=models.PROTECT )
    script_status = models.PositiveSmallIntegerField(default=0)
    timed_script = models.URLField(max_length=255)

    video = models.CharField(max_length=255)
    video_id = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    playlist_item_id = models.CharField(
        max_length=255, null=True, blank=True, default=None)
    video_thumbnail_time = models.TimeField(default='00:00:00')
    video_user = models.ForeignKey(User, related_name='videos', on_delete=models.PROTECT )
    video_status = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    version = models.PositiveSmallIntegerField(default=0)
    hit_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    publish_at = models.DateTimeField(null=True)
    # the last submission date for the tutorial
    submissiondate = models.DateTimeField(default=datetime.datetime(2000, 1, 2, 12, 00))
    # 0 - Not Assigned to anyone , 1 - Assigned & work in progress , 2 - Completed (= published / PR )
    assignment_status = models.PositiveSmallIntegerField(default=0)
    # 0 - Not Extended , 1 - Extended , 2 - Tutorial Terminated from user
    extension_status = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('tutorial_detail', 'language',)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('watch_tutorial', args=[self.tutorial_detail.foss.foss, self.tutorial_detail.tutorial, self.language])


class PaymentHonorarium(models.Model):
    amount = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    code = models.CharField(max_length=20, editable=False)
    initiated_by = models.ForeignKey(User, related_name="initiator",default=7)
    status = models.PositiveSmallIntegerField(default=1, choices=HONORARIUM_STATUS)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Generating custom Honorarium code
        """
        if not self.id:
            try:
                last_id = PaymentHonorarium.objects.order_by('-id')[0].id
            except IndexError:
                last_id = 0
            unique_id = last_id + 1
            today = datetime.date.today()
            self.code = "PH-{year}-{month:02n}-{unique_id:05n}".format(year=today.year, month=today.month, unique_id=unique_id)
        super(self.__class__, self).save(*args, **kwargs)


class TutorialPayment(models.Model):
    user = models.ForeignKey(User, related_name="contributor",)
    tutorial_resource = models.ForeignKey(TutorialResource)
    payment_honorarium = models.ForeignKey('PaymentHonorarium', related_name="tutorials", null=True, blank=True, on_delete=models.SET_NULL)
    user_type = models.PositiveSmallIntegerField(default=3, choices=USER_TYPE)
    seconds = models.PositiveIntegerField(default=0, help_text="Tutorial duration in seconds")
    amount = models.DecimalField(default=0, max_digits=7, decimal_places=2)
    status = models.PositiveSmallIntegerField(default=1, choices=PAYMENT_STATUS)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('tutorial_resource', 'user'),)

    def get_duration(self):
        """Displays time from seconds to hh:mm:ss format"""
        return str(datetime.timedelta(seconds=self.seconds))

    def save(self, *args, **kwargs):
        try:
            pps = PAY_PER_SEC[self.user_type]
            self.amount = round(pps * self.seconds, 2)
        except:
            print("An Error Occured. User_Type is beyond 3 causing list index out of range")
        super(TutorialPayment, self).save(*args, **kwargs)


class BankDetail(models.Model):
    """
        To store bank account details of external contributor
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        limit_choices_to=Q(groups__name='External-Contributor')
    )
    account_name = models.CharField(max_length=100,default=None)
    account_number = models.CharField(max_length=17)
    bankaddress = models.CharField(max_length=255, default=None)
    pancard = models.CharField(max_length=10, default=None)
    ifsc = models.CharField(max_length=11)
    bank = models.CharField(max_length=30)
    branch = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10,default=0)#India - 6, World -10
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    vendor = models.CharField(max_length=11,default=0)
    vendoraddress = models.CharField(max_length=255, default=None)


class ArchivedVideo(models.Model):
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    version = models.PositiveSmallIntegerField(default=0)
    video = models.CharField(max_length=255)
    atype = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class ContributorRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    foss_category = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    tutorial_detail = models.ForeignKey(TutorialDetail, null=True)
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def revoke(self):
        self.status = 0
        self.save()

    class Meta(object):
        unique_together = (('user', 'tutorial_detail', 'language',),)
        verbose_name = 'Contributor Role'



class DomainReviewerRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    foss_category = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def revoke(self):
        self.status = 0
        self.save()

    class Meta:
        unique_together = (('user', 'foss_category', 'language',),)
        verbose_name = 'Domain Reviewer Role'


class QualityReviewerRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    foss_category = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def revoke(self):
        self.status = 0
        self.save()

    class Meta:
        unique_together = (('user', 'foss_category', 'language',),)
        verbose_name = 'Quality Reviewer Role'


class ContributorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    component = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)


class AdminReviewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)


class DomainReviewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    component = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)


class QualityReviewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    component = models.CharField(max_length=255)
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)


class PublicReviewLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)


class PublishTutorialLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)


class NeedImprovementLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    review_state = models.PositiveSmallIntegerField()
    component = models.CharField(max_length=50)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class ContributorNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    title = models.CharField(max_length=255)
    message = models.TextField()
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)


class AdminReviewerNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    title = models.CharField(max_length=255)
    message = models.TextField()
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)


class DomainReviewerNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    title = models.CharField(max_length=255)
    message = models.TextField()
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)


class QualityReviewerNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    title = models.CharField(max_length=255)
    message = models.TextField()
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)


class RoleRequest(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.PROTECT )
    role_type = models.IntegerField(default=0)
    language = models.ForeignKey(Language, null=True)
    status = models.PositiveSmallIntegerField(default=0)
    approved_user = models.ForeignKey(
        User, related_name='approved_user', null=True, blank=True, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def revoke(self):
        self.status = 2
        self.save()

    class Meta:
        unique_together = (('user', 'role_type', 'language'),)



class FossAvailableForWorkshop(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        unique_together = (('foss', 'language'),)


class FossAvailableForTest(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        unique_together = (('foss', 'language'),)


class TutorialMissingComponent(models.Model):
    user = models.ForeignKey(
        User, related_name='raised_user', null=True, blank=True, on_delete=models.PROTECT )
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    component = models.PositiveSmallIntegerField()
    report_type = models.BooleanField(default=0)
    remarks = models.TextField(null=True, blank=True)
    inform_me = models.BooleanField(default=0)
    email = models.CharField(max_length=255, null=True, blank=True)
    reply_status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class TutorialMissingComponentReply(models.Model):
    missing_component = models.ForeignKey(TutorialMissingComponent, on_delete=models.PROTECT )
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    reply_message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


@python_2_unicode_compatible
class OperatingSystem(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class SuggestTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    topic_title = models.CharField(max_length=255)
    difficulty_level = models.ForeignKey(Level, on_delete=models.PROTECT )
    operating_system = models.ManyToManyField(OperatingSystem)
    brief_description = models.TextField()
    example_suggestion = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic_title


@python_2_unicode_compatible
class SuggestExample(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    topic_title = models.CharField(max_length=255)
    example_description = models.TextField()
    script_writer = models.BooleanField()
    is_reviewer = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic_title


@python_2_unicode_compatible
class ContributeTowards(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Collaborate(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    contact_number = models.CharField(max_length=20, null=True)
    institution_name = models.CharField(max_length=255)
    foss_name = models.CharField(max_length=255)
    are_you_one = models.CharField(max_length=255)
    contribute_towards = models.ManyToManyField(ContributeTowards)
    howmuch_time = models.PositiveIntegerField()
    availability_constraints = models.TextField(null=True, blank=True)
    is_reviewer = models.BooleanField()
    contribs_foss = models.TextField(null=True, blank=True)
    educational_qualifications = models.TextField(null=True, blank=True)
    prof_experience = models.CharField(max_length=255, null=True, blank=True)
    lang_contributor = models.BooleanField()
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    lead_st = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)


class ContributorRating(models.Model):
    user = models.ForeignKey(User)
    choices = ((0,0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
    rating = models.PositiveIntegerField(choices=choices,default=0)
    language = models.ForeignKey(Language)

    class Meta:
        unique_together = (('user', 'language'),)


class TutorialsAvailable(models.Model):
    tutorial_detail = models.ForeignKey(TutorialDetail)
    language = models.ForeignKey(Language)

    class Meta:
        unique_together = (('tutorial_detail', 'language'),)


class LanguageManager(models.Model):

    user = models.ForeignKey(User)
    language = models.ForeignKey(Language)
    status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('user', 'language')
        unique_together = (('user', 'language'),)

class TutorialDuration(models.Model):
    tresource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT , null=True)
    duration = models.CharField(max_length=15)
    created = models.DateTimeField(null=True)
