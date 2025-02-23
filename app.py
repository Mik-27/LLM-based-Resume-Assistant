import streamlit as st
import time
import math
import asyncio
import logging

from generators.resume_reviewer import ResumeReviewer
from config.logger_config import setup_logger

logger = setup_logger(__name__, level=logging.INFO)

# resume_page = st.Page("pages/tailor_resume.py", title="Tailor Resume", icon=":material/add_circle:")
# cover_letter_page = st.Page("pages/cover_letter.py", title="Cover Letter", icon=":material/delete:")

# pg = st.navigation([resume_page])
# st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
# pg.run()

st.set_page_config(page_title="Resume Parser", page_icon=":page_facing_up:", layout="wide")
    

# Setting up session state variables
if "layout" not in st.session_state:
    st.session_state.layout = "layout1" # Page layout

if "parsed_result" not in st.session_state:
    st.session_state.parsed_result = None # Keywords

if "resume" not in st.session_state:
    st.session_state.resume = None # Keywords

if "job_desc" not in st.session_state:
    st.session_state.job_desc = None # Keywords

if "score" not in st.session_state:
    st.session_state.score = None # Relevance score

if "resume_reviewer" not in st.session_state:
    st.session_state.resume_reviewer = None # ResumeReviewer object

if "keywords" not in st.session_state:
    st.session_state.keywords = None # Matching and Non-matching Keywords

if "strengths" not in st.session_state:
    st.session_state.strengths = None # Strengths

if "weaknesses" not in st.session_state:
    st.session_state.weaknesses = None # Weaknesses


def rel_score_color(score):
    if score > 80:
        return "#3CB371"
    elif score > 60:
        return "yellow"
    else:
        return "red"


async def get_rs(rr):
    """Function to get relevance score"""
    try:
        score = await rr.generate_relevancy_score()
        if score != -1:
            st.session_state.score = int(score * 100)
        else:
            st.session_state.score = -1
            st.error("Failed to generate relevance score.")
        return score
    except Exception as e:
        logger.error(f"Error in generating relevance score: {str(e)}")
        st.error("Error in generating relevance score. Please try again.")
        st.session_state.score = -1
        

async def get_keywords(rr):
    """Function to get matching and non-matching keywords"""
    try:
        keywords = await rr.extract_keywords(source="match")
        logger.debug(f"Keywords: {keywords}")
        matching_keywords = keywords['matching_keywords']
        non_matching_keywords = keywords['non_matching_keywords']
        
        st.session_state.matching_keywords = matching_keywords
        st.session_state.non_matching_keywords = non_matching_keywords
        
        st.session_state.keywords = [st.session_state.matching_keywords, st.session_state.non_matching_keywords]
        return st.session_state.matching_keywords, st.session_state.non_matching_keywords
    
    except Exception as e:
        logger.error(f"Error in extracting keywords: {str(e)}")
        st.error("Error in extracting keywords. Please try again.")


async def get_sw(rr):
    """Function to get strengths and weaknesses"""
    try:
        strengths = await rr.get_strengths()
        weaknesses = await rr.get_weaknesses()

        st.session_state.strengths = strengths
        st.session_state.weaknesses = weaknesses
        return strengths, weaknesses
    except Exception as e:
        logger.error(f"Error in extracting strengths and weaknesses: {str(e)}")
        st.error("Error in extracting strengths and weaknesses. Please try again.")

# Switch page layout after parsing resume for first time.
async def switch_layout():
    # Change layout
    if st.session_state.layout == "layout1":
        st.session_state.layout = "layout2"
    else:
        st.session_state.layout = "layout2"

    # Error handling for resume and job description inputs
    start = time.time()
    if not file_upload and not job_text:
        st.error("Please upload a resume and enter job description.")
        return
    elif not file_upload:
        st.error("Please upload a resume.")
        return
    elif not job_text:
        st.error("Please enter job description.")

    st.session_state.clicked = True
    # if not st.session_state.resume:
    st.session_state.resume = file_upload
    # if not st.session_state.job_desc:
    st.session_state.job_desc = job_text
    st.session_state.cover_letter = None

    # Initialize ResumeReviewer object if not initialized
    if not st.session_state.resume_reviewer:
        st.session_state.resume_reviewer = ResumeReviewer(st.session_state.resume, st.session_state.job_desc)
    rr = st.session_state.resume_reviewer
    
    with st.spinner('Parsing...'):
        await asyncio.gather(get_rs(rr), get_keywords(rr), get_sw(rr))

    st.success('Parsing complete!')
    
    # Time to parse resume and generate outputs
    logger.info(f"Resume Parsing Time taken:{time.time()-start}")


def button_click_helper():
    asyncio.run(switch_layout())


# Page Layouts
if st.session_state.layout == "layout1":
    upload_toggle = st.toggle("Upload resume")
    if upload_toggle:
        file_upload = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    else:
        file_upload = st.text_area("Paste resume", placeholder="Paste resume here...", height=200, on_change=lambda: st.session_state.__setitem__('resume', file_upload))

    job_text = st.text_area("Enter the job description", placeholder="Enter job description here...", height=350, on_change=lambda: st.session_state.__setitem__('job_desc', job_text))

    st.button("Parse", use_container_width=True, on_click=button_click_helper)

else:
    col1, col2 = st.columns([5,5], gap="large")
    with col1:
        upload_toggle = st.toggle("Upload resume")
        if upload_toggle:
            file_upload = st.file_uploader("Upload your resume", type=["pdf", "docx"])
        else:
            file_upload = st.text_area("Paste resume", placeholder="Paste resume here...", height=200, value=st.session_state.resume)

        job_text = st.text_area("Enter the job description", placeholder="Enter job description here...", height=350, value=st.session_state.job_desc)

        st.button("Parse", use_container_width=True, on_click=button_click_helper)

        if st.button("Tailor Resume", use_container_width=True):
            st.switch_page("pages/tailor_resume.py")

        if st.button("Generate Cover Letter", use_container_width=True):
            st.switch_page("pages/cover_letter.py")

    with col2:
        keyword_tab, strength_tab, weakness_tab = st.tabs(["Keywords", "Strengths", "Weaknesses"])
        with keyword_tab:
            # HTML styling
            st.markdown(
                f"""
                <style>
                .rel-score h1{{
                    font-size:50px !important;
                    color: {rel_score_color(st.session_state.score)};
                    margin-top: 0;
                    padding-top: 0;
                    margin-bottom: 20px;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                    f"""
                    <div class="rel-score">
                        <h3>Relevancy Score:</h3>
                        <h1>{st.session_state.score}</h1>
                    </div>""",
                    unsafe_allow_html=True
                )

            if st.session_state.keywords[0]:
                st.markdown(
                    f"<h5>✅ Matching Keywords:</h5>",
                    unsafe_allow_html=True
                )

                matching_keywords_per_col = math.ceil(len(st.session_state.keywords[0]) / 3)
                mk_col1, mk_col2, mk_col3 = st.columns(3)
                with mk_col1:
                    for keyword in st.session_state.keywords[0][:matching_keywords_per_col]:
                        st.markdown(
                            f"<p style='color: #3CB371;'>{keyword}</p>",
                            unsafe_allow_html=True
                        )

                with mk_col2:
                    for keyword in st.session_state.keywords[0][matching_keywords_per_col:matching_keywords_per_col*2]:
                        st.markdown(
                            f"<p style='color: #3CB371;'>{keyword}</p>",
                            unsafe_allow_html=True
                        )

                with mk_col3:
                    for keyword in st.session_state.keywords[0][matching_keywords_per_col*2:]:
                        st.markdown(
                            f"<p style='color: #3CB371;'>{keyword}</p>",
                            unsafe_allow_html=True
                        )

            if st.session_state.keywords[1]:
                st.markdown(
                    f"<h5>❌ Non-Matching Keywords:</h5>",
                    unsafe_allow_html=True
                )
                
                non_matching_keywords_per_col = math.ceil(len(st.session_state.keywords[1]) / 3)
                nmk_col1, nmk_col2, nmk_col3 = st.columns(3)
                with nmk_col1:
                    for keyword in st.session_state.keywords[1][:non_matching_keywords_per_col]:
                        st.markdown(
                            f"<p style='color: red;'>{keyword}</p>",
                            unsafe_allow_html=True
                        )

                with nmk_col2:
                    for keyword in st.session_state.keywords[1][non_matching_keywords_per_col:non_matching_keywords_per_col*2]:
                        st.markdown(
                            f"<p style='color: red;'>{keyword}</p>",
                            unsafe_allow_html=True
                        )

                with nmk_col3:
                    for keyword in st.session_state.keywords[1][non_matching_keywords_per_col*2:]:
                        st.markdown(
                            f"<p style='color: red;'>{keyword}</p>",
                            unsafe_allow_html=True
                        )

        with strength_tab:
            if st.session_state.strengths:
                
                for strength in st.session_state.strengths:
                    st.markdown(
                        f"<h6>{strength['title']}</h6>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<p>{strength['strength']}</p>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<hr>",
                        unsafe_allow_html=True
                    )

        with weakness_tab:
            if st.session_state.weaknesses:    
                for weakness in st.session_state.weaknesses:
                    st.markdown(
                        f"<h6>{weakness['title']}</h6>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<p>{weakness['problem']}</p>",
                        unsafe_allow_html=True
                    )
                    
                    improvements_html = "<ul>"
                    for sol in weakness['improvement']:
                        improvements_html += f"<li><em>{sol['suggested_improvement']}</em></li>"
                    improvements_html += "</ul>"
                    
                    st.markdown(
                        improvements_html,
                        unsafe_allow_html=True
                    )
                    
                    st.markdown(
                        f"<hr>",
                        unsafe_allow_html=True
                    )