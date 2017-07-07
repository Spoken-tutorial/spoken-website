from creation.models import BrochureDocument


def get_data_for_brochure_display():
    brochures = BrochureDocument.objects.all()
    data_dict = {}
    for brochure in brochures:
        categories = brochure.foss_course.category.all()
        for category in categories:
            foss = brochure.foss_course.foss
            file = brochure.document.url
            category_data = data_dict.get(category, None)
            # check if category key in the dictionary exists
            if category_data is None:
                data_dict[category] = []
            data_dict[category].append({"foss_name": foss, "cover_image": file})
            data_dict[category].sort()

    return data_dict
