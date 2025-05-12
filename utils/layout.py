import streamlit as st

def set_layout():
   
    
    # Set font family for the entire app
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
    
        /* Apply the font family globally */
        html, body, div, span, app-view-container, [class*="css"]  {
            font-family: 'Exo 2', sans-serif;
        }

        /* Apply the font family to all headings */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Exo 2', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True
    )