import streamlit as st
import time
import math
import asyncio

from generators.resume_reviewer import ResumeReviewer

resume_page = st.Page("pages/parse_resume.py", title="Parse Resume", icon=":material/add_circle:")
# delete_page = st.Page("delete.py", title="Delete entry", icon=":material/delete:")

pg = st.navigation([resume_page])
# st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()

st.set_page_config(page_title="Resume Parser", page_icon=":page_facing_up:", layout="wide")


# HACK: Implement tabs for [Keywords, strengths, weaknesses]

# Setting up session state variables
if "layout" not in st.session_state:
    st.session_state.layout = "layout1" # Page layout

if "parsed_result" not in st.session_state:
    st.session_state.parsed_result = None # Keywords

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
    score = await rr.generate_relevancy_score()
    st.session_state.score = int(score)*100
    return score

async def get_keywords(rr):
    """Function to get matching and non-matching keywords"""
    resume_keywords = await rr.extract_keywords("resume")
    job_keywords = await rr.extract_keywords("job")

    # TODO: Update to handle low and high proirity keywords separately
    resume_keywords = resume_keywords['keywords']
    job_keywords = job_keywords['high_priority']+job_keywords['low_priority']
    print(resume_keywords, job_keywords)

    matching_keywords = list(set(resume_keywords) & set(job_keywords))
    non_matching_keywords = list(set(job_keywords) - set(resume_keywords))
    print(matching_keywords, non_matching_keywords)

    st.session_state.keywords = [matching_keywords, non_matching_keywords]
    return matching_keywords, non_matching_keywords

async def get_sw(rr):
    """Function to get strengths and weaknesses"""
    strengths = await rr.get_strengths()
    weaknesses = await rr.get_weaknesses()
    print(strengths, weaknesses)

    st.session_state.strengths = strengths
    st.session_state.weaknesses = weaknesses
    return strengths, weaknesses


# Switch page layout after parsing resume for first time.
async def switch_layout():
    # Error handling for resume and job description inputs
    if not file_upload and not job_text:
        st.error("Please upload a resume and enter job description.")
        return
    elif not file_upload:
        st.error("Please upload a resume.")
        return
    elif not job_text:
        st.error("Please enter job description.")

    st.session_state.clicked = True

    # Initialize ResumeReviewer object if not initialized
    st.session_state.resume_reviewer = ResumeReviewer(file_upload, job_text)
    rr = st.session_state.resume_reviewer
    
    # FIXME: Awaiting 3 function calls increases overall response time
    with st.spinner('Parsing...'):
        await get_rs(rr)
        await get_keywords(rr)
        await get_sw(rr)

    st.success('Parsing complete!')
    if st.session_state.layout == "layout1":
        st.session_state.layout = "layout2"


# Page Layouts
if st.session_state.layout == "layout1":
    upload_toggle = st.toggle("Upload resume")
    if upload_toggle:
        file_upload = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    else:
        file_upload = st.text_area("Paste resume", placeholder="Paste resume here...", height=200)

    job_text = st.text_area("Enter the job description", placeholder="Enter job description here...", height=350)

    if st.button("Parse", use_container_width=True):
        # print("here")
        asyncio.run(switch_layout())

else:
    col1, col2 = st.columns([3,2], gap="large")
    with col1:
        upload_toggle = st.toggle("Upload resume")
        if upload_toggle:
            file_upload = st.file_uploader("Upload your resume", type=["pdf", "docx"])
        else:
            file_upload = st.text_area("Paste resume", placeholder="Paste resume here...", height=200)

        job_text = st.text_area("Enter the job description", placeholder="Enter job description here...", height=350)

        if st.button("Parse", use_container_width=True):
            asyncio.run(switch_layout())

    with col2:
        # HTML styling
        st.markdown(
            f"""
            <style>
            .rel-score h1{{
                font-size:50px !important;
                color: {rel_score_color(st.session_state.score)};
                margin-top: 0;
                padding-top: 0;
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

        st.markdown(
                f"<h3>Keywords:</h3>",
                unsafe_allow_html=True
            )

        # Temporary placeholder for matching and non-matching keywords
        # ------------------------------------------------------------------
        matching_keywords = ["apple", "kiwi", "banana", "cherry", "mango"]
        non_matching_keywords = ["orange", "grape", "pear", "plum", "peach"]
        # ------------------------------------------------------------------
        
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
        
        if st.session_state.strengths:
            st.markdown(
                    f"<h3>Strengths:</h3>",
                    unsafe_allow_html=True
                )
            
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
                    f"<p><em>{strength['importance']}</em></p>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<hr>",
                    unsafe_allow_html=True
                )
        
        if st.session_state.weaknesses:
            st.markdown(
                    f"<h3>Weaknesses:</h3>",
                    unsafe_allow_html=True
                )
            
            for weakness in st.session_state.weaknesses:
                st.markdown(
                    f"<h6>{weakness['title']}</h6>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<p>{weakness['problem']}</p>",
                    unsafe_allow_html=True
                )
                for sol in weakness['improvement']:
                    st.markdown(
                        f"<p><em>{sol['suggested_improvement']}</em></p>",
                        unsafe_allow_html=True
                    )
                st.markdown(
                    f"<hr>",
                    unsafe_allow_html=True
                )