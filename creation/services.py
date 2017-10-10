# Spoken Tutorial Stuff
from creation.models import BrochureDocument, BrochurePage


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
