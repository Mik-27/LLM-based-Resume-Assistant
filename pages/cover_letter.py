import streamlit as st
import asyncio
import logging
import time

from generators.cover_letter_generator import CoverLetterGenerator
from config.logger_config import setup_logger

logger = setup_logger(__name__, level=logging.INFO)

# print(st.session_state.resume, st.session_state.job_desc)

st.title("Cover Letter")

if "cover_letter_generator" not in st.session_state:
    st.session_state.cover_letter_generator = CoverLetterGenerator(st.session_state.resume, st.session_state.job_desc)


# Helper functions
async def get_cover_letter():
    cover_letter = await st.session_state.cover_letter_generator.generate_cover_letter()
    print(cover_letter)
    st.session_state.cover_letter = cover_letter


# Body
with st.spinner("Generating cover letter..."):
    start = time.time()
    asyncio.run(get_cover_letter())
    logger.info(f"Cover Letter Generation Time taken:{time.time()-start}")

st.text(f"{st.session_state.cover_letter}")

