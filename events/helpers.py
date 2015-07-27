from datetime import datetime
from django.conf import settings

def get_academic_years(default=settings.ACADEMIC_DURATION):
  current_year = datetime.now().year
  year_choice = [('', '-----')]
  for i in range(current_year - default, current_year + 1):
    year_choice.append((i, i))
  return year_choice
