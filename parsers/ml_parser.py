import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

from .base import ConferencePaperParser


class MLConferencePaperParser(ConferencePaperParser):
    """Parser for ML conferences (ICML, ICLR, NeurIPS)"""

    def __init__(self):
        self.conference_urls = {
            'NEURIPS': 'https://neurips.cc',
            'ICML': 'https://icml.cc',
            'ICLR': 'https://iclr.cc'
        }

        self.data_urls = {
            'NEURIPS': 'https://neurips.cc/static/virtual/data/neurips-{year}-orals-posters.json',
            'ICML': 'https://icml.cc/static/virtual/data/icml-{year}-orals-posters.json',
            'ICLR': 'https://iclr.cc/static/virtual/data/iclr-{year}-orals-posters.json'
        }

    def _get_data_url(self, venue: str, year: int) -> str:
        """Get the JSON data URL for the given venue and year"""
        base_url = self.data_urls.get(venue.upper())
        if not base_url:
            raise ValueError(f"Unsupported venue: {venue}")
        return base_url.format(year=year)

    def _construct_paper_url(self, venue: str, year: int, paper_id: str) -> str:
        """Construct the paper URL from its ID"""
        base_url = self.conference_urls.get(venue.upper())
        if not base_url:
            raise ValueError(f"Unsupported venue: {venue}")
        return f"{base_url}/virtual/{year}/poster/{paper_id}"

    def fetch_papers(self, venue: str, year: int) -> list:
        """
        Fetch papers from ML conferences using their JSON API
        Returns list of paper dictionaries with title, authors, paper_url, and abstract
        """
        try:
            # Get the JSON data
            url = self._get_data_url(venue, year)
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Process papers from results
            papers = []

            # Check if results exist in the JSON
            if 'results' not in data:
                st.error(f"No results found in JSON data from {url}")
                return papers

            for paper_data in data['results']:
                if paper_data:  # Skip empty entries
                    paper_info = self._extract_paper_info(
                        paper_data, venue, year)
                    if paper_info:
                        papers.append(paper_info)

            return papers

        except Exception as e:
            st.error(f"Error fetching papers: {str(e)}")
            print(f"Full error: {str(e)}")  # Detailed error for debugging
            return []

    def _extract_paper_info(self, paper_data: dict, venue: str, year: int) -> dict:
        """Extract relevant paper information from JSON data"""
        try:
            # Extract paper ID
            paper_id = str(paper_data.get('id'))

            # Get paper title (name in the JSON)
            title = paper_data.get('name', '').strip()
            if not title:  # Skip if no title
                return None

            # Get authors
            authors = []
            for author in paper_data.get('authors', []):
                if 'fullname' in author:
                    authors.append(author['fullname'])

            # Get abstract
            abstract = paper_data.get('abstract', '').strip()

            # Construct paper URL
            paper_url = self._construct_paper_url(venue, year, paper_id)

            return {
                'title': title,
                'authors': ', '.join(authors),
                'event': f"{venue}-{year}",
                'paper_url': paper_url,
                'abstract': abstract
            }

        except Exception as e:
            print(f"Error processing paper: {str(e)}")
            return None
