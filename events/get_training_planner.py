from __future__ import print_function
# Standard Library
from builtins import object
import datetime as dt

# Third Party Stuff
from django.core.exceptions import ObjectDoesNotExist

# Spoken Tutorial Stuff
from events.models import Semester, TrainingPlanner


class CurrentTrainingPlanner(object):

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
        now = dt.datetime.now()
        if sem is None:
            sem = self.is_even_sem(now.month)
        year = self.get_year(int(sem), now.year)
        try:
            return TrainingPlanner.objects.get(year=year, semester__even=sem,
                                               academic=user.organiser.academic, organiser=user.organiser)
        except ObjectDoesNotExist:
            return TrainingPlanner.objects.create(year=year,
                                                  semester=self.get_semester(sem), academic=user.organiser.academic,
                                                  organiser=user.organiser)
        except Exception as e:
            print(e)
        return False
