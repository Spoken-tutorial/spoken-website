from creation.models import TutorialResource, Language

LANGUAGES = Language.objects.all()
LANGUAGES_IDS = LANGUAGES.values_list('id', flat=True)


def check_english_timed_script_available(td):
    return TutorialResource.objects.filter(script_status=4, language_id=22, tutorial_detail=td).exists()


def get_available_languages(tutorial):
    ''' Returns set of languages id to do'''
    languages_done = TutorialResource.objects.filter(
        tutorial_detail=tutorial).values_list('language', flat=True)
    languages_available_ids = set(LANGUAGES_IDS) - set(languages_done)
    return LANGUAGES.filter(id__in=languages_available_ids)
