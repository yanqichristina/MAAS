# This module is responsible for assigning proctors to classes based on their availability and teaching assignments.
import streamlit as st
import pandas as pd

class Teacher:
    def __init__(self, name, workload, preferred_location, unavailable_dates):
        self.name = name
        self.workload = workload  # Workload of the teacher
        self.preferred_location = preferred_location  # Preferred location for the exam
        self.unavailable_dates = set(unavailable_dates)  # Set of unavailable dates
        self.main_proctor_count = 0  # Track main proctor count
        self.joint_proctor_count = 0  # Track joint proctor count across all courses
        self.main_proctor_courses = {}  # Track main proctor courses
        self.joint_proctor_courses = {}  # Track joint proctor courses

    def is_available(self, date):
        return date not in self.unavailable_dates

    def can_be_proctor(self):
        return self.joint_proctor_count + self.main_proctor_count < 3


class Class:
    def __init__(self, course, class_id, teachers, stu_count, exam_date, exam_time, exam_location):
        self.course = course
        self.class_id = class_id
        self.teachers = teachers
        self.stu_count = stu_count
        self.exam_date = exam_date
        self.exam_time = exam_time
        self.exam_location = exam_location
        self.exam_id = None
        self.main_proctor = None
        self.joint_proctor = None


def assign_proctors(teachers, classes):
    """
    Assign proctors to exam classes based on priority and availability.
    1. Assign the same exam_id to classes of the same course that are taught by the same teacher 
        if the combined student count is less than 100.
    2. Assign the same exam_id to classes of the same course that are taught by different teachers 
        if the combined student count is less than 100.
    3. Assign main proctor - teachers teaching the class have the highest priority to be the main proctor.
    4. Assign joint proctor - for exam with stu_count less than 30, no joint proctor is needed; for stu_count less than 80, 1 joint proctor is needed; 
        otherwise, 2 joint proctors are needed.
    5. When assigning joint proctor, balance workload across teachers.
    """
    # Assign exam_id to classes
    for cls in classes:
        if cls.exam_id is not None:
            continue

        if cls.stu_count >= 100:
            cls.exam_id = cls.course + "_" + str(cls.class_id) + "_" + cls.exam_location
            continue
        else:
            # Extract all classes with the same course and teachers
            teach_cls = [c for c in classes if c.course == cls.course and c.teachers == cls.teachers and c.exam_location == cls.exam_location]
            if len(teach_cls) > 1:
                teach_cls.sort(key=lambda c: c.stu_count, reverse=True)
                groups = []
                while teach_cls:
                    group = []
                    group_stu_count = 0
                    for c in teach_cls[:]:
                        if group_stu_count + c.stu_count <= 100:
                            group.append(c)
                            group_stu_count += c.stu_count
                            teach_cls.remove(c)
                    groups.append(group)
                
                for i, group in enumerate(groups):
                    exam_id = cls.course + "_" + "_".join(str(c.class_id) for c in group) + "_" + cls.exam_location
                    for c in group:
                        c.exam_id = exam_id
            else:
                cls.exam_id = cls.course + "_" + str(cls.class_id) + "_" + cls.exam_location

            
    # Assign main and joint proctors for each exam class
    # Group classes by exam_id
    exams = {}
    for cls in classes:
        if cls.exam_id not in exams:
            exams[cls.exam_id] = []
        exams[cls.exam_id].append(cls)

    # Find available teaching teacher to assign as main proctor for each exam_id
    for exam_id, exam_classes in exams.items():
        if any(cls.main_proctor for cls in exam_classes):
            continue

        # Find available teaching teachers
        exam_date = exam_classes[0].exam_date
        exam_time = exam_classes[0].exam_time
        exam_location = exam_classes[0].exam_location
        teaching_teachers = set()
        for cls in exam_classes:
            teaching_teachers.update(cls.teachers)
        teaching_teachers = [t for t in teachers if t.name in teaching_teachers]

        # Remove teachers who have already been assigned as the main proctor for another exam held at the same time or same date at a different location
        for teacher in teaching_teachers:
            for cls in [c for c in classes if c not in exam_classes and 
                        c.exam_date == exam_classes[0].exam_date and 
                        c.exam_time == exam_classes[0].exam_time]:
                if cls.main_proctor == teacher.name:
                    teaching_teachers.remove(teacher)
                    break
            if teacher in teaching_teachers:
                for cls in [c for c in classes if c not in exam_classes and
                            c.exam_date == exam_classes[0].exam_date and 
                            c.exam_location != exam_classes[0].exam_location]:
                    if cls.main_proctor == teacher.name:
                        teaching_teachers.remove(teacher)
                        break

        for teacher in teaching_teachers:
            if exam_date not in teacher.unavailable_dates:
                for cls in exam_classes:
                    cls.main_proctor = teacher.name
                teacher.main_proctor_count += 1
                teacher.main_proctor_courses[cls.course] = teacher.main_proctor_courses.get(cls.course, 0) + 1
                teacher.workload += 1
                break

    # Assign non-teaching teachers as main proctor if teaching teachers are not available
    for exam_id, exam_classes in exams.items():
        if any(cls.main_proctor for cls in exam_classes):
            continue

        # Find available non-teaching teachers
        exam_date = exam_classes[0].exam_date
        exam_location = exam_classes[0].exam_location

        teaching_teachers = set()
        for cls in exam_classes:
            teaching_teachers.update(cls.teachers)
        teaching_teachers = [t for t in teachers if t.name in teaching_teachers]
        other_teachers = [t for t in teachers if t not in teaching_teachers and
                          (t.preferred_location == exam_location or pd.isna(t.preferred_location)) and
                          t.can_be_proctor()]
        
        other_teachers.sort(key=lambda t: t.workload)
        # other_teachers_df = pd.DataFrame([{
        #     "Name": teacher.name,
        #     "Workload": teacher.workload,
        #     "Preferred Location": teacher.preferred_location,
        #     "Unavailable Dates": list(teacher.unavailable_dates),
        #     "Main Proctor Count": teacher.main_proctor_count,
        #     "Joint Proctor Count": teacher.joint_proctor_count
        # } for teacher in other_teachers])
        # st.write(other_teachers_df)

        # Assign main proctor
        for teacher in other_teachers:
            if all(cls.exam_date not in teacher.unavailable_dates for cls in exam_classes):
                for cls in exam_classes:
                    cls.main_proctor = teacher.name
                teacher.main_proctor_count += 1
                teacher.main_proctor_courses[cls.course] = teacher.main_proctor_courses.get(cls.course, 0) + 1
                teacher.workload += 1
                break

    
    # Assign joint proctor for each exam_id
    for exam_id, exam_classes in exams.items():
        # Assign joint proctor if needed
        total_students = sum(cls.stu_count for cls in exam_classes)
        if total_students <= 30:
            continue
        else:
            exam_date = exam_classes[0].exam_date
            exam_location = exam_classes[0].exam_location
            # find available teachers
            teaching_teachers = set()
            for cls in exam_classes:
                teaching_teachers.update(cls.teachers)
            teaching_teachers = [t for t in teachers if t.name in teaching_teachers]
            other_teachers = [t for t in teachers if t not in teaching_teachers and 
                              (t.preferred_location == exam_location or pd.isna(t.preferred_location)) and
                              t.can_be_proctor()]
            
            # remove teachers who have already been assigned as the main proctor or joint proctor for another exam held at the same time or same date at a different location
            for teacher in teaching_teachers + other_teachers:
                for cls in [c for c in classes if c.exam_date == exam_classes[0].exam_date and c.exam_time == exam_classes[0].exam_time]:
                    if teacher.main_proctor_courses.get(cls.course,0) > 0 or teacher.joint_proctor_courses.get(cls.course,0) > 0:
                        if teacher in teaching_teachers:
                            teaching_teachers.remove(teacher)
                        else:
                            other_teachers.remove(teacher)
                        break
                if teacher in teaching_teachers or teacher in other_teachers:
                    for cls in [c for c in classes if c.exam_date == exam_classes[0].exam_date and c.exam_location != exam_classes[0].exam_location]:
                        if teacher.main_proctor_courses.get(cls.course,0) > 0 or teacher.joint_proctor_courses.get(cls.course,0) > 0:
                            if teacher in teaching_teachers:
                                teaching_teachers.remove(teacher)
                            elif teacher in other_teachers:
                                other_teachers.remove(teacher)
                            break
            # Sort teachers by workload
            other_teachers.sort(key=lambda t: t.workload)


            # Assign joint proctor based on student count
            if total_students > 30 and total_students <= 80:
                for group in [teaching_teachers, other_teachers]:
                    for teacher in group:
                        if exam_date not in teacher.unavailable_dates:
                            for cls in exam_classes:
                                cls.joint_proctor = teacher.name
                            teacher.joint_proctor_count += 1
                            teacher.joint_proctor_courses[cls.course] = teacher.joint_proctor_courses.get(cls.course, 0) + 1
                            teacher.workload += 1
                            break
                    if any(cls.joint_proctor for cls in exam_classes):
                        break
            elif total_students > 80:
                joint_proctors_assigned = 0
                for group in [teaching_teachers, other_teachers]:
                    for teacher in group:
                        if joint_proctors_assigned >= 2:
                            break
                        if exam_date not in teacher.unavailable_dates:
                            for cls in exam_classes:
                                if not cls.joint_proctor:
                                    cls.joint_proctor = teacher.name
                                else:
                                    cls.joint_proctor += f", {teacher.name}"
                            teacher.joint_proctor_count += 1
                            teacher.joint_proctor_courses[cls.course] = teacher.joint_proctor_courses.get(cls.course, 0) + 1
                            teacher.workload += 1
                            joint_proctors_assigned += 1
                    if joint_proctors_assigned >= 2:
                        break

        