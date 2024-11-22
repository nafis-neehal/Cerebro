import streamlit as st
import math
from config import PAPERS_PER_PAGE
from config import VENUE_GROUPS
from parsers.acl_parser import ACLPaperParser
from parsers.ml_parser import MLConferencePaperParser


def initialize_session_state():
    """Initialize session state variables"""
    if 'papers' not in st.session_state:
        st.session_state.papers = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'filtered_papers' not in st.session_state:
        st.session_state.filtered_papers = []


def search_papers():
    """Filter papers based on search query"""
    search_query = st.text_input("Search papers by title",
                                 value=st.session_state.search_query,
                                 key="search_box")

    if search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
        st.session_state.current_page = 1

    if search_query:
        st.session_state.filtered_papers = [
            paper for paper in st.session_state.papers
            if search_query.lower() in paper['title'].lower()
        ]
    else:
        st.session_state.filtered_papers = st.session_state.papers


def get_paper_link(paper):
    """Get paper link handling both ACL and ML conference formats"""
    # Check ML conference format first
    if 'paper_url' in paper and paper['paper_url']:
        return paper['paper_url']
    # Check ACL format
    if 'pdf_link' in paper and paper['pdf_link']:
        return paper['pdf_link']
    return None


def display_paper_card(paper):
    """Display a single paper card"""
    st.markdown(f"### {paper['title']}")
    st.write(f"**Authors:** {paper['authors']}")
    st.write(f"**Event:** {paper['event']}")

    col1, col2 = st.columns([1, 3])
    with col1:
        if paper.get('paper_url'):  # Using dict.get() for cleaner access
            st.markdown(f"[📄 Paper]({paper['paper_url']})")
    with col2:
        if paper.get('abstract'):  # Using dict.get() for cleaner access
            with st.expander("📝 Abstract"):
                st.write(paper['abstract'])
    st.markdown("---")


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
        st.write(f"Page {st.session_state.current_page} of {total_pages}")

    with col3:
        if st.session_state.current_page < total_pages:
            if st.button("Next ▶️"):
                st.session_state.current_page += 1
                st.rerun()

    # Display papers
    if total_papers > 0:
        for paper in papers_to_display[start_idx:end_idx]:
            display_paper_card(paper)
    else:
        st.write("No papers found.")


def get_parser_for_venue(venue):
    """Return appropriate parser based on venue"""
    if venue in VENUE_GROUPS["ACL"]:
        return ACLPaperParser()
    elif venue in VENUE_GROUPS["ML"]:
        return MLConferencePaperParser()
    else:
        raise ValueError(f"No parser found for venue: {venue}")
