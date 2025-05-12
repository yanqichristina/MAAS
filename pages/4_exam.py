# Description: This file contains the code for exam proctor assignment
# SUFE holds exam in two batches, exam1 and exam2.
# Each batch has a set of courses, and each course has a set of classes.
# Each class has one main proctor and one joint proctor.
# Each teacher can serve as the main proctor for only 1 course with up to 3 classes,
# and be the joint proctor for up to 2 classes of any course.
# The proctors are assigned based on their time availability and priority.

#!/usr/bin/env python

import streamlit as st
import pandas as pd
from utils.exam import Teacher, assign_proctors
from utils.layout import set_layout
from utils.translations import translations_exam as translations

set_layout()
st.logo("image/logo_full_black.png", size="large", icon_image="image/logo_icon_black.png")


@st.cache_data
def load_sample():
    if lang_code == "en":
        teacherSample = pd.read_csv("data_sample/exam/teacher_sample_en.csv")
        exam1Sample = pd.read_csv("data_sample/exam/exam1_sample_en.csv")
    elif lang_code == "zh":
        teacherSample = pd.read_csv("data_sample/exam/teacher_sample_zh.csv")
        exam1Sample = pd.read_csv("data_sample/exam/exam1_sample_zh.csv")
    return teacherSample, exam1Sample



lang_code = st.session_state["lang_code"]
st.title(translations[lang_code]['title'])
st.write(translations[lang_code]['intro'])
st.write("<div style='height: 2cm;'></div>", unsafe_allow_html=True)
teacherSample, exam1Sample = load_sample()

#------------------------------------------------#
#  Step 1: Upload exam schedule                  #
#------------------------------------------------#
st.subheader(translations[lang_code]['upload_exam_schedule'])
exam1_file = st.file_uploader(translations[lang_code]['upload_exam_schedule_desc'], type=["csv"], key="exam_schedule_file")

if exam1_file is None:
    if st.checkbox(translations[lang_code]['Show example'], key="exam_schedule_example"):
        st.write(exam1Sample.head())
else:
    exam1_info = pd.read_csv(exam1_file)
    exam1_classes = [
        {
            'course': row[translations[lang_code]['course']],
            'teachers': row[translations[lang_code]['teachers']].split(','),  # Assuming teachers are comma-separated
            'class_id': row[translations[lang_code]['class_id']],
            'exam_date': row[translations[lang_code]['exam_date']],
            'main_proctor_faculty': row[translations[lang_code]['main_proctor_faculty']],
            'joint_proctor_faculty': row[translations[lang_code]['joint_proctor_faculty']],
        }
        for _, row in exam1_info.iterrows()
    ]
    exam2_file = None

# allow uploading of 2nd batch exam schedule
if st.button(translations[lang_code]['upload_exam_schedule_2'], key="exam2_schedule"):
    exam2_file = st.file_uploader("", type=["csv"], key="exam2_schedule_file")
    if exam2_file is not None:
        exam2_info = pd.read_csv(exam2_file)
        exam2_classes = [
            {
                'course': row[translations[lang_code]['course']],
                'teachers': row[translations[lang_code]['teachers']].split(','),  # Assuming teachers are comma-separated
                'class_id': row[translations[lang_code]['class_id']],
                'exam_date': row[translations[lang_code]['exam_date']],
                'main_proctor_faculty': row[translations[lang_code]['main_proctor_faculty']],
                'joint_proctor_faculty': row[translations[lang_code]['joint_proctor_faculty']],
            }
            for _, row in exam2_info.iterrows()
        ]

#------------------------------------------------#
#  Step 2: Upload invigilator information        #
#------------------------------------------------#
st.write("<div style='height: 2cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]['upload_invigilator'])
teacher_file = st.file_uploader(translations[lang_code]['upload_invigilator_desc'], type=["csv"], key="invigilator_file")

if teacher_file is None:
    # Show example data if no file is uploaded
    if st.checkbox(translations[lang_code]['Show example'], key="invigilator_example"):
        st.write(teacherSample.head())
else:
    teacher_info = pd.read_csv(teacher_file)
    teachers = [
        Teacher(row[translations[lang_code]['teacher_name']], [row[translations[lang_code]['date1']], row[translations[lang_code]['date2']], row[translations[lang_code]['date3']]])
        for _, row in teacher_info.iterrows()
    ]

#------------------------------------------------#
#  Step 3: Run assignment                        #
#------------------------------------------------#

st.write("<div style='height: 2cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]['run_assignment'])
if st.button(translations[lang_code]['run_assignment_button']):
    if exam1_file is None or teacher_info is None:
        st.error(translations[lang_code]['error_message'])
    else:
        # Assign proctors for both exam batches
        assign_proctors(teachers, exam1_classes)
        # Convert results to DataFrames
        exam1_classes_df = pd.DataFrame(exam1_classes)
        exam1_classes_df.rename(columns={
            'course': translations[lang_code]['course'],
            'teachers': translations[lang_code]['teachers'],
            'class_id': translations[lang_code]['class_id'],
            'exam_date': translations[lang_code]['exam_date'],
            'main_proctor_faculty': translations[lang_code]['main_proctor_faculty'],
            'joint_proctor_faculty': translations[lang_code]['joint_proctor_faculty'],
            'main_proctor': translations[lang_code]['main_proctor'],
            'joint_proctor': translations[lang_code]['joint_proctor'],
        }, inplace=True)
        exam1_csv = exam1_classes_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        # Display results
        st.subheader(translations[lang_code]['invigilator_preview:'])
        st.write(pd.DataFrame(exam1_classes_df[['课程名称','授课老师','教学班','考试日期','主考院系','主考老师','监考院系','监考老师']]))
        st.download_button(translations[lang_code]["download_invigilators"], exam1_csv, "proctor_assignments.csv", "text/csv")

        if exam2_file is not None:
            assign_proctors(teachers, exam2_classes)
            exam2_csv = exam2_classes.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.write(pd.DataFrame(exam2_classes))
            st.download_button(translations[lang_code]["download_invigilators"], exam2_csv, "proctor_assignments2.csv", "text/csv")

        st.success(translations[lang_code]['success_message'])


