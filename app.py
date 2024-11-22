# app.py

import streamlit as st
from db.paper_db import PaperDB
from config import VENUE_GROUPS, PAPERS_PER_PAGE
from utils import initialize_session_state, display_papers


def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
        <style>
        .stApp {
            background: #ffffff;
        }

        .main-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .stSelectbox [data-baseweb="select"] {
            background-color: white !important;
            border-radius: 8px !important;
            border: 1px solid #E5E7EB !important;
        }

        .stTextInput input {
            background-color: white !important;
            border-radius: 8px !important;
            border: 1px solid #E5E7EB !important;
            padding: 0.75rem 1rem !important;
        }

        .stButton>button {
            width: 100%;
            background-color: #4F46E5 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 0.75rem 1.5rem !important;
            border: none !important;
            font-weight: 500 !important;
            transition: background-color 0.2s;
        }

        .stButton>button:hover {
            background-color: #4338CA !important;
        }
                
        # Updated CSS for thinner cards:
        .paper-card {
        background: white;
        padding: 0.75rem 1rem;
        border-radius: 4px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05); 
        margin-bottom: 0.5rem;
        min-height: unset;
        display: flex;
        align-items: center;
        }

        .paper-content {
        flex: 1;
        display: flex;
        gap: 1rem;
        align-items: center;
        }

        .paper-title {
        flex: 2;
        font-size: 0.9rem;
        margin: 0;
        }

        .paper-authors {
        flex: 1;
        font-size: 0.8rem;
        margin: 0;
        }

        .paper-event {
        width: 120px;
        font-size: 0.8rem;
        margin: 0;
        }

        .paper-actions {
        width: 100px;
        }

        .stButton>button {
        padding: 0.25rem 0.5rem !important;
        font-size: 0.8rem !important;
        }

        
        .paper-title a:hover {
            text-decoration: underline;
        }

        [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
        [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button {
            width: 120px !important;
            margin: 0 auto !important;
            background: linear-gradient(to right, #EC4899, #F472B6) !important;
            padding: 0.5rem 1rem !important;
        }
        
        [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button:hover,
        [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button:hover {
            background: linear-gradient(to right, #DB2777, #EC4899) !important;
        }

        .stButton {
            margin-top: auto;
        }
                
        .stButton>button {
           background-color: #275F96 !important;
           color: white !important;
       }
       .pagination-button>button {
           background-color: #275F96 !important;
           color: white !important;
       }

        </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Cerebro - Search Engine for AI Conferences",
        page_icon="🧠",
        layout="centered"
    )

    if 'db' not in st.session_state:
        st.session_state.db = PaperDB()

    if 'loaded' not in st.session_state:
        loading = st.empty()
        with loading.container():
            with st.spinner("Checking database status..."):
                progress_bar = st.progress(0)
                needs_init = st.session_state.db.needs_initialization()

                if needs_init:
                    st.session_state.db.load_initial_papers(progress_bar)

                # Initialize search index after loading papers
                st.session_state.db._init_search_index()

                progress_bar.empty()
                st.session_state.db.start_background_fetch()
                st.session_state.loaded = True

        loading.empty()

    # Logo and title
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("cerebro.jpg", width=500)
    with col2:
        st.markdown("# Cerebro - Search Engine for AI Conferences")

    apply_custom_css()
    initialize_session_state()

    all_venues = []
    for venues in VENUE_GROUPS.values():
        all_venues.extend(venues)

    with st.container():
        search_query = st.text_input(
            "",
            placeholder=f"🔍 Search across {st.session_state.db.get_paper_count()} papers...",
            key="search_query",
            label_visibility="collapsed"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            venue = st.selectbox("Conference", ["All"] + all_venues)
        with col2:
            year = st.selectbox("Year", ["All"] + list(range(2024, 2009, -1)))

        if search_query:
            venue_filter = None if venue == "All" else venue
            year_filter = None if year == "All" else year
            try:
                results = st.session_state.db.search_papers(
                    search_query, venue_filter, year_filter)
                st.session_state.filtered_papers = results
            except Exception as e:
                st.error(f"Search error: {str(e)}")
                st.session_state.filtered_papers = []
        else:
            st.session_state.filtered_papers = []

        display_papers()


if __name__ == "__main__":
    main()
