from datetime import datetime
from django.conf import settings

def get_academic_years(default=settings.ACADEMIC_DURATION):
  current_year = datetime.now().year
  year_choice = [('', '-----')]
  for i in range(current_year - default, current_year + 1):
    year_choice.append((i, i))
  return year_choice
  
def get_prev_semester_duration(semester_type, year):
    if semester_type.lower() == 'even':
        return datetime.strptime(str(year)+'-01-01', '%Y-%m-%d').date(), datetime.strptime(str(year)+'-06-30', '%Y-%m-%d').date()
    if semester_type.lower() == 'odd':
        return datetime.strptime(str(year)+'-07-01', '%Y-%m-%d').date(), datetime.strptime(str(year)+'-12-31', '%Y-%m-%d').date()
    raise Exception("Invalid semester type, it must be either odd or even")
