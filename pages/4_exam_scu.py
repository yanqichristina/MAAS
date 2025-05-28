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
from utils.exam_scu import Teacher, Class, assign_proctors
from utils.layout import set_layout
from utils.translations import translations_exam_scu as translations

set_layout()
st.logo("image/logo_full_black.png", size="large", icon_image="image/logo_icon_black.png")


# @st.cache_data
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
exam_name = st.text_input(translations[lang_code]['exam_name'], key="exam_name")
exam1_file = st.file_uploader(translations[lang_code]['upload_exam_schedule_desc'], type=["csv"], key="exam_schedule_file")

if exam1_file is None:
    if st.checkbox(translations[lang_code]['Show example'], key="exam_schedule_example"):
        st.write(exam1Sample.head())
else:
    exam1_info = pd.read_csv(exam1_file)
    st.write(exam1_info)
    exam1_classes = [
        Class(row[translations[lang_code]['course']]+ ' (' +str(row[translations[lang_code]['course_id']]) + ')',
              row[translations[lang_code]['class_id']],
              row[translations[lang_code]['teachers']].split(','),  # Assuming teachers are comma-separated
              row[translations[lang_code]['student_count']],
              row[translations[lang_code]['exam_date']],
              row[translations[lang_code]['exam_time']],
              row[translations[lang_code]['exam_location']]
            # 'main_proctor_faculty': row[translations[lang_code]['main_proctor_faculty']],
            # 'joint_proctor_faculty': row[translations[lang_code]['joint_proctor_faculty']],
        )
        for _, row in exam1_info.iterrows()
    ] 
    exam2_file = None

# allow uploading of 2nd batch exam schedule
# if st.button(translations[lang_code]['upload_exam_schedule_2'], key="exam2_schedule"):
#     exam2_file = st.file_uploader("", type=["csv"], key="exam2_schedule_file")
#     if exam2_file is not None:
#         exam2_info = pd.read_csv(exam2_file)
#         exam2_classes = [
#             {
#                 'course': row[translations[lang_code]['course']],
#                 'teachers': row[translations[lang_code]['teachers']].split(','),  # Assuming teachers are comma-separated
#                 'class_id': row[translations[lang_code]['class_id']],
#                 'exam_date': row[translations[lang_code]['exam_date']],
#                 'main_proctor_faculty': row[translations[lang_code]['main_proctor_faculty']],
#                 'joint_proctor_faculty': row[translations[lang_code]['joint_proctor_faculty']],
#             }
#             for _, row in exam2_info.iterrows()
#         ]

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
    st.write(teacher_info)
    # remove rows with non-empty column '豁免主考'
    # teacher_info = teacher_info[teacher_info[translations[lang_code]['exempted_main']].isna()]
    teachers = [
        Teacher(row[translations[lang_code]['teacher_name']], 
                row[translations[lang_code]['workload']],
                row[translations[lang_code]['exempted_main']],
                row[translations[lang_code]['exempted_joint']],
                row[translations[lang_code]['preferred_location']],
                row[translations[lang_code]['special_needs']],
                [row[translations[lang_code]['date1']], row[translations[lang_code]['date2']], row[translations[lang_code]['date3']]])
        for _, row in teacher_info.iterrows()
    ]
    
    # teachers_df = [
    #     {
    #         'name': t.name,
    #         'workload': t.workload,
    #         'exemption_main': t.exempted_main,
    #         'exemption_joint': t.exempted_joint,
    #         'preferred_location': t.preferred_location,
    #         'special_needs': t.special_needs,
    #         'unavailable_date': t.unavailable_dates
    #     }
    #     for t in teachers
    # ]
    # teachers_df = pd.DataFrame(teachers_df)
    # teachers_df = teachers_df[teachers_df['special_needs'].str.contains('不排早八', na=False)]
    # st.write(teachers_df)

#------------------------------------------------#
#  Step 3: Run assignment                        #
#------------------------------------------------#

st.write("<div style='height: 2cm;'></div>", unsafe_allow_html=True)
st.subheader(translations[lang_code]['run_assignment'])
if st.button(translations[lang_code]['run_assignment_button']):
    if exam1_file is None or teacher_info is None:
        st.error(translations[lang_code]['error_message'])
        exam1_classes = [
            Class(row[translations[lang_code]['course']]+ ' (' +str(row[translations[lang_code]['course_id']]) + ')',
                row[translations[lang_code]['class_id']],
                row[translations[lang_code]['teachers']].split(','),  # Assuming teachers are comma-separated
                row[translations[lang_code]['student_count']],
                row[translations[lang_code]['exam_date']],
                row[translations[lang_code]['exam_time']],
                row[translations[lang_code]['exam_location']]
                # 'main_proctor_faculty': row[translations[lang_code]['main_proctor_faculty']],
                # 'joint_proctor_faculty': row[translations[lang_code]['joint_proctor_faculty']],
            )
            for _, row in exam1Sample.iterrows()
        ]

        teachers = [
            Teacher(row[translations[lang_code]['teacher_name']], 
                    row[translations[lang_code]['workload']],
                    row[translations[lang_code]['exempted_main']],
                    row[translations[lang_code]['exempted_joint']],
                    row[translations[lang_code]['preferred_location']],
                    row[translations[lang_code]['special_needs']],
                    [row[translations[lang_code]['date1']], row[translations[lang_code]['date2']], row[translations[lang_code]['date3']]])
            for _, row in teacherSample.iterrows()
        ]
    
    else:
        # Assign proctors for both exam batches
        assign_proctors(teachers, exam1_classes)
        # Convert Class object to DataFrames
        exam1_classes = [
            {
            'course': cls.course.split(' (')[0],  # Extract course name
            'course_id': cls.course.split(' (')[1][:-1],  # Extract course ID
            'class_id': cls.class_id,
            'teachers': ', '.join(cls.teachers),
            'stu_count': cls.stu_count,
            'exam_date': cls.exam_date,
            'exam_time': cls.exam_time,
            'exam_location': cls.exam_location,
            'exam_id': cls.exam_id,
            # 'main_proctor_faculty': cls.main_proctor_faculty,
            # 'joint_proctor_faculty': cls.joint_proctor_faculty,
            'main_proctor': cls.main_proctor,
            'joint_proctor': cls.joint_proctor
            }
            for cls in exam1_classes
        ]
        exam1_classes_df = pd.DataFrame(exam1_classes)
        exam1_classes_df.rename(columns={
            'course': translations[lang_code]['course'],
            'course_id': translations[lang_code]['course_id'],
            'class_id': translations[lang_code]['class_id'],
            'teachers': translations[lang_code]['teachers'],
            'stu_count': translations[lang_code]['student_count'],
            'exam_date': translations[lang_code]['exam_date'],
            'exam_time': translations[lang_code]['exam_time'],
            'exam_location': translations[lang_code]['exam_location'],
            'exam_id': translations[lang_code]['exam_id'],
            # 'main_proctor_faculty': translations[lang_code]['main_proctor_faculty'],
            # 'joint_proctor_faculty': translations[lang_code]['joint_proctor_faculty'],
            'main_proctor': translations[lang_code]['main_proctor'],
            'joint_proctor': translations[lang_code]['joint_proctor'],
        }, inplace=True)
        exam1_csv = exam1_classes_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        
        # Display results
        st.subheader(translations[lang_code]['invigilator_preview:'])
        def highlight_columns(s):
            return ['background-color: lightyellow' if col in [translations[lang_code]['main_proctor'], translations[lang_code]['joint_proctor']] else '' for col in s.index]

        st.write(exam1_classes_df[[
            translations[lang_code]['course'],
            translations[lang_code]['course_id'],
            translations[lang_code]['class_id'],
            translations[lang_code]['teachers'],
            translations[lang_code]['student_count'],
            translations[lang_code]['exam_date'],
            translations[lang_code]['exam_time'],
            translations[lang_code]['exam_location'],
            translations[lang_code]['exam_id'],
            translations[lang_code]['main_proctor'],
            translations[lang_code]['joint_proctor']
            ]].style.apply(highlight_columns, axis=1))
        
        today = pd.Timestamp.now().strftime("%y%m%d")
        st.download_button(translations[lang_code]["download_classes"], 
                            exam1_csv, 
                            f"{exam_name}监考安排{today}.csv", 
                            "text/csv")

        # if exam2_file is not None:
        #     assign_proctors(teachers, exam2_classes)
        #     exam2_csv = exam2_classes.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        #     st.write(pd.DataFrame(exam2_classes))
        #     st.download_button(translations[lang_code]["download_classes"], 
        #                        exam2_csv, 
        #                        "proctor_assignments2.csv", 
        #                        "text/csv")

        st.subheader(translations[lang_code]['workload_preview:'])
        # Sum up invigilation duties assigned for each teacher, and append to the teacher_info DataFrame
        teacher_info[exam_name] = 0
        teacher_info[f'{exam_name}主考'] = 0
        teacher_info[f'{exam_name}监考'] = 0
        for teacher in teachers:
            teacher_info.loc[teacher_info[translations[lang_code]['teacher_name']] == teacher.name, f'{exam_name}主考'] = teacher.main_proctor_count
            teacher_info.loc[teacher_info[translations[lang_code]['teacher_name']] == teacher.name, f'{exam_name}监考'] = teacher.joint_proctor_count
            teacher_info.loc[teacher_info[translations[lang_code]['teacher_name']] == teacher.name, exam_name] = teacher.main_proctor_count + teacher.joint_proctor_count
            # Update workload in teacher_info DataFrame
            teacher_info.loc[teacher_info[translations[lang_code]['teacher_name']] == teacher.name, '本期监考总数'] += teacher.main_proctor_count + teacher.joint_proctor_count
            teacher_info.loc[teacher_info[translations[lang_code]['teacher_name']] == teacher.name, translations[lang_code]['workload']] = teacher.workload
        # st.write(teacher_info[[
        #     translations[lang_code]['teacher_name'],
        #     translations[lang_code]['workload'],
        #     translations[lang_code]['preferred_location'],
        #     f'{exam_name}主考',
        #     f'{exam_name}监考',
        #     exam_name]])

        # put the column exam_name before the column '本期监考总数‘
        cols = list(teacher_info.columns)
        cols.insert(cols.index('本期监考总数'), cols.pop(cols.index(exam_name)))
        teacher_info = teacher_info[cols]

        # Convert all float type columns to integer while keeping None values
        float_cols = teacher_info.select_dtypes(include=['float']).columns
        teacher_info[float_cols] = teacher_info[float_cols].apply(lambda x: x.round().astype('Int64'))
        
        def highlight_exam_name(s):
            return ['background-color: lightyellow' if col == exam_name else '' for col in s.index]

        st.write(teacher_info.style.apply(highlight_exam_name, axis=1))

        # Download the updated teacher information
        teacher_csv = teacher_info.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(translations[lang_code]["download_teachers"], 
                            teacher_csv, 
                            f"老师监考工作量{today}.csv", 
                            "text/csv")
        
        # Display success message
        st.success(translations[lang_code]['success_message'])