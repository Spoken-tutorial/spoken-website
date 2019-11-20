from rest_framework.permissions import IsAuthenticatedOrReadOnly
from creation.views import is_domainreviewer, is_qualityreviewer

class ScriptOwnerPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user
    
    if (obj.status): return True

    if (not user.is_anonymous() and (is_domainreviewer(user) or is_qualityreviewer(user) or obj.user == user)):
      return True
    
    return False

class ScriptModifyPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user
    
    if (user.is_anonymous() or obj.script.status): return False

    return obj.script.user == user
      
class PublishedScriptPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user

    if (user.is_anonymous()): return False

    return is_domainreviewer(user) or is_qualityreviewer(user) or obj.user == user

class ReviewScriptPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user

    if (user.is_anonymous()): return False

    return is_domainreviewer(user) or is_qualityreviewer(user)


class CommentOwnnerPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = obj.user
    if (user.is_anonymous()): return False

    if ('done' in request.data.keys()):
      return is_domainreviewer(user) or is_qualityreviewer(user) or obj.user == user

    return request.user == obj.user
