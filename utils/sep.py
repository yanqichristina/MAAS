import streamlit as st

class Student:
    def __init__(self, name, gpa, preferences):
        self.name = name
        self.gpa = gpa
        self.preferences = [pref.strip() for pref in preferences]  # Ordered list of preferred schools
        self.current_proposal = 0  # Index of the next school to propose

    def propose(self):
        if self.current_proposal < len(self.preferences):
            school = self.preferences[self.current_proposal]
            self.current_proposal += 1
            return school
        return None  # No more schools to propose


class School:
    def __init__(self, name, quota):
        self.name = name
        self.quota = quota
        self.accepted_students = []  # List of (gpa, student_name)
    
    def consider(self, student):
        self.accepted_students.append((student.gpa, student.name))
        self.accepted_students.sort(reverse=True, key=lambda x: x[0])  # Sort by GPA
        if len(self.accepted_students) > self.quota:
            return self.accepted_students.pop()  # Remove lowest-ranked student
        return None

def deferred_acceptance(students, schools):
    unmatched_students = list(students.values())

    # Create a placeholder to collect all the text output
    output_text = []
    def st_write_wrapper(text):
        nonlocal output_text
        st.write(text)
        output_text.append(str(text))
    
    with st.expander("See detailed matching process"):
        with st.container(height=300, border=False):
            # st.write("Deferred Acceptance Algorithm:")
            st.divider()
            
            while len(unmatched_students)>0:
                student = unmatched_students.pop(0)
                school_name = student.propose()
                if school_name is not None:
                    st_write_wrapper(f"{student.name} propose to Choice {student.current_proposal} -- {school_name}")
                    # st.write(f"{student.name} propose to Choice {student.current_proposal} -- {school_name}")
                    removed_student = schools[school_name].consider(student)
                    if removed_student:
                        st_write_wrapper(f":blue[{removed_student[1]} is rejected from {school_name}]")
                        # st.write(f":blue[{removed_student[1]} is rejected from {school_name}]")
                        unmatched_students.append(students[removed_student[1]])
    
    student_assignments = {s.name: None for s in students.values()}
    school_enrollments = {school.name: [] for school in schools.values()}
    
    for school in schools.values():
        for gpa, student_name in school.accepted_students:
            student_assignments[student_name] = school.name
            school_enrollments[school.name].append(student_name)
    
    return student_assignments, school_enrollments, output_text