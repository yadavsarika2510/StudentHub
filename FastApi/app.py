
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(
    page_title="StudentHub",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Remove unnecessary Streamlit spacing
st.markdown("""
<style>
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    iframe {
        width: 100% !important;
        border: none !important;
    }
    header, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

HTML_FILE = Path(__file__).parent / "studenthub.html"

if not HTML_FILE.exists():
    st.error("studenthub.html not found!")
    st.stop()

html = HTML_FILE.read_text(encoding="utf-8")

components.html(
    html,
    height=1200,
    scrolling=True
)
