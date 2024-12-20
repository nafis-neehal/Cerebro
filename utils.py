import streamlit as st
import math
from config import PAPERS_PER_PAGE
from config import VENUE_GROUPS
from parsers.acl_parser import ACLPaperParser
from parsers.ml_parser import MLConferencePaperParser
from typing import List, Dict, Any


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
    if 'current_arxiv_query' not in st.session_state:
        st.session_state.current_arxiv_query = ""
    if 'current_arxiv_categories' not in st.session_state:
        st.session_state.current_arxiv_categories = []


def search_papers(self, query: str, venue: str = None, year: int = None) -> List[Dict[str, Any]]:
    conn = self._get_connection()
    try:
        conn.row_factory = sqlite3.Row
        sql = '''
            SELECT p.id, p.title, p.authors, p.venue, p.year, p.paper_url, p.abstract 
            FROM papers p
            JOIN papers_search ps ON p.id = ps.rowid
            WHERE papers_search MATCH ?
        '''
        params = [query]

        if venue and venue != "All":
            sql += ' AND p.venue LIKE ?'
            params.append(f'%{venue}%')

        if year and year != "All":
            sql += ' AND p.year = ?'
            params.append(year)

        sql += ' ORDER BY rank'

        cursor = conn.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    finally:
        conn.close()


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
    with st.container():
        st.markdown(f"""
           <div class="paper-card">
               <div class="paper-content">
                   <div class="paper-title">
                       <a href="{paper['paper_url']}">{paper['title']}</a>
                   </div>
                   <div class="paper-authors">{paper['authors']}</div>
                   <div class="paper-event">{paper['venue']} {paper['year']}</div>
               </div>
           </div>
       """, unsafe_allow_html=True)

        if paper.get('abstract'):
            if st.button("View Abstract", key=f"{paper['id']}_{paper['year']}"):
                view_abstract(paper)


@st.dialog("Abstract")
def view_abstract(item):
    st.write(item['abstract'])


def display_papers():
    papers_to_display = st.session_state.filtered_papers
    total_papers = len(papers_to_display)

    if total_papers > 0:
        total_pages = math.ceil(total_papers / PAPERS_PER_PAGE)
        start_idx = (st.session_state.current_page - 1) * PAPERS_PER_PAGE
        end_idx = min(start_idx + PAPERS_PER_PAGE, total_papers)

        # Create table headers
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.markdown("**Title**")
        with col2:
            st.markdown("**Authors**")
        with col3:
            st.markdown("**Venue**")
        with col4:
            st.markdown("**Abstract**")

        # Create table rows
        for paper in papers_to_display[start_idx:end_idx]:
            col1, col2, col3, col4 = st.columns([3, 2, 1.5, 1])
            with col1:
                st.markdown(f"[{paper['title']}]({paper['paper_url']})")
            with col2:
                st.markdown(f"{paper['authors']}")
            with col3:
                st.markdown(f"{paper['venue']}")
            with col4:
                if paper.get('abstract'):
                    if st.button("View", key=f"abstract_{paper['id']}"):
                        view_abstract(paper)

        # Pagination
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            if st.session_state.current_page > 1:
                if st.button("Previous", type="primary"):
                    st.session_state.current_page -= 1
                    st.rerun()
        # with col3:
        #     st.write(f"Page {st.session_state.current_page} of {total_pages}")
        with col4:
            if st.session_state.current_page < total_pages:
                if st.button("Next", type="primary"):
                    st.session_state.current_page += 1
                    st.rerun()


def get_parser_for_venue(venue):
    """Return appropriate parser based on venue"""
    if venue in VENUE_GROUPS["ACL"]:
        return ACLPaperParser()
    elif venue in VENUE_GROUPS["ML"]:
        return MLConferencePaperParser()
    else:
        raise ValueError(f"No parser found for venue: {venue}")


def display_arxiv_papers(papers):
    if not papers:
        return

    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
    with col1:
        st.markdown("**Title**")
    with col2:
        st.markdown("**Authors**")
    with col3:
        st.markdown("**Date**")
    with col4:
        st.markdown("**Abstract**")

    for paper in papers:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        with col1:
            st.markdown(f"[{paper['title']}]({paper['link']})")
        with col2:
            st.markdown(f"{paper['authors']}")
        with col3:
            st.markdown(f"{paper['submitted']}")
        with col4:
            if st.button("View", key=f"abstract_{paper['link']}"):
                view_abstract(paper)
