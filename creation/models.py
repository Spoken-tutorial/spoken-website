# Third Party Stuff
from django.contrib.auth.models import User
from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    code = models.CharField(max_length=10, default='en')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class FossSuperCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FOSS Category'
        verbose_name_plural = 'FOSS Categories'
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class FossCategory(models.Model):
    foss = models.CharField(unique=True, max_length=255)
    description = models.TextField()
    status = models.BooleanField(max_length=2)
    is_learners_allowed = models.BooleanField(max_length=2,default=0 )
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    category = models.ManyToManyField(FossSuperCategory)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    show_on_homepage = models.BooleanField(default=True, help_text ='If unchecked, this foss will be displayed on series page, instead of home page' )

    class Meta:
        verbose_name = 'FOSS'
        verbose_name_plural = 'FOSSes'
        ordering = ('foss', )

    def __unicode__(self):
        return self.foss


class BrochureDocument(models.Model):
    foss_course = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    foss_language = models.ForeignKey(Language, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FOSS Brochure'
        verbose_name_plural = 'FOSS Brochures'

    def __unicode__(self):
        return self.foss_course.foss


class BrochurePage(models.Model):
    brochure = models.ForeignKey(BrochureDocument, related_name='pages', on_delete=models.PROTECT )
    page = models.FileField(upload_to='brochures/')
    page_no = models.PositiveIntegerField()

    class Meta:
        ordering = ('page_no', )
        unique_together = (('brochure', 'page_no'),)


class PlaylistInfo(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    playlist_id = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Playlist Info'
        unique_together = (('foss', 'language'),)

    def __unicode__(self):
        return self.playlist_id


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(PlaylistInfo, on_delete=models.PROTECT )
    item_id = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Playlist Item'
        unique_together = (('playlist', 'item_id'),)


class Level(models.Model):
    level = models.CharField(max_length=255)
    code = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Tutorial Level'

    def __unicode__(self):
        return self.level


class TutorialDetail(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    tutorial = models.CharField(max_length=255)
    level = models.ForeignKey(Level, on_delete=models.PROTECT )
    order = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tutorial Detail'
        unique_together = (('foss', 'tutorial', 'level'),)

    def __unicode__(self):
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

    class Meta:
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

    class Meta:
        unique_together = (('tutorial_detail', 'language',),)


class ArchivedVideo(models.Model):
    tutorial_resource = models.ForeignKey(TutorialResource, on_delete=models.PROTECT )
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    version = models.PositiveSmallIntegerField(default=0)
    video = models.CharField(max_length=255)
    atype = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class ContributorRole(models.Model):
    foss_category = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'foss_category', 'language',),)
        verbose_name = 'Contributor Role'


class DomainReviewerRole(models.Model):
    foss_category = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'foss_category', 'language',),)
        verbose_name = 'Domain Reviewer Role'


class QualityReviewerRole(models.Model):
    foss_category = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
    status = models.PositiveSmallIntegerField(default=0)
    approved_user = models.ForeignKey(
        User, related_name='approved_user', null=True, blank=True, on_delete=models.PROTECT )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'role_type',),)


class FossAvailableForWorkshop(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('foss', 'language'),)


class FossAvailableForTest(models.Model):
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    language = models.ForeignKey(Language, on_delete=models.PROTECT )
    status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
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


class OperatingSystem(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class SuggestTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    topic_title = models.CharField(max_length=255)
    difficulty_level = models.ForeignKey(Level, on_delete=models.PROTECT )
    operating_system = models.ManyToManyField(OperatingSystem)
    brief_description = models.TextField()
    example_suggestion = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.topic_title


class SuggestExample(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    topic_title = models.CharField(max_length=255)
    example_description = models.TextField()
    script_writer = models.BooleanField()
    is_reviewer = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.topic_title


class ContributeTowards(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
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
