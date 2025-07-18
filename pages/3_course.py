# Description: This file contains the code for teacher and course matching

#!/usr/bin/env python

import streamlit as st
import pandas as pd
from utils.translations import translations_course as translations
from utils.course import Teacher, Course, teacher_course_matching
from utils.layout import set_layout
from utils.surveys import teaching_survey

set_layout()
st.logo("image/logo_full_black.png", size="large", icon_image="image/logo_icon_black.png")


@st.cache_data
def load_sample(lang_code):
    if lang_code == "en":
        teacherSample = pd.read_csv("data_sample/course/teacher_sample_en.csv")
        courseSample = pd.read_csv("data_sample/course/course_sample_en.csv")
    elif lang_code == "zh":
        teacherSample = pd.read_csv("data_sample/course/teacher_sample_zh.csv")
        courseSample = pd.read_csv("data_sample/course/course_sample_zh.csv")
    return teacherSample, courseSample


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
teacherSample, courseSample = load_sample(lang_code)

#--------------------------------------------------#
#  Step 1: Upload course data                      #
#--------------------------------------------------#
st.write("<div style='height: 1.5cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]["upload_course"])
course_file = st.file_uploader(translations[lang_code]["upload_course_desc"], type=["csv"], key="course_file")

if course_file is None:
    if st.checkbox(translations[lang_code]["Show example"], key="course_example"):
        st.write(courseSample.head())
else:
    courses_df = pd.read_csv(course_file)
    st.dataframe(courses_df, height=200, hide_index=True)

#--------------------------------------------------#
# Step 2: Upload teacher preferences               #
#--------------------------------------------------#
st.write("<div style='height: 1.5cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]["upload_teacher"])
teacher_file = st.file_uploader(translations[lang_code]["upload_teacher_desc"], type=["csv"], key ="teacher_file")

if teacher_file is None:
    if st.checkbox(translations[lang_code]["Show example"], key="teacher_example"):
        st.write(teacherSample.head())
else:
    teachers_df = pd.read_csv(teacher_file)
    st.dataframe(teachers_df, height=200, hide_index=True)

# Step 2.1: Collect teacher preferences (optional)   #
st.write("<div style='height: 1cm;'></div>", unsafe_allow_html=True)
# st.subheader(translations[lang_code]["collect_teacher_preferences"])
# st.write(translations[lang_code]["collect_teacher_preferences_desc"])
st.write(translations[lang_code]["survey_platform"])
col1, col2, col3 = st.columns(3)
with col1:
    st.link_button(translations[lang_code]["survey_platform1"], 
                   "https://www.wenjuan.com/", 
                   icon=":material/arrow_circle_right:",
                   use_container_width=True)
with col2:
    st.link_button(translations[lang_code]["survey_platform2"], 
                   "https://wj.qq.com/", 
                   icon=":material/arrow_circle_right:",
                   use_container_width=True)

with st.expander(translations[lang_code]["teacher_survey_sample"]):
    teaching_survey()

#--------------------------------------------------#
# Step 4: Run matching                             #
#--------------------------------------------------#
st.write("<div style='height: 1.5cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]["run_matching"])
if st.button(translations[lang_code]["run_matching_button"]):
    if teacher_file and course_file:
        teachers = {}
        for _, row in teachers_df.iterrows():
            if lang_code == "en":
                preferences = [row[f"choice{i}"] for i in range(1, len(row) - 2) if pd.notna(row[f"choice{i}"])]
                teachers[row["name"]] = Teacher(row["name"], row["language"], int(row["required_classes"]), preferences)
            elif lang_code == "zh":
                preferences = [row[f"课程偏好{i}"] for i in range(1, len(row) - 2) if pd.notna(row[f"课程偏好{i}"])]
                teachers[row["老师姓名"]] = Teacher(row["老师姓名"], row["授课语言"], int(row["课时要求"]), preferences)
        
        if lang_code == "en":
            courses = {row["course"]: Course(row["course"], int(row["classes"])) for _, row in courses_df.iterrows()}
        elif lang_code == "zh":
            courses = {row["课程名称"]: Course(row["课程名称"], int(row["班次需求"])) for _, row in courses_df.iterrows()}
        
        teacher_assignments, course_assignments = teacher_course_matching(teachers, courses)
        
        # Convert results to DataFrames
        teacher_results_df = pd.DataFrame([(t, ", ".join(map(str, courses))) for t, courses in teacher_assignments.items()], 
                                            columns=["Teacher", "Assigned Courses"])
        course_results_df = pd.DataFrame([(c, ", ".join(map(str, teachers))) for c, teachers in course_assignments.items()], 
                                            columns=["Course", "Assigned Teachers"])
        teacher_results_df["Required Classes"] = teacher_results_df["Teacher"].map(
            lambda t: teachers[t].required_classes
        )
        teacher_results_df["Assigned Classes"] = teacher_results_df["Teacher"].map(
            lambda t: sum(course[2] for course in teacher_assignments[t])
        )
        teacher_results_df['Gap'] = teacher_results_df['Required Classes'] - teacher_results_df['Assigned Classes']

        course_results_df["Required Classes"] = course_results_df["Course"].map(
            lambda c: courses_df.loc[courses_df["course"] == c, "classes"].values[0] 
            if lang_code == "en" 
            else courses_df.loc[courses_df["课程名称"] == c, "班次需求"].values[0]
        )
        course_results_df["Assigned Classes"] = course_results_df["Course"].map(
            lambda c: sum(teacher[2] for teacher in course_assignments[c])
        )
        course_results_df['Gap'] = course_results_df['Required Classes'] - course_results_df['Assigned Classes']

        
        st.success(translations[lang_code]["success_message"])
        teacher_csv = teacher_results_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        course_csv = course_results_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        

        st.write(translations[lang_code]["teacher_preview:"])
        if lang_code == "zh":
            teacher_results_df.rename(columns={
                "Teacher": "老师",
                "Assigned Courses": "教授课程",
            }, inplace=True)
            st.dataframe(teacher_results_df[["老师", "教授课程"]],height=200)
        st.download_button(translations[lang_code]["download_teachers"], teacher_csv, "teacher_assignments.csv", "text/csv")
        st.write(translations[lang_code]["course_preview:"])
        if lang_code == "zh":
            course_results_df.rename(columns={
                "Course": "课程",
                "Assigned Teachers": "授课老师",
            }, inplace=True)
            st.dataframe(course_results_df[["课程", "授课老师"]],height=200)
        st.download_button(translations[lang_code]["download_courses"], course_csv, "course_enrollments.csv", "text/csv")  
                
    else:
        st.error(translations[lang_code]["error_message"])

