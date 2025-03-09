import streamlit as st
from utils.translations import translations

def main():
    st.title(translations["en"]["title"])
    st.write("Welcome to the Student-School Matching App!")

if __name__ == "__main__":
    main()
