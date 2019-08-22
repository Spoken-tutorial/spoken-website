# Spoken Tutorial Stuff
from creation.models import BrochureDocument, BrochurePage, FossCategory, FossSuperCategory
import collections

def get_data_for_brochure_display():
    # my code starts here
    categories = FossSuperCategory.objects.order_by('name')
    data_dict = collections.OrderedDict()

    for category in categories:
        fosses = FossCategory.objects.filter(category=category.id)
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
