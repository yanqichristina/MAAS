import streamlit as st
import pandas as pd

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
    def __init__(self, name, quota, minGPA):
        self.name = name
        self.quota = quota
        self.minGPA = minGPA
        self.accepted_students = []  # List of (gpa, student_name)
    
    def consider(self, student):
        if student.gpa < self.minGPA:
            rejected_reason = f"minimum GPA {self.minGPA} not met"
            return (student.gpa, student.name), rejected_reason  # Student does not meet GPA requirement
        self.accepted_students.append((student.gpa, student.name))
        self.accepted_students.sort(reverse=True, key=lambda x: x[0])  # Sort by GPA
        if len(self.accepted_students) > self.quota:
            rejected_reason = f"maximum quota reached. Accepted students: {[(name, gpa) for gpa, name in self.accepted_students[:-1]]}"
            return self.accepted_students.pop(), rejected_reason  # Remove lowest-ranked student
        return None, None  # No student removed

def deferred_acceptance(students, schools):
    unmatched_students = list(students.values())

    # Create a DataFrame to record the matching process
    columns = ['Student Name', 'GPA', 'Action', 'Choice Number', 'School Name', 'Reason']
    matching_process_df = pd.DataFrame(columns=columns)

    with st.expander("See detailed matching process"):
        with st.container(height=300, border=False):
            # st.write("Deferred Acceptance Algorithm:")
            st.divider()
            
            while len(unmatched_students)>0:
                student = unmatched_students.pop(0)
                school_name = student.propose()
                if school_name is not None:
                    # Record the proposal action
                    new_row = {
                        'Student Name': student.name,
                        'GPA': student.gpa,
                        'Action': 'proposed to',
                        'Choice Number': student.current_proposal,
                        'School Name': school_name,
                        'Reason': None
                    }
                    matching_process_df = pd.concat([matching_process_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.write(f"{student.name} propose to Choice {student.current_proposal} -- {school_name}")
                    
                    removed_student, rejected_reason = schools[school_name].consider(student)
                    if removed_student:
                        # Record the rejection action     
                        new_row = {
                            'Student Name': removed_student[1],
                            'GPA': removed_student[0],
                            'Action': 'rejected by',
                            'Choice Number': students[removed_student[1]].preferences.index(school_name) + 1,
                            'School Name': school_name,
                            'Reason': rejected_reason
                        }
                        matching_process_df = pd.concat([matching_process_df, pd.DataFrame([new_row])], ignore_index=True)
                        st.write(f"{removed_student[1]} (GPA:{removed_student[0]}) is rejected by {school_name} because {rejected_reason}")
                        unmatched_students.append(students[removed_student[1]])
    
    student_assignments = {s.name: None for s in students.values()}
    school_enrollments = {school.name: [] for school in schools.values()}
    
    for school in schools.values():
        for gpa, student_name in school.accepted_students:
            student_assignments[student_name] = school.name
            school_enrollments[school.name].append(student_name)
    
    return student_assignments, school_enrollments, matching_process_df