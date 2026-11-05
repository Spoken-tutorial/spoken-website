# Third Party Stuff
from django import template
from django.contrib.auth.models import User

# Spoken Tutorial Stuff
from events.models import Test, TestAttendance, TrainingAttendance, FossMdlCourses
from mdldjango.models import *

register = template.Library()

def get_participant_score(key):
    try:
        ta = MdlUser.objects.get(mdluser_id = key)
    except:
        return 'error'
    
    return key

def check_training_enrole(rid, mdluser_id):
    try:
        wa = TrainingAttendance.objects.get(training_id = rid, mdluser_id = mdluser_id)
        return True
    except:
        return False

def check_test_enrole(rid, mdluser_id):
    try:
        wa = TestAttendance.objects.get(test_id = rid, mdluser_id = mdluser_id)
        return True
    except:
        return False

def is_second_attempt(ta):
    if not ta:
        return False
    try:
        if ta.test.training_id:
            ta_list = TestAttendance.objects.filter(test__training_id=ta.test.training_id, mdluser_id=ta.mdluser_id).order_by('id')
        else:
            ta_list = TestAttendance.objects.filter(test_id=ta.test_id, mdluser_id=ta.mdluser_id).order_by('id')
        if ta_list.count() >= 2 and ta_list[1].id == ta.id:
            return True
    except Exception:
        return False
    return False

def get_first_attempt_ta(rid, mdluser_id):
    try:
        test = Test.objects.get(id=rid)
        if test.training_id:
            ta_list = TestAttendance.objects.filter(test__training_id=test.training_id, mdluser_id=mdluser_id).order_by('id')
        else:
            ta_list = TestAttendance.objects.filter(test_id=rid, mdluser_id=mdluser_id).order_by('id')
        return ta_list.first()
    except Exception:
        return None

def calculate_attempt_grade(ta, attempt_index=0):
    if not ta or not ta.mdlquiz_id:
        return None
    
    quiz_id = ta.mdlquiz_id
    mdluser_id = ta.mdluser_id
    sumgrades = None
    quiz_grade = None
    quiz_sumgrades = None
    
    from django.db import connections
    try:
        with connections['moodle'].cursor() as cursor:
            if ta.mdlattempt_id:
                cursor.execute("SELECT sumgrades, quiz FROM mdl_quiz_attempts WHERE id = %s", [ta.mdlattempt_id])
                row = cursor.fetchone()
                if row and row[0] is not None:
                    sumgrades = row[0]
                    quiz_id = row[1]
            
            if sumgrades is None:
                cursor.execute("SELECT sumgrades, quiz FROM mdl_quiz_attempts WHERE quiz = %s AND userid = %s ORDER BY id ASC", [quiz_id, mdluser_id])
                rows = cursor.fetchall()
                if len(rows) > attempt_index and rows[attempt_index][0] is not None:
                    sumgrades = rows[attempt_index][0]
                    quiz_id = rows[attempt_index][1]
                elif len(rows) == 1 and rows[0][0] is not None:
                    sumgrades = rows[0][0]
                    quiz_id = rows[0][1]
            
            cursor.execute("SELECT grade, sumgrades FROM mdl_quiz WHERE id = %s", [quiz_id])
            q_row = cursor.fetchone()
            if q_row:
                quiz_grade = float(q_row[0]) if q_row[0] is not None else 0.0
                quiz_sumgrades = float(q_row[1]) if q_row[1] is not None else 0.0
            
            if sumgrades is not None and quiz_grade is not None and quiz_sumgrades and quiz_sumgrades > 0:
                final_grade = (float(sumgrades) * quiz_grade) / quiz_sumgrades
                return round(final_grade, 2)
            
            cursor.execute("SELECT grade FROM mdl_quiz_grades WHERE quiz = %s AND userid = %s ORDER BY grade DESC", [quiz_id, mdluser_id])
            g_row = cursor.fetchone()
            if g_row and g_row[0] is not None:
                return round(float(g_row[0]), 2)
    except Exception as e:
        return None
    return None

def calculate_first_attempt_grade(first_ta):
    return calculate_attempt_grade(first_ta, attempt_index=0)

def calculate_second_attempt_grade(second_ta):
    return calculate_attempt_grade(second_ta, attempt_index=1)

def get_first_attempt_mark(rid, mdluser_id):
    first_ta = get_first_attempt_ta(rid, mdluser_id)
    if not first_ta:
        return None
    grade = calculate_first_attempt_grade(first_ta)
    if grade is not None:
        return round(grade, 1)
    return None

def get_first_attempt_testid(rid, mdluser_id):
    first_ta = get_first_attempt_ta(rid, mdluser_id)
    if not first_ta:
        return rid
    return first_ta.test_id

def get_participant_mark(rid, mdluser_id):
    try:
        test = Test.objects.get(id=rid)
        ta = TestAttendance.objects.filter(test_id=rid, mdluser_id=mdluser_id).first()
        if ta and is_second_attempt(ta):
            return get_second_attempt_mark(rid, mdluser_id)

        if not ta and test.training_id:
            ta = TestAttendance.objects.filter(test__training_id=test.training_id, mdluser_id=mdluser_id).order_by('id').first()
        elif not ta:
            ta = TestAttendance.objects.filter(test_id=rid, mdluser_id=mdluser_id).first()
        if ta:
            grade = calculate_first_attempt_grade(ta)
            if grade is not None:
                return round(grade, 1)
            if ta.mdlquiz_id:
                mdl = MdlQuizGrades.objects.filter(quiz=ta.mdlquiz_id, userid=mdluser_id).order_by('-grade').first()
                if mdl:
                    return round(mdl.grade, 1)
    except Exception:
        return None
    return None

def get_second_attempt_ta(rid, mdluser_id):
    try:
        test = Test.objects.get(id=rid)
        if test.training_id:
            ta_list = TestAttendance.objects.filter(test__training_id=test.training_id, mdluser_id=mdluser_id).order_by('id')
        else:
            ta_list = TestAttendance.objects.filter(test_id=rid, mdluser_id=mdluser_id).order_by('id')
        if ta_list.count() >= 2:
            return ta_list[1]
        return None
    except Exception:
        return None

def get_second_attempt_status(rid, mdluser_id):
    second_ta = get_second_attempt_ta(rid, mdluser_id)
    if not second_ta:
        return None
    return second_ta.status

def get_second_attempt_courseid(rid, mdluser_id):
    second_ta = get_second_attempt_ta(rid, mdluser_id)
    if not second_ta:
        return None
    return second_ta.mdlcourse_id

def get_second_attempt_testid(rid, mdluser_id):
    second_ta = get_second_attempt_ta(rid, mdluser_id)
    if not second_ta:
        return rid
    return second_ta.test_id

def get_second_attempt_mark(rid, mdluser_id):
    second_ta = get_second_attempt_ta(rid, mdluser_id)
    if not second_ta:
        return None
    grade = calculate_second_attempt_grade(second_ta)
    if grade is not None:
        return round(grade, 1)
    return None

def get_moodle_courseid(rid, mdluser_id):
    #print "rid =>", rid
    #print "mdluser =>", mdluser_id
    #ensure the training.fossmdlmap_id.foss == training.courseMap.foss
    training = Test.objects.get(id=rid).training
    test = Test.objects.get(id=rid)
    if training.fossmdlmap is not None:
        try:
            fmap_foss = training.fossmdlmap.foss_id
            cmap_foss = training.course.foss_id
            if fmap_foss != cmap_foss:
                print(f"\033[91m NOT EQUAL : {fmap_foss}  {cmap_foss}\033[0m")
                # fossmdlmap = FossMdlCourses.objects.filter(foss_id = cmap_foss, level="Advanced", language="English")
                # check if it is C & CPP(43), Moodle (97)
                foss_id = cmap_foss
                if cmap_foss in (43, 97):
                    
                    foss_id = test.foss_id
                fossmdlmap = FossMdlCourses.objects.filter(foss_id = foss_id).first()
                training.fossmdlmap_id = fossmdlmap.id
                training.save()
        except:
            pass
    try:
        wa = TestAttendance.objects.get(test_id = rid, mdluser_id = mdluser_id)
        #print wa.mdlcourse_id
        fossmdlmap_id = wa.test.training.fossmdlmap_id
        if fossmdlmap_id is not None:
            print(f"\033[92m RETURNING \033[0m")
            return FossMdlCourses.objects.get(id=fossmdlmap_id).mdlcourse_id
        print(f"\033[93m Return from try \033[0m")
        return wa.mdlcourse_id
    except Exception as e:
        print(f"\033[91m Exception : {e} \033[0m")
        return False

def get_mdluser_details(mdluser_id):
    try:
        mdluser = MdlUser.objects.get(id=mdluser_id)
        return mdluser
    except:
        return False
    
    
register.filter('get_participant_score', get_participant_score)
register.filter('get_participant_mark', get_participant_mark)
register.filter('get_first_attempt_mark', get_first_attempt_mark)
register.filter('get_first_attempt_testid', get_first_attempt_testid)
register.filter('get_second_attempt_status', get_second_attempt_status)
register.filter('get_second_attempt_courseid', get_second_attempt_courseid)
register.filter('get_second_attempt_testid', get_second_attempt_testid)
register.filter('get_second_attempt_mark', get_second_attempt_mark)
register.filter('check_training_enrole', check_training_enrole)
register.filter('check_test_enrole', check_test_enrole)
register.filter('get_moodle_courseid', get_moodle_courseid)
register.filter('get_mdluser_details', get_mdluser_details)
