import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

from .base import ConferencePaperParser


class ACLPaperParser(ConferencePaperParser):
    """Parser for ACL Anthology papers"""

    def __init__(self):
        self.base_url = "https://aclanthology.org"

    def _sanitize_venue_name(self, venue: str) -> str:
        """
        Sanitize venue name for URL construction
        - Removes special characters
        - Converts to lowercase
        - Handles special cases like *SEM
        """
        # Special cases
        if venue.lower() == "*sem":
            return "sem"

        # Remove special characters and convert to lowercase
        sanitized = re.sub(r'[^a-zA-Z0-9]', '', venue).lower()
        return sanitized

    def fetch_papers(self, venue: str, year: int) -> list:
        """
        Fetch papers from ACL Anthology
        Returns list of paper dictionaries with title, authors, paper_url, and abstract
        """
        sanitized_venue = self._sanitize_venue_name(venue)
        url = f"{self.base_url}/events/{sanitized_venue}-{year}/"

        try:
            response = requests.get(url)
            response.raise_for_status()
            return self._parse_papers(response.text, venue, year)
        except Exception as e:
            st.error(f"Error fetching papers: {str(e)}")
            return []

    def _parse_papers(self, html_content: str, venue: str, year: int) -> list:
        """Parse paper information from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        papers = []

        for paper in soup.find_all('p', class_='d-sm-flex'):
            paper_info = self._extract_paper_info(paper, venue, year)
            if paper_info:
                papers.append(paper_info)

        return papers

    def _extract_paper_info(self, paper_elem, venue: str, year: int) -> dict:
        """Extract information for a single paper"""
        # Get paper URL (formerly pdf_link)
        paper_url = None
        pdf_badge = paper_elem.find('a', class_='badge-primary')
        if pdf_badge and 'pdf' in pdf_badge.text.lower():
            paper_url = urljoin(self.base_url, pdf_badge['href'])

        # Get title
        title_elem = paper_elem.find('strong').find('a', class_='align-middle')
        if not title_elem:
            return None

        # Get authors
        author_spans = paper_elem.find_all(
            'a', href=lambda x: x and x.startswith('/people/'))
        authors = [author.text.strip() for author in author_spans]

        # Get abstract
        abstract = ""
        abstract_div = paper_elem.find_next('div', class_='abstract-collapse')
        if abstract_div:
            abstract_body = abstract_div.find('div', class_='card-body')
            if abstract_body:
                abstract = abstract_body.text.strip()

        return {
            'title': title_elem.text.strip(),
            'authors': ', '.join(authors),
            'event': f"{venue}-{year}",
            'paper_url': paper_url,  # Changed from pdf_link to paper_url
            'abstract': abstract
        }
