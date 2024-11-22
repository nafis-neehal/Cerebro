# db.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import threading
from queue import Queue
import streamlit as st
from typing import List, Dict, Any
from config import VENUE_GROUPS


class PaperDB:

    def __init__(self):
        self.db_path = Path("papers.db")
        self._init_db()
        self.fetch_queue = Queue()
        self.fetch_thread = None

    def _init_db(self):
        conn = self._get_connection()
        try:
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
                CREATE TABLE IF NOT EXISTS initialization_status (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    initialized BOOLEAN NOT NULL,
                    last_updated TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS papers_search 
                USING FTS5(title, abstract, authors, content='papers', content_rowid='id')
            ''')
            conn.commit()
        finally:
            conn.close()

    def needs_initialization(self):
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                'SELECT initialized FROM initialization_status WHERE id = 1')
            result = cursor.fetchone()
            return result is None or not result[0]
        finally:
            conn.close()

    def mark_initialized(self):
        conn = self._get_connection()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO initialization_status (id, initialized, last_updated)
                VALUES (1, TRUE, ?)
            ''', (datetime.now().isoformat(),))
            conn.commit()
        finally:
            conn.close()

    def load_initial_papers(self, progress_bar):
        if not self.needs_initialization():
            return False

        all_venues = []
        for venues in VENUE_GROUPS.values():
            all_venues.extend(venues)

        total_combinations = len(all_venues) * len(range(2010, 2025))
        loaded = 0

        for venue in all_venues:
            for year in range(2010, 2025):
                self._fetch_and_store_papers(venue, year)
                loaded += 1
                progress_bar.progress(loaded / total_combinations,
                                      f"Loading papers from ({loaded}/{total_combinations}) venues and years")

        self.mark_initialized()
        return True

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _init_search_index(self):
        conn = self._get_connection()
        try:
            conn.execute(
                'INSERT INTO papers_search(papers_search) VALUES("rebuild")')
            conn.commit()
        finally:
            conn.close()

    def start_background_fetch(self):
        if self.fetch_thread is None or not self.fetch_thread.is_alive():
            self.fetch_thread = threading.Thread(
                target=self._background_fetch_worker)
            self.fetch_thread.daemon = True
            self.fetch_thread.start()

    def _background_fetch_worker(self):
        while True:
            try:
                venue, year = self.fetch_queue.get()
                self._fetch_and_store_papers(venue, year)
                self.fetch_queue.task_done()
            except Exception as e:
                st.error(f"Error in background fetch: {str(e)}")

    def queue_fetch(self, venue: str, year: int):
        self.fetch_queue.put((venue, year))

    def _fetch_and_store_papers(self, venue: str, year: int):
        from utils import get_parser_for_venue
        parser = get_parser_for_venue(venue)
        papers = parser.fetch_papers(venue, year)

        conn = self._get_connection()
        try:
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
            conn.commit()
        finally:
            conn.close()

    # def search_papers(self, query: str, venue: str = None, year: int = None) -> List[Dict[str, Any]]:
    #     conn = self._get_connection()
    #     # replace hyphens with spaces for search
    #     query = query.replace('-', ' ')
    #     try:
    #         conn.row_factory = sqlite3.Row
    #         sql = '''
    #             SELECT p.*
    #             FROM papers p
    #             JOIN papers_search ps ON p.id = ps.rowid
    #             WHERE papers_search MATCH ?
    #         '''
    #         params = [query]

    #         if venue and venue != "All":
    #             sql += ' AND p.venue LIKE ?'
    #             params.append(f'%{venue}%')

    #         if year and year != "All":
    #             sql += ' AND p.year = ?'
    #             params.append(year)

    #         sql += ' ORDER BY rank'

    #         cursor = conn.execute(sql, params)
    #         return [dict(row) for row in cursor.fetchall()]
    #     finally:
    #         conn.close()

    def search_papers(self, query: str, venue: str = None, year: int = None) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        # Replace hyphens with spaces for search
        query = query.replace('-', ' ')
        try:
            conn.row_factory = sqlite3.Row
            sql = '''
                SELECT p.* 
                FROM papers p
                JOIN papers_search ps ON p.id = ps.rowid
                WHERE papers_search MATCH ?
            '''
            params = [query]

            if venue and venue != "All":
                sql += ' AND p.venue LIKE ?'
                params.append(f'{venue}-%')  # Matches "ACL-" at the start

            if year and year != "All":
                sql += ' AND p.year = ?'
                params.append(year)

            sql += ' ORDER BY rank'

            cursor = conn.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_paper_count(self):
        """Get total papers in database"""
        conn = self._get_connection()
        try:
            cursor = conn.execute('SELECT COUNT(*) FROM papers')
            return cursor.fetchone()[0]
        finally:
            conn.close()
