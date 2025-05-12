import streamlit as st
import pandas as pd
from utils.translations import translations_teaching_survey as translations

def teaching_survey():
    lang_code = st.session_state["lang_code"]
    # Page title
    st.title(translations[lang_code]["title"])

    # Introduction
    st.write(translations[lang_code]["intro"])

    teacherName = st.text_input(translations[lang_code]["name"])

    # Preferred Course List
    # st.header(translations[lang_code]["preferred_courses"])
    # st.write(translations[lang_code]["select_courses"])
    # courseslist = pd.read_csv("data/course/courselist.csv")
    if lang_code == "en":
        courseslist = ["course1", "course2", "course3", "course4", "course5"]
    elif lang_code == "zh":
        courseslist = ["课程1", "课程2", "课程3", "课程4", "课程5"]

    prefered_course1 = st.selectbox(
        translations[lang_code]["1st_choice"],   
        options=courseslist,
    )

    prefered_course2 = st.selectbox(
        translations[lang_code]["2nd_choice"],
        options=courseslist[courseslist != prefered_course1]
    )

    prefered_course3 = st.selectbox(
        translations[lang_code]["3rd_choice"],
        options=[course for course in courseslist if course not in [prefered_course1, prefered_course2]]
    )

    # Requirement Classes
    # st.header(translations[lang_code]["required_classes"])
    required_classes = st.number_input(
        translations[lang_code]["select_classes"],
        min_value=1,  # Minimum value restriction
        max_value=5  # Maximum value restriction
    )

    if required_classes > 3:
        st.warning(translations[lang_code]["warning_message"])

    # Teaching Language
    # st.header(translations[lang_code]["teaching_language"])
    if lang_code == "en":
        lang_options = ["English", "Mandarin", "Bilingual", "Other"]
    elif lang_code == "zh":
        lang_options = ["英文", "普通话", "双语", "其他"]
    teaching_language = st.selectbox(
        translations[lang_code]["select_language"],
        options = lang_options
    )

    if teaching_language == "Other" or teaching_language == "其他":
        teaching_language = st.text_input(translations[lang_code]["other_language"])

    # Optional Comments
    # st.header(translations[lang_code]["additional_request"])
    comments = st.text_area(translations[lang_code]["additional_comments"])

    st.button(translations[lang_code]["submit_button"])