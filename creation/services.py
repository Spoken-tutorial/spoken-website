# Spoken Tutorial Stuff
from creation.models import BrochureDocument, \
BrochurePage, RoleRequest, Language
from creation.models import BrochureDocument, BrochurePage, FossCategory, FossSuperCategory
import collections

def get_data_for_brochure_display():
    # my code starts here
    categories = FossSuperCategory.objects.order_by('name')
    data_dict = collections.OrderedDict()

    for category in categories:
        fosses = FossCategory.objects.filter(category=category.id, show_on_homepage__lt=2)
        for foss in fosses:
            brochuredocs = BrochureDocument.objects.filter(foss_course=foss.id)
            if brochuredocs:
                category_data = data_dict.get(category, None)
                if category_data is None:
                    data_dict[category] = []
                for brochure in brochuredocs:
                    pages = BrochurePage.objects.filter(brochure_id=brochure.id)
                    for page in pages:
                        data_dict[category].append({"foss_name": brochure.foss_course, "cover_image": page.page.url})
    return data_dict


def get_revokable_languages_for_role(user, role_type):
    roles = {
        'contributor': 0,
        'external-contributor': 1,
        'video-reviewer': 2,
        'domain-reviewer': 3,
        'quality-reviewer': 4,
    }
    contrib_languages = RoleRequest.objects.filter(user=user, status=1,
                                                   role_type=roles[role_type]).values('language')
    languages = \
        Language.objects.filter(id__in=contrib_languages).values('name', 'id')
    return languages
