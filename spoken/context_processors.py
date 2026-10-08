from spoken.config import PROCESS_URL, SPOKEN_BASE_URL, SCRIPT_URL, FORUMS_SPOKEN_URL


def spoken_urls(request):
    return {
        'PROCESS_URL': PROCESS_URL,
        'SPOKEN_BASE_URL': SPOKEN_BASE_URL,
        'SCRIPT_URL': SCRIPT_URL,
        'FORUMS_SPOKEN_URL': FORUMS_SPOKEN_URL,
    }