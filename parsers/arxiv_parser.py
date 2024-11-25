from datetime import datetime
import urllib.request
import xml.etree.ElementTree as ET
import streamlit as st
from .base import ConferencePaperParser


class ArXivParser(ConferencePaperParser):
    """Parser for arXiv papers using the arXiv API"""

    def fetch_papers(self, query: str, categories: list, start_idx: int = 0, max_results: int = 10) -> list:
        """Fetch papers from arXiv API based on query and categories"""
        if not categories or not query:
            return []

        cats = "+OR+".join(f"cat:{cat}" for cat in categories)
        url = f'http://export.arxiv.org/api/query?search_query=({cats})+AND+all:{query}&start={start_idx}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'

        try:
            with urllib.request.urlopen(url) as response:
                xml_content = response.read().decode('utf-8')
                return self._parse_response(xml_content)
        except Exception as e:
            st.error(f"Error fetching arXiv papers: {str(e)}")
            return []

    def _parse_response(self, xml_content: str) -> list:
        """Parse XML response from arXiv API"""
        root = ET.fromstring(xml_content)
        papers = []

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            published = entry.find(
                '{http://www.w3.org/2005/Atom}published').text
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
