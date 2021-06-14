from rest_framework.permissions import IsAuthenticatedOrReadOnly
from creation.views import is_domainreviewer, is_qualityreviewer
from creation.models import TutorialDetail, ContributorRole, DomainReviewerRole, QualityReviewerRole

class ScriptOwnerPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user
    tutorialdetails = getFOSS(obj.tutorial)    
    
    if (obj.status): return True

    if (not user.is_anonymous() and (isDomainReviewer(tutorialdetails, obj.language, user) or isQualityReviewer(tutorialdetails, obj.language, user) or isContributor(tutorialdetails, obj.language, user))):
      return True
    
    return False

class ScriptModifyPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user
    tutorialdetails = getFOSS(obj.script.tutorial)
    
    if (user.is_anonymous() or obj.script.status): return False

    return (isDomainReviewer(tutorialdetails, obj.script.language, user) or isQualityReviewer(tutorialdetails, obj.script.language, user) or isContributor(tutorialdetails, obj.script.language, user))
      
class PublishedScriptPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user

    if (user.is_anonymous()): return False

    return is_domainreviewer(user) or is_qualityreviewer(user) or obj.user == user

class ReviewScriptPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user
    tutorialdetails = getFOSS(obj.tutorial)    

    if (user.is_anonymous()): return False

    return isDomainReviewer(tutorialdetails, obj.language, user) or isQualityReviewer(tutorialdetails, obj.language, user)


class CommentOwnerPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = obj.user
    if (user.is_anonymous() or obj.script_details.script.status): return False

    if ('done' in request.data.keys()):
      return is_domainreviewer(user) or is_qualityreviewer(user) or obj.user == user

    return request.user == obj.user

class CanCommentPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    return not obj.script.status

class CanRevisePermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    return not obj.script.status
    
def getFOSS(tutorial):
  tutorialdetails = TutorialDetail.objects.get(tutorial=tutorial)
  return tutorialdetails

def isContributor(foss, language, user):
  if ContributorRole.objects.filter(foss_category=foss.foss, language=language, user=user).exists():
    return True
  return False

def isDomainReviewer(foss, language, user):
  if DomainReviewerRole.objects.filter(foss_category=foss.foss, language=language, user=user).exists():
    return True
  return False

def isQualityReviewer(foss, language, user):
  if QualityReviewerRole.objects.filter(foss_category=foss.foss, language=language, user=user).exists():
    return True
  return False
