# Description: This file contains the code for the Streamlit app that runs the Student-Proposing Deferred Acceptance Algorithm.

#!/usr/bin/env python

import streamlit as st
import pandas as pd
from utils.translations import translations_sep as translations
from utils.sep import Student, School, deferred_acceptance
from utils.layout import set_layout

set_layout()
st.logo("image/logo_full_black.png", size="large", icon_image="image/logo_icon_black.png")


@st.cache_data
def load_sample(lang_code):
    if lang_code == "en":
        studentSample = pd.read_csv("data_sample/sep/student_sample_en.csv")
        schoolSample = pd.read_csv("data_sample/sep/school_sample_en.csv")
    elif lang_code == "zh":
        studentSample = pd.read_csv("data_sample/sep/student_sample_zh.csv")
        schoolSample = pd.read_csv("data_sample/sep/school_sample_zh.csv")
    return studentSample, schoolSample

lang_code = st.session_state["lang_code"]
with st.sidebar:
    lang = st.selectbox("Select Language / 选择语言", ["中文", "English"], index=1 if lang_code == "en" else 0)
if lang == "English":
    lang_code = "en"    
elif lang == "中文":
    lang_code = "zh"
st.session_state["lang_code"] = lang_code

st.title(translations[lang_code]["title"])
st.write(translations[lang_code]["intro"])
# Load sample data
studentSample, schoolSample = load_sample(lang_code)


#--------------------------------------------------#
# Step 1: Upload student preferences and CPA       #
#--------------------------------------------------#
st.write("<div style='height: 1.5cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]["upload_student"])
student_file = st.file_uploader(translations[lang_code]["upload_student_desc"], type=["csv"])

if student_file is None:
    if st.checkbox(translations[lang_code]["Show example"], key="student_example"):
        st.write(studentSample.head())
else:
    students_df = pd.read_csv(student_file)
    st.write(students_df.head())
    students = {}
    for _, row in students_df.iterrows():
        if lang_code == "en":
            preferences = [row[f"Choice{i}"] for i in range(1, len(row) - 1) if pd.notna(row[f"Choice{i}"])]
            students[row["StudentName"]] = Student(row["StudentName"], row["GPA"], preferences)
        elif lang_code == "zh":
            preferences = [row[f"选择{i}"] for i in range(1, len(row) - 1) if pd.notna(row[f"选择{i}"])]
            students[row["姓名"]] = Student(row["姓名"], row["GPA"], preferences)


#--------------------------------------------------#
# Step 2: Upload school quota                      #
#--------------------------------------------------#
st.write("<div style='height: 1.5cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]["upload_school"])
school_file = st.file_uploader(translations[lang_code]["upload_school_desc"], type=["csv"])

if school_file is None:
    if st.checkbox(translations[lang_code]["Show example"], key="school_example"):
        st.write(schoolSample.head())
else:
    schools_df = pd.read_csv(school_file)
    st.write(schools_df.head())
    if lang_code == "en":
        schools = {row["SchoolName"]: School(row["SchoolName"], int(row["Quota"])) for _, row in schools_df.iterrows()}
    elif lang_code == "zh":
        schools = {row["学校名称"]: School(row["学校名称"], int(row["名额"])) for _, row in schools_df.iterrows()}


#--------------------------------------------------#
# Step 3: Run matching                             #
#--------------------------------------------------#
st.write("<div style='height: 1.5cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]["run_matching"])
if st.button(translations[lang_code]["run_matching"]):
    if student_file and school_file:                
        student_assignments, school_enrollments, output_text = deferred_acceptance(students, schools)
        
        student_assignments_df = pd.DataFrame(list(student_assignments.items()), columns=["Student", "Assigned School"])
        school_enrollments_df = pd.DataFrame(list(school_enrollments.items()), columns=["School", "Enrolled Student"])
        # school_enrollments_df = pd.DataFrame([(school, student) for school, students in school_enrollments.items() for student in students], columns=["School", "Enrolled Student"])
        
        st.success(translations[lang_code]["success_message"])
        student_csv = student_assignments_df.to_csv(index=False).encode("utf-8")
        school_csv = school_enrollments_df.to_csv(index=False).encode("utf-8")

        
        st.write(translations[lang_code]["student_preview:"])
        st.table(student_assignments_df)
        st.write(translations[lang_code]["school_preview:"])
        st.table(school_enrollments_df)

        # Create a button to export the results
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                translations[lang_code]["download_students"],
                student_csv,
                "student_assignments.csv",
                "text/csv",
                on_click="ignore"
            )
        with col2:
            st.download_button(
                translations[lang_code]["download_schools"],
                school_csv,
                "school_enrollments.csv",
                "text/csv",
                on_click="ignore"
            )
        
        with col3:
            st.download_button(
                label="Download Matching Processes",
                data='\n'.join(map(str, output_text)) if isinstance(output_text, list) else str(output_text),
                file_name="output.txt",
                mime="text/plain",
                on_click="ignore"
            )
    else:
        st.error(translations[lang_code]["error_message"])

