# Description: This file contains the code for the Streamlit app that runs the Student-Proposing Deferred Acceptance Algorithm.

#!/usr/bin/env python

import streamlit as st
import pandas as pd
from utils.translations import translations_sep as translations
from utils.sep_nus import Student, Program, deferred_acceptance
from utils.layout import set_layout

set_layout()
st.logo("image/logo_full_black.png", size="large", icon_image="image/logo_icon_black.png")


@st.cache_data
def load_sample(lang_code):
    if lang_code == "en":
        studentSample = pd.read_csv("data_sample/sep/student_sample_nus.csv")
        schoolSample = pd.read_csv("data_sample/sep/school_sample_nus.csv")
    elif lang_code == "zh":
        studentSample = pd.read_csv("data_sample/sep/student_sample_zh.csv")
        schoolSample = pd.read_csv("data_sample/sep/school_sample_zh.csv")
    return studentSample, schoolSample

if "lang_code" not in st.session_state:
    st.session_state["lang_code"] = "en"
# Language selection dropdown in the sidebar, default to English if not selecte
with st.sidebar:
    lang = st.selectbox("Select Language / 选择语言", ["中文", "English"], index=1 if st.session_state["lang_code"] == "en" else 0)
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
        st.dataframe(studentSample, hide_index=True)
else:
    students_df = pd.read_csv(student_file)
    st.dataframe(students_df, hide_index=True)
    students = {}
    # Group the data by student name to collect all preferences
    if lang_code == "en":
        grouped = students_df.groupby("*EmplID")
        for student_name, group in grouped:
            preferences = [
                [row["Ext. Study Location"], row["*Ext. Study Period"]] 
                for _, row in sorted(group.iterrows(), key=lambda x: x[1]["Destination Ranking"])
                ]
            students[student_name] = Student(
                student_name, 
                group.iloc[0]["GPA"], 
                group.iloc[0]["Total Score"],
                group.iloc[0]["Student Major"].replace(' (Hons)', ''),
                group.iloc[0]["Seniority"],
                group.iloc[0]["Singapore Residency Status"],
                preferences
                )
        # st.write(students['27X'])
    elif lang_code == "zh":
        grouped = students_df.groupby("姓名")
        for student_name, group in grouped:
            preferences = [[row["学校名称"], row["学期"]] for _, row in group.iterrows()]
            students[student_name] = Student(student_name, group.iloc[0]["GPA"], preferences)
            

#--------------------------------------------------#
# Step 2: Upload school quota                      #
#--------------------------------------------------#
st.write("<div style='height: 1.5cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]["upload_school"])
school_file = st.file_uploader(translations[lang_code]["upload_school_desc"], type=["csv"])

if school_file is None:
    if st.checkbox(translations[lang_code]["Show example"], key="school_example"):
        st.dataframe(schoolSample, hide_index=True)
else:
    schools_df = pd.read_csv(school_file)
    st.dataframe(schools_df, hide_index=True)
    if lang_code == "en":
        programs = {
            row["ProgramID"]: 
            Program(
                row["SchoolName"],
                row["Semester"],
                row["Major (incl)"].split(", ") if not pd.isna(row["Major (incl)"]) else [],
                row["Major (excl)"].split(", ") if not pd.isna(row["Major (excl)"]) else [],
                int(row["Quota"]),
                row["minGPA"],
                row["Seniority"],
                row["Nationality (excl)"].split(", ") if not pd.isna(row["Nationality (excl)"]) else []
            )            
            for _, row in schools_df.iterrows()}
    elif lang_code == "zh":
        schools = {row["学校名称"]: School(row["学校名称"], int(row["名额"]), row["最低绩点"]) for _, row in schools_df.iterrows()}


#--------------------------------------------------#
# Step 3: Run matching                             #
#--------------------------------------------------#
st.write("<div style='height: 1.5cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]["run_matching"])
if st.button(translations[lang_code]["run_matching"]):
    if student_file and school_file:                
        student_assignments, program_enrollments, matching_process_df = deferred_acceptance(students, programs)

        # clean results for student assignments and school enrollments        
        student_assignments_df = pd.DataFrame(list(student_assignments.items()), columns=["Student", "ProgramID"])
        student_assignments_df = student_assignments_df.merge(
            schools_df[['ProgramID', 'SchoolName', 'Semester']].rename(columns={'Semester': 'PU required semester'}), 
            on="ProgramID",
            how="left"
            )
        
        # find the student's preferred exchange semester in student.preferences for the assigned school
        student_assignments_df["Student preferred semester"] = student_assignments_df["Student"].apply(lambda x: students[x].preferences[students[x].current_proposal - 1][1])

        program_enrollments_df = pd.DataFrame(list(program_enrollments.items()), columns=["ProgramID", "Enrolled Student"])
        program_enrollments_df = program_enrollments_df.merge(
            schools_df[['ProgramID', 'SchoolName', 'Semester', 'Quota']].rename(columns={'Semester': 'PU required semester'}), 
            on="ProgramID", 
            how="left"
            )
        
        # add a column to show the number of students enrolled in each school
        program_enrollments_df["Students Count"] = program_enrollments_df["Enrolled Student"].apply(lambda x: len(x) if x else 0)
        program_enrollments_df["Quota Remaining"] = program_enrollments_df["Quota"] - program_enrollments_df["Students Count"]
        
        st.success(translations[lang_code]["success_message"])
        st.write(translations[lang_code]["student_preview:"])
        st.dataframe(student_assignments_df, hide_index=True)
        st.write(translations[lang_code]["school_preview:"])
        st.dataframe(program_enrollments_df[program_enrollments_df["Enrolled Student"].apply(lambda x: len(x) > 0)], hide_index=True)


        # append the results to the input dataframes and allow users to download the results as csv files
        students_df["Assigned ProgramID"] = students_df["*EmplID"].map(student_assignments)
        students_df["Assigned University"] = students_df["Assigned ProgramID"].map(programs).apply(lambda x: x.schoolName if x else None)
        students_df['PU required semester'] = students_df['Assigned ProgramID'].map(programs).apply(lambda x: x.sem if x else None)
        schools_df["Enrolled Students"] = schools_df["ProgramID"].map(program_enrollments).apply(lambda x: ", ".join(x) if x else None)
        schools_df["Enrolled Students Count"] = schools_df["Enrolled Students"].apply(lambda x: len(x.split(", ")) if x else 0)
        schools_df["Quota Remaining"] = schools_df["Quota"] - schools_df["Enrolled Students Count"]
        
        student_csv = students_df.to_csv(index=False).encode("utf-8")
        school_csv = schools_df.to_csv(index=False).encode("utf-8")
        matching_process_csv = matching_process_df.to_csv(index=False).encode("utf-8")

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
                "Download Matching Processes",
                matching_process_csv,
                "matching_processes.csv",
                "text/csv",
                on_click="ignore"
            )
    else:
        st.error(translations[lang_code]["error_message"])

