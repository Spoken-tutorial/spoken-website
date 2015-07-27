from datetime import datetime
from events.models import TrainingPlanner, Semester
from django.core.exceptions import ObjectDoesNotExist
class CurrentTrainingPlanner():
  def is_even_sem(self, month):
      # 0 => odd sem, 1 => even sem
      if month > 6 and month < 13:
        return 0
      return 1

  def get_year(self, sem, year):
    if sem:
      return year - 1
    return year

  def get_semester(self, sem):
    return Semester.objects.get(even=sem)

  def get_current_planner(self, user, sem=None):
    now = datetime.now()
    if sem == None:
      sem = self.is_even_sem(now.month)
    year = self.get_year(int(sem), now.year)
    try:
      return TrainingPlanner.objects.get(year=year, semester__even=sem, \
        academic=user.organiser.academic, organiser=user.organiser)
    except ObjectDoesNotExist:
      return TrainingPlanner.objects.create(year=year, \
        semester=self.get_semester(sem), academic=user.organiser.academic,\
          organiser=user.organiser)
    except Exception, e:
      print e
    return False
