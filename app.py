import streamlit as st
import math
from parsers.acl_parser import ACLPaperParser
from parsers.ml_parser import MLConferencePaperParser
from config import VENUE_GROUPS, PAPERS_PER_PAGE
from utils import initialize_session_state, search_papers, get_parser_for_venue


def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
        <style>
        .stApp {
            background: #F3F4F6;
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

        .paper-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            min-height: 200px;  /* Fixed minimum height */
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .paper-content {
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
        }

        .paper-title {
            color: #111827;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            flex: 0 0 auto;
        }
        
        .paper-title a {
            color: #111827;
            text-decoration: none;
        }
        
        .paper-title a:hover {
            text-decoration: underline;
        }

        .paper-authors {
            color: #4B5563;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            flex: 1 1 auto;
        }

        .paper-event {
            color: #6B7280;
            font-size: 0.8rem;
            margin-bottom: 1rem;
            flex: 0 0 auto;
        }

        /* Make pagination buttons smaller and pink */
        [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
        [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button {
            width: 120px !important;  /* Make buttons smaller */
            margin: 0 auto !important;
            background: linear-gradient(to right, #EC4899, #F472B6) !important;
            padding: 0.5rem 1rem !important;  /* Smaller padding */
        }
        
        [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button:hover,
        [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button:hover {
            background: linear-gradient(to right, #DB2777, #EC4899) !important;
        }

        /* Fix button alignment in paper cards */
        .stButton {
            margin-top: auto;
        }
                
        </style>
    """, unsafe_allow_html=True)


def display_paper_card(paper):
    """Display a single paper card"""
    with st.container():
        st.markdown(f"""
            <div class="paper-card">
                <div class="paper-content">
                    <div class="paper-title"><a href={paper['paper_url']}> {paper['title']} </a></div>
                    <div class="paper-authors">{paper['authors']}</div>
                    <div class="paper-event">{paper['event']}</div>
                </div>
                <div class="paper-actions">
                </div>
            </div>
        """, unsafe_allow_html=True)

        if paper.get('abstract'):
            if st.button("View Abstract", key=paper['title']):
                view_abstract(paper)


@st.dialog("Abstract")
def view_abstract(item):
    st.write(item['abstract'])


def display_papers():
    """Display papers for current page with pagination"""
    papers_to_display = st.session_state.filtered_papers
    total_papers = len(papers_to_display)
    total_pages = math.ceil(total_papers / PAPERS_PER_PAGE)

    # Ensure current page is valid
    st.session_state.current_page = max(
        1, min(st.session_state.current_page, total_pages))

    # Calculate start and end indices
    start_idx = (st.session_state.current_page - 1) * PAPERS_PER_PAGE
    end_idx = min(start_idx + PAPERS_PER_PAGE, total_papers)

    # Display pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.current_page > 1:
            if st.button("◀️ Previous"):
                st.session_state.current_page -= 1
                st.rerun()

    with col2:
        st.markdown(f"""
            <div class="pagination-info">
                Page {st.session_state.current_page} of {total_pages}
            </div>
        """, unsafe_allow_html=True)

    with col3:
        if st.session_state.current_page < total_pages:
            if st.button("Next ▶️"):
                st.session_state.current_page += 1
                st.rerun()

    # Display papers
    if total_papers > 0:
        papers_for_page = papers_to_display[start_idx:end_idx]
        papers_per_row = 3

        for i in range(0, len(papers_for_page), papers_per_row):
            cols = st.columns(papers_per_row)
            for j, col in enumerate(cols):
                if i + j < len(papers_for_page):
                    with col:
                        display_paper_card(papers_for_page[i + j])
    else:
        st.write("No papers found.")


def main():
    st.set_page_config(
        page_title="Cerebro - Search Engine for AI Conferences",
        page_icon="🧠",
        layout="wide"
    )

    apply_custom_css()
    initialize_session_state()

    # Main container
    with st.container():
        st.markdown(
            '<div class="header"><h1>Cerebro - Search Engine for AI Conferences </h1></div>', unsafe_allow_html=True)

        # Single search box with icon
        st.text_input(
            "",
            placeholder="🔍 Search papers by title...",
            key="search_query",
            label_visibility="collapsed"
        )

        # Get all venues
        all_venues = []
        for venues in VENUE_GROUPS.values():
            all_venues.extend(venues)

        # Controls container
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            venue = st.selectbox("Conference", all_venues)
        with col2:
            year = st.selectbox("Year", range(2024, 2019, -1))
        with col3:
            # Spacing for alignment
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Get Papers", use_container_width=True):
                with st.spinner("Fetching papers..."):
                    parser = get_parser_for_venue(venue)
                    st.session_state.papers = parser.fetch_papers(venue, year)
                    st.session_state.filtered_papers = st.session_state.papers
                    st.session_state.current_page = 1

        # Display papers
        if st.session_state.papers:
            # Remove the explicit search_papers() call since we're using a single search box
            # Update filtered papers based on search query
            search_query = st.session_state.search_query
            if search_query:
                st.session_state.filtered_papers = [
                    paper for paper in st.session_state.papers
                    if search_query.lower() in paper['title'].lower()
                ]
            else:
                st.session_state.filtered_papers = st.session_state.papers

            display_papers()


if __name__ == "__main__":
    main()
