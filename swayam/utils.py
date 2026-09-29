import logging
from django.conf import settings
from .models import SwayamUser

logger = logging.getLogger(__name__)


# Check if user is a swayam user
def is_swayam_user(user):
    if not user:
        return False
    is_auth = user.is_authenticated() if callable(user.is_authenticated) else user.is_authenticated
    if not is_auth:
        return False
    return SwayamUser.objects.filter(user=user).exists()


# check if foss category is configured in SWAYAM_FOSS_LIST
def is_swayam_foss(foss):
    swayam_foss_list = getattr(settings, 'SWAYAM_FOSS_LIST', [])
    if not swayam_foss_list:
        return False

    foss_id = getattr(foss, 'id', foss)
    try:
        foss_id_int = int(foss_id)
        return any(int(x) == foss_id_int for x in swayam_foss_list if str(x).isdigit())
    except (ValueError, TypeError):
        foss_name = getattr(foss, 'foss', str(foss))
        return any(str(x).strip().lower() == foss_name.strip().lower() for x in swayam_foss_list)
