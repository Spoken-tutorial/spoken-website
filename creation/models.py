from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Language(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.name

class FossCategory(models.Model):
    foss = models.CharField(unique=True, max_length = 255)
    description = models.TextField()
    status = models.BooleanField(max_length = 2)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'FOSS Category'

    def __unicode__(self):
        return self.foss

class Level(models.Model):
    level = models.CharField(max_length = 255)
    code = models.CharField(max_length = 10)

    class Meta:
        verbose_name = 'Tutorial Level'

    def __unicode__(self):
        return self.level

class TutorialDetail(models.Model):
    foss = models.ForeignKey(FossCategory)
    tutorial = models.CharField(max_length = 255)
    level = models.ForeignKey(Level)
    order = models.IntegerField()
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Tutorial Detail'
        unique_together = (('foss', 'tutorial', 'level'),)

    def __unicode__(self):
        return self.tutorial

class TutorialCommonContent(models.Model):
    tutorial_detail = models.ForeignKey(TutorialDetail, unique=True, related_name='tutorial_detail')
    slide = models.CharField(max_length = 255)
    slide_user = models.ForeignKey(User, related_name='slides')
    slide_status = models.PositiveSmallIntegerField(default = 0)

    code = models.CharField(max_length = 255)
    code_user = models.ForeignKey(User, related_name='codes')
    code_status = models.PositiveSmallIntegerField(default = 0)

    assignment = models.CharField(max_length = 255)
    assignment_user = models.ForeignKey(User, related_name='assignments')
    assignment_status = models.PositiveSmallIntegerField(default = 0)

    prerequisite = models.ForeignKey(TutorialDetail, related_name='prerequisite', blank=True, null=True)
    prerequisite_user = models.ForeignKey(User, related_name='prerequisite')
    prerequisite_status = models.PositiveSmallIntegerField(default = 0)

    keyword = models.TextField()
    keyword_user = models.ForeignKey(User, related_name='keywords')
    keyword_status = models.PositiveSmallIntegerField(default = 0)

    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        verbose_name = 'Tutorial Common Content'

class TutorialResource(models.Model):
    tutorial_detail = models.ForeignKey(TutorialDetail)
    common_content = models.ForeignKey(TutorialCommonContent)
    language = models.ForeignKey(Language)

    outline = models.TextField()
    outline_user = models.ForeignKey(User, related_name='outlines')
    outline_status = models.PositiveSmallIntegerField(default = 0)

    script = models.URLField(max_length = 255)
    script_user = models.ForeignKey(User, related_name='scripts')
    script_status = models.PositiveSmallIntegerField(default = 0)
    timed_script = models.URLField(max_length = 255)

    video = models.CharField(max_length = 255)
    video_user = models.ForeignKey(User, related_name='videos')
    video_status = models.PositiveSmallIntegerField(default = 0)

    status = models.PositiveSmallIntegerField(default = 0)
    version = models.PositiveSmallIntegerField(default = 0)
    hit_count = models.PositiveIntegerField(default = 0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = (('tutorial_detail', 'language',),)

class ArchivedVideo(models.Model):
    tutorial_resource = models.ForeignKey(TutorialResource)
    user = models.ForeignKey(User)
    version = models.PositiveSmallIntegerField(default = 0)
    video = models.CharField(max_length = 255)
    atype = models.PositiveSmallIntegerField(default = 0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

class ContributorRole(models.Model):
    foss_category = models.ForeignKey(FossCategory)
    language = models.ForeignKey(Language)
    user = models.ForeignKey(User)
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = (('user','foss_category', 'language',),)
        verbose_name = 'Contributor Role'

class DomainReviewerRole(models.Model):
    foss_category = models.ForeignKey(FossCategory)
    language = models.ForeignKey(Language)
    user = models.ForeignKey(User)
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = (('user','foss_category', 'language',),)
        verbose_name = 'Domain Reviewer Role'

class QualityReviewerRole(models.Model):
    foss_category = models.ForeignKey(FossCategory)
    language = models.ForeignKey(Language)
    user = models.ForeignKey(User)
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = (('user','foss_category', 'language',),)
        verbose_name = 'Quality Reviewer Role'

class ContributorLog(models.Model):
    user = models.ForeignKey(User)
    tutorial_resource = models.ForeignKey(TutorialResource)
    component = models.CharField(max_length = 255)
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add = True)

class AdminReviewLog(models.Model):
    user = models.ForeignKey(User)
    tutorial_resource = models.ForeignKey(TutorialResource)
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add = True)

class DomainReviewLog(models.Model):
    user = models.ForeignKey(User)
    tutorial_resource = models.ForeignKey(TutorialResource)
    component = models.CharField(max_length = 255)
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add = True)

class QualityReviewLog(models.Model):
    user = models.ForeignKey(User)
    tutorial_resource = models.ForeignKey(TutorialResource)
    component = models.CharField(max_length = 255)
    status = models.PositiveSmallIntegerField()
    created = models.DateTimeField(auto_now_add = True)

class PublicReviewLog(models.Model):
    user = models.ForeignKey(User)
    tutorial_resource = models.ForeignKey(TutorialResource)
    created = models.DateTimeField(auto_now_add = True)

class PublishTutorialLog(models.Model):
    user = models.ForeignKey(User)
    tutorial_resource = models.ForeignKey(TutorialResource)
    created = models.DateTimeField(auto_now_add = True)

class NeedImprovementLog(models.Model):
    user = models.ForeignKey(User)
    tutorial_resource = models.ForeignKey(TutorialResource)
    review_state = models.PositiveSmallIntegerField()
    component = models.CharField(max_length = 50)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add = True)

class ContributorNotification(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length = 255)
    message = models.TextField()
    tutorial_resource = models.ForeignKey(TutorialResource)
    created = models.DateTimeField(auto_now_add = True)

class AdminReviewerNotification(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length = 255)
    message = models.TextField()
    tutorial_resource = models.ForeignKey(TutorialResource)
    created = models.DateTimeField(auto_now_add = True)

class DomainReviewerNotification(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length = 255)
    message = models.TextField()
    tutorial_resource = models.ForeignKey(TutorialResource)
    created = models.DateTimeField(auto_now_add = True)

class QualityReviewerNotification(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length = 255)
    message = models.TextField()
    tutorial_resource = models.ForeignKey(TutorialResource)
    created = models.DateTimeField(auto_now_add = True)

