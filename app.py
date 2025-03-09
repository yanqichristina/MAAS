
#!/usr/bin/env python

import streamlit as st
import pandas as pd
from utils.matching_algorithm import deferred_acceptance
from utils.translations import translations
from utils.models import Student, School

# class Student:
#     def __init__(self, name, gpa, preferences):
#         self.name = name
#         self.gpa = gpa
#         self.preferences = [pref.strip() for pref in preferences]   # Ordered list of preferred schools
#         self.current_proposal = 0  # Index of the next school to propose

#     def propose(self):
#         if self.current_proposal < len(self.preferences):
#             school = self.preferences[self.current_proposal]
#             self.current_proposal += 1
#             return school
#         return None  # No more schools to propose

# class School:
#     def __init__(self, name, quota):
#         self.name = name
#         self.quota = quota
#         self.accepted_students = []  # List of (gpa, student_name)
    
#     def consider(self, student):
#         self.accepted_students.append((student.gpa, student.name))
#         self.accepted_students.sort(reverse=True, key=lambda x: x[0])  # Sort by GPA
#         if len(self.accepted_students) > self.quota:
#             return self.accepted_students.pop()  # Remove lowest-ranked student
#         return None


@st.cache_data
def load_sample():
    studentSample = pd.read_csv("data/student_sample.csv")
    schoolSample = pd.read_csv("data/school_sample.csv")
    return studentSample, schoolSample

def main():
    st.sidebar.title("Settings")
    lang = st.sidebar.selectbox("Select Language / 选择语言", ["English", "中文"])
    if lang == "English":
        lang_code = "en"
    elif lang == "中文":
        lang_code = "zh"

    st.title(translations[lang_code]["title"])
    studentSample, schoolSample = load_sample()
    
    # st.header("Upload Student Data")
    # student_file = st.file_uploader("Upload CSV file with student data (name, GPA, preferences as comma-separated values)", type=["csv"])
    st.header(translations[lang_code]["upload_student"])
    student_file = st.file_uploader(translations[lang_code]["upload_student"], type=["csv"])

    if student_file is None:
        st.write(translations[lang_code]["Example:"])
        st.write(studentSample)

    # st.header("Upload School Data")
    # school_file = st.file_uploader("Upload CSV file with school data (name, quota)", type=["csv"])
    st.header(translations[lang_code]["upload_school"])
    school_file = st.file_uploader(translations[lang_code]["upload_school"], type=["csv"])

    if school_file is None:
        st.write(translations[lang_code]["Example:"])
        st.write(schoolSample)
    
    if st.button(translations[lang_code]["run_matching"]):
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
            
            st.success(translations[lang_code]["success_message"])
            student_csv = student_assignments_df.to_csv(index=False).encode("utf-8")
            school_csv = school_enrollments_df.to_csv(index=False).encode("utf-8")

            st.write(translations[lang_code]["student_preview:"])
            st.write(student_assignments_df)
            st.download_button(translations[lang_code]["download_students"], student_csv, "student_assignments.csv", "text/csv")
            st.write(translations[lang_code]["school_preview:"])
            st.write(school_enrollments_df)
            st.download_button(translations[lang_code]["download_schools"], school_csv, "school_enrollments.csv", "text/csv")  
                   
        else:
            st.error(translations[lang_code]["error_message"])

if __name__ == "__main__":
    main()

