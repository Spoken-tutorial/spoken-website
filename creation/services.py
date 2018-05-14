# Spoken Tutorial Stuff
from creation.models import BrochureDocument, BrochurePage, RoleRequest,Language


def get_data_for_brochure_display():
    brochures = BrochureDocument.objects.all()
    data_dict = {}
    for brochure in brochures:
        categories = brochure.foss_course.category.all()
        for category in categories:
            pages = BrochurePage.objects.filter(brochure_id=brochure.id)
            for page in pages:
                category_data = data_dict.get(category, None)
                if category_data is None:
                    data_dict[category] = []
                data_dict[category].append({"foss_name": brochure.foss_course, "cover_image": page.page.url})

    return data_dict


def get_revokable_languages_for_role(user,role_type):
    roles = {
    'contributor': 0,
    'external-contributor': 1,
    'video-reviewer': 2,
    'domain-reviewer': 3,
    'quality-reviewer': 4,
    }
    set_languages = RoleRequest.objects.filter(user=user, status=1, role_type = roles[role_type]).values('language')
    languages = Language.objects.filter(id__in = set_languages).values('name','id')
    return languages
