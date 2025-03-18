
#!/usr/bin/env python

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# %% Functions
def initialize_authenticator():
    """Initialize the authenticator with configuration"""
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )

def login():
    """Handle login functionality"""
    authenticator = initialize_authenticator()
    
    # Login form
    authenticator.login('main', 'Login')
    
    if st.session_state['authentication_status']:
        st.session_state['user'] = authenticator
        st.session_state['logged_in'] = True
        st.success('Login successful!')
    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')
    
    st.rerun()

def logout():
    """Handle logout functionality"""
    if 'user' in st.session_state:
        user = st.session_state['user']
        if st.button("Log out"):
            user.logout()
            for key in list(st.session_state.keys()):
                if key in ['user', 'logged_in', 'authentication_status']:
                    del st.session_state[key]
            st.session_state['logged_in'] = False
            st.success('Logged out successfully!')
            st.rerun()

# %% Page definitions
# login_page = st.Page(login, title="Log in", icon=":material/login:")
# logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
home = st.Page("pages/1_home.py", title="Home", icon=":material/home:", default=True)
sep_page = st.Page("pages/2_sep.py", title="SEP", icon=":material/school:") 
course_page = st.Page("pages/3_course.py", title="Course", icon=":material/book:")



st.set_page_config(layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# if st.session_state.get('logged_in', False):
pg = st.navigation(
    {   
        "Modules": [home, sep_page, course_page],
    }
)
# else:
#     pg = st.navigation([login_page])

pg.run()
