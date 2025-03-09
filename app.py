
#!/usr/bin/env python

import streamlit as st
import pandas as pd
# from collections import defaultdict

class Student:
    def __init__(self, name, gpa, preferences):
        self.name = name
        self.gpa = gpa
        self.preferences = [pref.strip() for pref in preferences]   # Ordered list of preferred schools
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
    
    while unmatched_students:
        student = unmatched_students.pop(0)
        school_name = student.propose()
        if school_name is not None:
            removed_student = schools[school_name].consider(student)
            if removed_student:
                unmatched_students.append(students[removed_student[1]])
    
    student_assignments = {s.name: None for s in students.values()}
    school_enrollments = {school.name: [] for school in schools.values()}
    
    for school in schools.values():
        for gpa, student_name in school.accepted_students:
            student_assignments[student_name] = school.name
            school_enrollments[school.name].append(student_name)
    
    return student_assignments, school_enrollments

# @st.cache_data
# def load_sample():
#     studentSample = pd.read_csv("samples/student_sample.csv")
#     schoolSample = pd.read_csv("samples/school_sample.csv")
#     return studentSample, schoolSample

def main():
    st.title("Student-School Matching for Exchange Programs")
    # studentSample, schoolSample = load_sample()
    
    st.header("Upload Student Data")
    student_file = st.file_uploader("Upload CSV file with student data (name, GPA, preferences as comma-separated values)", type=["csv"])
    if student_file is None:
        st.write("Example:")
        # st.write(studentSample)

    st.header("Upload School Data")
    school_file = st.file_uploader("Upload CSV file with school data (name, quota)", type=["csv"])
    if school_file is None:
        st.write("Example:")
        # st.write(schoolSample)
    
    if st.button("Run Matching"):
        if student_file and school_file:
            students_df = pd.read_csv(student_file)
            schools_df = pd.read_csv(school_file)
            
            students = {}
            for _, row in students_df.iterrows():
                preferences = row["preferences"].split(",")
                students[row["name"]] = Student(row["name"], row["GPA"], preferences)
            
            schools = {row["name"]: School(row["name"], int(row["quota"])) for _, row in schools_df.iterrows()}
            
            student_assignments, school_enrollments = deferred_acceptance(students, schools)
            
            student_assignments_df = pd.DataFrame(list(student_assignments.items()), columns=["Student", "Assigned School"])
            school_enrollments_df = pd.DataFrame([(school, student) for school, students in school_enrollments.items() for student in students], columns=["School", "Enrolled Student"])
            
            st.success("Matching completed!")
            student_csv = student_assignments_df.to_csv(index=False).encode("utf-8")
            school_csv = school_enrollments_df.to_csv(index=False).encode("utf-8")

            st.write("Student Assignments Preview:")
            st.write(student_assignments_df)
            st.download_button("Download Student Assignments", student_csv, "student_assignments.csv", "text/csv")
            st.write("School Enrollments Preview:")
            st.write(school_enrollments_df)
            st.download_button("Download School Enrollments", school_csv, "school_enrollments.csv", "text/csv")            
                   
        else:
            st.error("Please upload both student and school data files.")

if __name__ == "__main__":
    main()

