import streamlit as st
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from db.paper_db import PaperDB
from config import VENUE_GROUPS
from utils import initialize_session_state, display_papers, view_abstract


def parse_arxiv_response(xml_content):
    root = ET.fromstring(xml_content)
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        date_obj = datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        paper = {
            'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
            'authors': ', '.join([author.find('{http://www.w3.org/2005/Atom}name').text
                                  for author in entry.findall('{http://www.w3.org/2005/Atom}author')]),
            'abstract': entry.find('{http://www.w3.org/2005/Atom}summary').text.strip(),
            'link': entry.find('{http://www.w3.org/2005/Atom}id').text,
            'submitted': formatted_date
        }
        papers.append(paper)
    return papers


def do_arxiv_search(query, categories, start_idx):
    if categories and query:
        cats = "+OR+".join(f"cat:{cat}" for cat in categories)
        url = f'http://export.arxiv.org/api/query?search_query=({cats})+AND+all:{query}&start={start_idx}&max_results=10&sortBy=submittedDate&sortOrder=descending'
        try:
            with urllib.request.urlopen(url) as response:
                xml_content = response.read().decode('utf-8')
                return parse_arxiv_response(xml_content)
        except Exception as e:
            st.error(f"Error fetching arXiv papers: {str(e)}")
            return []
    return []


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


def main():
    st.set_page_config(
        page_title="Cerebro - Search Engine for AI Conferences", page_icon="🧠", layout="centered")

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
                    st.session_state.db._init_search_index()
                progress_bar.empty()
                st.session_state.db.start_background_fetch()
                st.session_state.loaded = True
        loading.empty()

    initialize_session_state()

    if 'arxiv_start' not in st.session_state:
        st.session_state.arxiv_start = 0
    if 'arxiv_papers' not in st.session_state:
        st.session_state.arxiv_papers = []
    if 'arxiv_query_submitted' not in st.session_state:
        st.session_state.arxiv_query_submitted = False
    if 'current_arxiv_query' not in st.session_state:
        st.session_state.current_arxiv_query = ""
    if 'current_arxiv_categories' not in st.session_state:
        st.session_state.current_arxiv_categories = []

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("assets/cerebro.jpg", width=150)
    with col2:
        st.title("Cerebro AI Paper Search")

    if st.session_state.arxiv_query_submitted:
        st.session_state.arxiv_papers = do_arxiv_search(
            st.session_state.current_arxiv_query,
            st.session_state.current_arxiv_categories,
            st.session_state.arxiv_start
        )
        st.session_state.arxiv_query_submitted = False

    tabs = st.tabs(["Conference Papers", "arXiv Papers"])

    with tabs[0]:
        search_query = st.text_input("", placeholder=f"🔍 Search across {st.session_state.db.get_paper_count()} papers...",
                                     key="search_query", label_visibility="collapsed")

        all_venues = []
        for venues in VENUE_GROUPS.values():
            all_venues.extend(venues)

        col1, col2 = st.columns([1, 1])
        with col1:
            venue = st.selectbox(
                "Conference", ["All"] + all_venues, key="conf_venue")
        with col2:
            year = st.selectbox(
                "Year", ["All"] + list(range(2024, 2009, -1)), key="conf_year")

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

        display_papers()

    with tabs[1]:
        arxiv_query = st.text_input("Search arXiv papers", key="arxiv_query")
        categories = st.multiselect("Select Categories",
                                    ["cs.AI", "cs.LG", "cs.CL", "cs.CV"],
                                    default=["cs.AI"],
                                    key="category_select")

        if st.button("Search arXiv", type="primary", key="arxiv_search"):
            st.session_state.current_arxiv_query = arxiv_query
            st.session_state.current_arxiv_categories = categories
            st.session_state.arxiv_query_submitted = True
            st.rerun()

        display_arxiv_papers(st.session_state.arxiv_papers)

        if st.session_state.arxiv_papers:
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            with col1:
                if st.session_state.arxiv_start > 0:
                    if st.button("Previous", type="primary", key="prev_button"):
                        st.session_state.arxiv_start = max(
                            0, st.session_state.arxiv_start - 10)
                        st.session_state.arxiv_query_submitted = True
                        st.rerun()
            with col4:
                if st.button("Next", type="primary", key="next_button"):
                    st.session_state.arxiv_start += 10
                    st.session_state.arxiv_query_submitted = True
                    st.rerun()


if __name__ == "__main__":
    main()
