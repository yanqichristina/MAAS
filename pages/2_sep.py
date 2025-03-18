# Description: This file contains the code for the Streamlit app that runs the Student-Proposing Deferred Acceptance Algorithm.

#!/usr/bin/env python

import streamlit as st
import pandas as pd
from utils.translations import translations_sep as translations
from utils.sep import Student, School, deferred_acceptance

@st.cache_data
def load_sample(lang_code):
    if lang_code == "en":
        studentSample = pd.read_csv("data/sep/student_sample_en.csv")
        schoolSample = pd.read_csv("data/sep/school_sample_en.csv")
    elif lang_code == "zh":
        studentSample = pd.read_csv("data/sep/student_sample_zh.csv")
        schoolSample = pd.read_csv("data/sep/school_sample_zh.csv")
    return studentSample, schoolSample


lang_code = st.session_state["lang_code"]

st.title(translations[lang_code]["title"])
studentSample, schoolSample = load_sample(lang_code)

# st.header("Upload Student Data")
# student_file = st.file_uploader("Upload CSV file with student data (name, GPA, preferences as comma-separated values)", type=["csv"])
st.header(translations[lang_code]["upload_student"])
student_file = st.file_uploader(translations[lang_code]["upload_student"], type=["csv"])

if student_file is None:
    if st.checkbox(translations[lang_code]["Show example"], key="student_example"):
        st.write(studentSample)

# st.header("Upload School Data")
# school_file = st.file_uploader("Upload CSV file with school data (name, quota)", type=["csv"])
st.header(translations[lang_code]["upload_school"])
school_file = st.file_uploader(translations[lang_code]["upload_school"], type=["csv"])

if school_file is None:
    if st.checkbox(translations[lang_code]["Show example"], key="school_example"):
        st.write(schoolSample)

if st.button(translations[lang_code]["run_matching"]):
    if student_file and school_file:
        students_df = pd.read_csv(student_file)
        schools_df = pd.read_csv(school_file)
        
        students = {}
        for _, row in students_df.iterrows():
            if lang_code == "en":
                preferences = [row[f"choice{i}"] for i in range(1, len(row) - 2) if pd.notna(row[f"choice{i}"])]
                students[row["name"]] = Student(row["name"], row["GPA"], preferences)
            elif lang_code == "zh":
                preferences = [row[f"选择{i}"] for i in range(1, len(row) - 2) if pd.notna(row[f"选择{i}"])]
                students[row["姓名"]] = Student(row["姓名"], row["GPA"], preferences)
        
        if lang_code == "en":
            schools = {row["name"]: School(row["name"], int(row["quota"])) for _, row in schools_df.iterrows()}
        elif lang_code == "zh":
            schools = {row["学校名称"]: School(row["学校名称"], int(row["名额"])) for _, row in schools_df.iterrows()}
        
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

