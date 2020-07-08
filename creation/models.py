# Third Party Stuff

from builtins import object
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
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
    show_on_homepage = models.PositiveSmallIntegerField(default=0, help_text ='0:Display on home page, 1:Series, 2:Archived')
    available_for_nasscom = models.BooleanField(default=True, help_text ='If unchecked, this foss will not be available for nasscom' )

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