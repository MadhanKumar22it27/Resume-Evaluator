import streamlit as st
from user_side import process_user_mode
from recruiters import process_recruiters_mode


def main():
    st.set_page_config(page_title="Resume Evaluator", page_icon="✅")

    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose an option", ["Users", "Recruiters"])

    if app_mode == "Users":
        process_user_mode()

    if app_mode == "Recruiters":
        process_recruiters_mode()

if __name__ == "__main__":
    main()
