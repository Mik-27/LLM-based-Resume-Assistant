import streamlit as st

from generators.cover_letter_generator import CoverLetterGenerator

st.title("Cover Letter")

if "cover_letter_generator" not in st.session_state:
    st.session_state.cover_letter_generator = CoverLetterGenerator(st.session_state.resume, st.session_state.job_description)