import streamlit as st
from utils.translations import translations_home as translations


st.title("Welcome to MatchME - Matching Made Easy!")

lang = st.selectbox("Select Language / 选择语言", ["中文", "English"])
if lang == "English":
    lang_code = "en"    
elif lang == "中文":
    lang_code = "zh"
st.session_state["lang_code"] = lang_code

modulelist = [translations[lang_code]["sep"], translations[lang_code]["course"]]
module = st.selectbox(translations[lang_code]["select_module"], modulelist)

if st.button(translations[lang_code]["go"]):
    if module == translations[lang_code]["sep"]:
        st.switch_page("pages/2_sep.py")
    elif module == translations[lang_code]["course"]:
        st.switch_page("pages/3_course.py")
             
