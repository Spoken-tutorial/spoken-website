from rest_framework.permissions import IsAuthenticatedOrReadOnly
from creation.views import is_domainreviewer, is_qualityreviewer

class ViewScriptPermission(IsAuthenticatedOrReadOnly):
  def has_object_permission(self, request, view, obj):
    user = request.user
    
    if (obj.status): return True

    if (not user.is_anonymous() and (is_domainreviewer(user) or is_qualityreviewer(user) or obj.user == user)):
      return True
    
    return False