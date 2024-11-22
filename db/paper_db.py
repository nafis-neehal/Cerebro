# db.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import threading
from queue import Queue
import streamlit as st
from typing import List, Dict, Any


class PaperDB:
    def __init__(self):
        self.db_path = Path("papers.db")
        self.lock = threading.Lock()  # Add lock
        self._init_db()
        self._init_search_index()
        self.fetch_queue = Queue()
        self.fetch_thread = None

    def _init_db(self):
        """Initialize SQLite database with papers and search index tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    venue TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    paper_url TEXT,
                    abstract TEXT,
                    last_updated TIMESTAMP,
                    UNIQUE(title, venue, year)
                )
            ''')

            conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS papers_search 
                USING FTS5(title, abstract, authors, content='papers', content_rowid='id')
            ''')

            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS papers_ai AFTER INSERT ON papers BEGIN
                    INSERT INTO papers_search(rowid, title, abstract, authors)
                    VALUES (new.id, new.title, new.abstract, new.authors);
                END
            ''')

    def _init_search_index(self):
        with self.lock:  # Use lock
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT INTO papers_search(papers_search) VALUES("rebuild")')

    def start_background_fetch(self):
        """Start background thread for fetching papers"""
        if self.fetch_thread is None or not self.fetch_thread.is_alive():
            self.fetch_thread = threading.Thread(
                target=self._background_fetch_worker)
            self.fetch_thread.daemon = True
            self.fetch_thread.start()

    def _background_fetch_worker(self):
        """Worker thread that processes fetch requests"""
        while True:
            try:
                venue, year = self.fetch_queue.get()
                self._fetch_and_store_papers(venue, year)
                self.fetch_queue.task_done()
            except Exception as e:
                st.error(f"Error in background fetch: {str(e)}")

    def queue_fetch(self, venue: str, year: int):
        """Queue a venue/year combination for background fetching"""
        self.fetch_queue.put((venue, year))

    def _fetch_and_store_papers(self, venue: str, year: int):
        """Fetch papers and store in database"""
        from utils import get_parser_for_venue

        parser = get_parser_for_venue(venue)
        papers = parser.fetch_papers(venue, year)

        with self.lock:  # Use lock
            with sqlite3.connect(self.db_path) as conn:
                for paper in papers:
                    conn.execute('''
                        INSERT OR REPLACE INTO papers 
                        (title, authors, venue, year, paper_url, abstract, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        paper['title'],
                        paper['authors'],
                        paper['event'],
                        year,
                        paper.get('paper_url'),
                        paper.get('abstract', ''),
                        datetime.now().isoformat()
                    ))

    def search_papers(self, query: str, venue: str = None, year: int = None) -> List[Dict[str, Any]]:
        """Search papers using FTS index with optional venue/year filters"""
        with self.lock:  # Use lock
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                sql = '''
                    SELECT p.* 
                    FROM papers p
                    JOIN papers_search ps ON p.id = ps.rowid
                    WHERE papers_search MATCH ?
                '''
                params = [query]

                if venue:
                    sql += ' AND p.venue LIKE ?'
                    params.append(f'%{venue}%')

                if year:
                    sql += ' AND p.year = ?'
                    params.append(year)

                sql += ' ORDER BY rank'

                cursor = conn.execute(sql, params)
                return [dict(row) for row in cursor.fetchall()]
