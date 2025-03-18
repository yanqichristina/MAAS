import streamlit as st

class Teacher:
    def __init__(self, name, lang, required_classes, preferred_courses):
        self.name = name
        self.lang = lang
        self.required_classes = required_classes  # Number of classes they need to teach
        self.preferred_courses = preferred_courses  # Courses they are willing to teach
        self.assigned_classes = 0  # Tracks how many classes assigned

    # def can_teach(self, course):
    #     return course in self.preferred_courses

class Course:
    def __init__(self, name, required_classes):
        self.name = name
        self.required_classes = required_classes  # Total classes that need teachers
        self.assigned_teachers = []  # List of (teacher_name, lang, num_classes)

def teacher_course_matching(teachers, courses):
    """
    Matches teachers to courses ensuring all courses are covered and 
    teachers meet their required workload.
    """
    teacher_list = sorted(teachers.values(), key=lambda t: len(t.preferred_courses))  # Prioritize by fewer courses they can teach

    for teacher in teacher_list:
        for course in teacher.preferred_courses:
            if teacher.assigned_classes >= teacher.required_classes:
                break  # Stop assigning if teacher workload is met
            if course in courses and courses[course].required_classes > 0:
                assigned_classes = min(
                    teacher.required_classes - teacher.assigned_classes, 
                    courses[course].required_classes
                )
                courses[course].assigned_teachers.append((teacher.name, teacher.lang, assigned_classes))
                teacher.assigned_classes += assigned_classes
                courses[course].required_classes -= assigned_classes

    # Generate initial results
    teacher_assignments = {t.name: [] for t in teachers.values()}
    course_assignments = {c.name: [] for c in courses.values()}

    for course_name, course in courses.items():
        for teacher_name, teaching_lang, num_classes in course.assigned_teachers:
            teacher_assignments[teacher_name].append((course_name, teaching_lang, num_classes))
            course_assignments[course_name].append((teacher_name, teaching_lang, num_classes))

    
    # # Reassign teachers to unassigned courses
    for course_name, course in courses.items():
        if course.assigned_teachers==[]:
            # st.write(course_name)
            for teacher in teacher_list:
                if course.assigned_teachers!=[]:
                    break
                if course_name in teacher.preferred_courses:
                    # st.write(teacher.name)
                    for assigned_course_name, _, num_classes in teacher_assignments[teacher.name]:
                        # st.write(assigned_course_name, num_classes)
                        if num_classes > 1 or len(courses[assigned_course_name].assigned_teachers) > 1:
                            # st.write(assigned_course_name)
                            # Move one class from assigned course to the unassigned course
                            teacher_assignments[teacher.name].remove((assigned_course_name, teacher.lang, num_classes))
                            if num_classes > 1:
                                teacher_assignments[teacher.name].append((assigned_course_name, teacher.lang, num_classes - 1))
                            teacher_assignments[teacher.name].append((course_name, teacher.lang, 1))
                            courses[assigned_course_name].assigned_teachers.remove((teacher.name, teacher.lang, num_classes))
                            if num_classes > 1:
                                courses[assigned_course_name].assigned_teachers.append((teacher.name, teacher.lang, num_classes - 1))
                            courses[course_name].assigned_teachers.append((teacher.name, teacher.lang, 1))
                            courses[assigned_course_name].required_classes += 1
                            courses[course_name].required_classes -= 1
                            course_assignments[course_name].append((teacher.name, teacher.lang, 1))
                            course_assignments[assigned_course_name].remove((teacher.name, teacher.lang, num_classes))
                            if num_classes > 1:
                                course_assignments[assigned_course_name].append((teacher.name, teacher.lang, num_classes - 1))
                            break
               

    return teacher_assignments, course_assignments