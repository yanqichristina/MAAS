# This module is responsible for assigning proctors to classes based on their availability and teaching assignments.

class Teacher:
    def __init__(self, name, unavailable_dates):
        self.name = name
        self.unavailable_dates = set(unavailable_dates)  # Set of unavailable dates
        self.main_proctor_count = 0  # Track main proctor count
        self.joint_proctor_count = 0  # Track joint proctor count across all courses
        self.main_proctor_courses = {}  # Track main proctor courses
        self.joint_proctor_courses = {}  # Track joint proctor courses

    def is_available(self, date):
        return date not in self.unavailable_dates

    def can_be_main_proctor(self, course):
        # Check if the teacher can be the main proctor for the given course
        return (
            self.main_proctor_count == 0 or 
            ((course in self.main_proctor_courses.keys() and self.main_proctor_count < 3 ))
        )

    def can_be_joint_proctor(self):
        return self.joint_proctor_count < 2


class Class:
    def __init__(self, course, class_id, teachers, exam_date):
        self.course = course
        self.class_id = class_id
        self.teachers = teachers
        self.exam_date = exam_date
        self.main_proctor = None
        self.joint_proctor = None


def assign_proctors(teachers, classes):
    """
    Assign proctors to classes based on priority and availability.
    Priority:
    1. Teachers teaching the class have the highest priority to be the main proctor.
    """

    for cls in classes:
        # Filter teachers teaching the class
        teaching_class = [t for t in teachers if t.name in cls.get('teachers', [])]
        other_teachers = [t for t in teachers if t not in teaching_class]
        other_teachers.sort(key=lambda t: t.joint_proctor_count)

        # Assign main proctor
        if cls['main_proctor_faculty'] == '经济学院':
            for group in [teaching_class, other_teachers]:
                for teacher in group:
                    if cls['exam_date'] not in teacher.unavailable_dates and teacher.can_be_main_proctor(cls['course']):
                        cls['main_proctor'] = teacher.name
                        teacher.main_proctor_courses[cls['course']] = teacher.main_proctor_courses.get(cls['course'], 0) + 1
                        teacher.main_proctor_count += 1
                        if teacher in other_teachers:
                            other_teachers.remove(teacher)  # Remove from other teachers list
                        break
                if cls.get('main_proctor'):
                    break

        # Assign joint proctor
        if cls['joint_proctor_faculty'] == '经济学院':
            for group in [other_teachers]:
                for teacher in group:
                    if cls['exam_date'] not in teacher.unavailable_dates and teacher.can_be_joint_proctor():
                        cls['joint_proctor'] = teacher.name
                        teacher.joint_proctor_count += 1
                        teacher.joint_proctor_courses[cls['course']] = teacher.joint_proctor_courses.get(cls['course'], 0) + 1
                        break
                if cls.get('joint_proctor'):
                    break

        