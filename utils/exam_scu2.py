# This module is responsible for assigning proctors to classes based on their availability and teaching assignments.
import streamlit as st
import pandas as pd

class Teacher:
    def __init__(self, name, workload, exempted_main, exempted_joint, preferred_location, special_needs, unavailable_dates):
        self.name = name
        self.workload = workload  # Workload of the teacher
        self.exempted_main = exempted_main # Exempted from being main proctor
        self.exempted_joint = exempted_joint # Exempted from being main proctor
        self.preferred_location = preferred_location  # Preferred location for the exam
        self.special_needs = special_needs
        self.unavailable_dates = set(unavailable_dates)  # Set of unavailable dates
        self.main_proctor_count = 0  # Track main proctor count
        self.joint_proctor_count = 0  # Track joint proctor count across all courses
        self.main_proctor_courses = {}  # Track main proctor courses
        self.joint_proctor_courses = {}  # Track joint proctor courses

    def can_be_proctor(self, date, time):
        if pd.isna(self.exempted_main) is False:
            return False
        elif pd.isna(self.exempted_joint) is False:
            return False
        elif self.joint_proctor_count + self.main_proctor_count >= 3:
            return False
        elif date in self.unavailable_dates:
            return False
        elif '不排早八' in str(self.special_needs) and '08' in str(time):  
            return False
        elif '不排晚上' in str(self.special_needs) and int(time[:2]) >= 18:
            return False
        else:
            return True


class Exam:
    def __init__(self, exam_id, teaching_dept, course, class_id, teachers, exam_date, exam_time, exam_location, proctor_dept, proctor_count):
        self.exam_id = exam_id
        self.teaching_dept = teaching_dept
        self.course = course
        self.class_id = class_id
        self.teachers = teachers
        self.exam_date = exam_date
        self.exam_time = exam_time
        self.exam_location = exam_location
        self.proctor_dept = proctor_dept
        self.proctor_count = proctor_count
        self.main_proctor = None
        self.joint_proctor = None


def assign_proctors(teachers, exams):
    """
    Assign proctors to exam classes based on priority and availability.
    1. For exams with teaching_dept = "SOE", assign available teaching teachers as the main proctor. 
        Add workload to the teachers, do not double count for the same course.
    2. For exams with proctor_dept = "SOE", assign available non-teaching teachers as the joint proctor based on 
        the number of prctors required in proctor_count.
    3. When assigning joint proctors, take into account workload and location preferrance.
    """
    # sort teachers by workload
    teachers.sort(key=lambda t: t.workload)

    # Find available teaching teacher to assign as main proctor for exams with teaching_dept = "SOE"
    for exam in exams:
        if exam.teaching_dept != "经济学院":
            continue

        # Remove teachers who have been assigned as the main proctor for another exam held at the same time or same date at a different location
        teaching_teachers = [t for t in teachers if t.name in exam.teachers]

        for teacher in teaching_teachers:
            for temp_e in [e for e in exams if e.course != exam.course and 
                            e.exam_date == exam.exam_date and 
                            e.exam_time == exam.exam_time]:
                if temp_e.main_proctor == teacher.name:
                    teaching_teachers.remove(teacher)
                    break
            if teacher in teaching_teachers:
                for temp_e in [e for e in exams if e.course != exam.course and 
                               e.exam_date == exam.exam_date and
                               e.exam_location != exam.exam_location]:
                    if temp_e.main_proctor == teacher.name:
                        teaching_teachers.remove(teacher)
                        break

        for teacher in teaching_teachers:
            if pd.isna(teacher.exempted_main) and exam.exam_date not in teacher.unavailable_dates:
                exam.main_proctor = teacher.name
                if exam.course not in teacher.main_proctor_courses:
                    teacher.main_proctor_courses[exam.course] = 1
                    teacher.main_proctor_count += 1
                    teacher.workload += 1
                    break

    
    # Assign joint proctor for exams with proctor_dept = "SOE"
    for exam in exams:
        if exam.proctor_dept != 102 or exam.proctor_count == 0:
            continue

        # find available teachers
        avail_teachers = teachers.copy()

        # remove teachers who have already been assigned as the main proctor or joint proctor for another exam held at the same time or same date at a different location
        for teacher in teachers:

            if teacher.can_be_proctor(exam.exam_date, exam.exam_time) is False:
                avail_teachers.remove(teacher)
                continue

            for temp_exam in [e for e in exams if e.exam_id != exam.exam_id and
                            e.exam_date == exam.exam_date and 
                            e.exam_time == exam.exam_time]:                
                if temp_exam.main_proctor == teacher.name:
                    avail_teachers.remove(teacher)
                    break
                if temp_exam.joint_proctor is not None and \
                    teacher.name in temp_exam.joint_proctor.split(','):
                    # if exam.exam_id == 146:
                    #     st.write(f"Removing {teacher.name} from available teachers for exam {exam.exam_id} due to joint proctor assignment in exam {temp_exam.exam_id}")
                    avail_teachers.remove(teacher)
                    break
                                    

            if teacher in avail_teachers:
                for temp_exam in [e for e in exams if e.exam_id != exam.exam_id and
                                e.exam_date == exam.exam_date and 
                                e.exam_location != exam.exam_location]:
                    if temp_exam.main_proctor == teacher.name:
                        avail_teachers.remove(teacher)
                        break
                    if temp_exam.joint_proctor is not None and \
                        teacher.name in temp_exam.joint_proctor.split(','):
                        avail_teachers.remove(teacher)
                        break

        
        teachers_preferloc = [t for t in avail_teachers if
                            (t.preferred_location == exam.exam_location or pd.isna(t.preferred_location))]
        teachers_other = [t for t in avail_teachers if t not in teachers_preferloc]


        if min(t.workload for t in teachers_preferloc) >= min(t.workload for t in teachers_other) + 2:
            combined_teachers = teachers_other
        else:
            combined_teachers = teachers_preferloc
       
        
        # combined_teachers = sorted(
        #     teaching_teachers + teachers_location + teachers_other,
        #     key=lambda t: (t.workload + (2 if t in teachers_other else 0), t not in teachers_location)
        # )


        while exam.joint_proctor is None or len(exam.joint_proctor.split(',')) < exam.proctor_count:
            for teacher in combined_teachers:                
                if exam.joint_proctor:
                    exam.joint_proctor += f",{teacher.name}"
                else:
                    exam.joint_proctor = teacher.name
                teacher.joint_proctor_count += 1
                teacher.joint_proctor_courses[exam.course] = teacher.joint_proctor_courses.get(exam.course, 0) + 1
                teacher.workload += 1
                if len(exam.joint_proctor.split(',')) >= exam.proctor_count:
                    break
                    
        