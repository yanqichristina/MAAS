import streamlit as st
from utils.translations import translations_home as translations
from utils.layout import set_layout

set_layout()
st.logo("image/logo_full_black.png", size="large", link="https://nexmatch.co", icon_image="image/logo_icon_black.png")

st.markdown(
    """
    <h1 style="margin-bottom: 0;">
        <span style="color: orange;">M A A </span><span style="color: #007bff;">S</span>
    </h1>
    <h5 style="margin-top: -10px; font-weight: normal;">
        <span style="color: orange;">M</span>atching & <span style="color: orange;">A</span>llocation <span style="color: orange;">A</span>ssistant for <span style="color: #007BFF;">S</span>chools
    </h5>
    """,
    unsafe_allow_html=True
)

st.markdown("<br><br>", unsafe_allow_html=True)

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

modulelist = [translations[lang_code]["sep"], translations[lang_code]["course"]]


# To make the padding adaptable to the column (card) width, use relative units like 'em', '%', or 'vw'.
# Here, padding is set as a percentage of the button width for adaptability.

button_style = """
    <style>
    .custom-button {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 4% 8%; /* Top/bottom padding is 6% of button width, left/right is 0 */
        font-size: clamp(0.8em, 25vw, 1.2em); /* Responsive font size */
        font-weight: bold;
        color: #007bff;
        background-color: #f8f9fa;
        border: none;
        text-align: center;
        text-decoration: none;
        width: 60%;
        cursor: pointer;
        flex-direction: column;
        position: relative;
        overflow: hidden;
        box-sizing: border-box;
        margin: 0 auto; /* Center the button horizontally */
    }
    .custom-button:hover {
        background-color: blue;
        color: white;
        transition: background-color 0.3s ease;
        border: 1px white solid;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transform: translateY(-2px);
    }
    .custom-button:link, .custom-button:visited {
        text-decoration: none;
    }
    </style>
"""

# Use custom HTML buttons with JavaScript for user interactions
st.markdown(button_style, unsafe_allow_html=True)


st.markdown(
    f'<a href="?page=course" class="custom-button" target="_self">{translations[lang_code]["course"]}</a>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<a href="?page=exam" class="custom-button" target="_self">{translations[lang_code]["exam"]}</a>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<a href="?page=sep" class="custom-button" target="_self">{translations[lang_code]["sep"]}</a>',
    unsafe_allow_html=True,
)

# Detect which button was clicked
query_params = st.query_params
# st.write(query_params)
if "page" in query_params:
    clicked_button = query_params["page"]
    st.write(f"User clicked on: {clicked_button}")
    # Add navigation or logic based on the button clicked
    if clicked_button == "sep":
        st.switch_page("pages/2_sep.py")
    elif clicked_button == "course":
        st.switch_page("pages/3_course.py")
    elif clicked_button == "exam":
        st.switch_page("pages/4_exam_scu2.py")


