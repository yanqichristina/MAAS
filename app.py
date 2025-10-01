
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
    
    # Pre-hashing all plain text passwords once
    # stauth.Hasher.hash_passwords(config['credentials'])

    authenticator =  stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )
    
    
    return authenticator, config

def login():
    """Handle login functionality"""
    authenticator, config = initialize_authenticator()
    
    # Login form
    try:
        authenticator.login()
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        st.error(f"Login failed: {e}")
    
    if st.session_state['authentication_status']:
        st.session_state['user'] = authenticator
        st.session_state['logged_in'] = True
        st.success('Login successful!')
    elif st.session_state['authentication_status'] is False:
        st.error('Username/password is incorrect')
    elif st.session_state['authentication_status'] is None:
        st.warning('Please enter your username and password')

    if st.button("Register New User"):
        # Registration form
        try:
            email_of_registered_user, \
            username_of_registered_user, \
            name_of_registered_user = authenticator.register_user()
            if email_of_registered_user:
                st.success('User registered successfully')
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            st.error(e)
    
    # with st.expander("Forgot Username"):
    #     try:
    #         username_of_forgotten_username, \
    #         email_of_forgotten_username = authenticator.forgot_username()
    #         if username_of_forgotten_username:
    #             st.success('Username to be sent securely')
    #             # To securely transfer the username to the user please see step 8.
    #         elif username_of_forgotten_username == False:
    #             st.error('Email not found')
    #     except Exception as e:
    #         st.error(e)

    # with st.expander("Forgot Password"):
    #     try:
    #         username_of_forgotten_password, \
    #         email_of_forgotten_password, \
    #         new_random_password = authenticator.forgot_password()
    #         if username_of_forgotten_password:
    #             st.success('New password to be sent securely')
    #             # To securely transfer the new password to the user please see step 8.
    #         elif username_of_forgotten_password == False:
    #             st.error('Username not found')
    #     except Exception as e:
    #         st.error(e)
    

    
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

def reset_pwd():
    """Handle password reset functionality"""
    if st.session_state.get('authentication_status'):
        user = st.session_state['user']
        try:
            if user.reset_password(st.session_state.get('username')):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)

def update_user_profile():
    """Handle user profile update functionality"""
    if st.session_state.get('authentication_status'):
        user = st.session_state['user']
        try:
            if user.update_user_details(st.session_state.get('username')):
                st.success('Entries updated successfully')
        except Exception as e:
            st.error(e)


# %% Page definitions
# login_page = st.Page(login, title="Log in", icon=":material/login:")
# logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
# reset_pwd_page = st.Page(reset_pwd, title="Reset Password", icon=":material/lock_reset:")
# update_user_profile_page = st.Page(update_user_profile, title="Update Profile", icon=":material/account_circle:")
home = st.Page("modules/1_home.py", title="Homepage", icon=":material/home:", default=True)
sep_page = st.Page("modules/2_sep_nus.py", title="SEP_NUS", icon=":material/school:") 
course_page = st.Page("modules/3_course.py", title="Lecturer-Course", icon=":material/book:")
exam_page = st.Page("modules/4_exam_scu2.py", title="Proctor-Exam", icon=":material/assignment:")



st.set_page_config(layout="wide")

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False

# if st.session_state.get('logged_in') is True:
pg = st.navigation(
    {   
        "Modules": [home, sep_page],
        # "Settings": [logout_page, reset_pwd_page],
    }
)
# else:
#     pg = st.navigation([login_page])

pg.run()
