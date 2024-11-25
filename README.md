# Cerebro - AI Conference Paper Search Engine 

<p align="center">
  <img src="assets/cerebro.jpg" alt="Cerebro Logo" width="400"/>
</p>

Cerebro is a modern, streamlined search engine for discovering and exploring papers from major AI/ML conferences and arXiv. Built with Streamlit, it provides real-time paper aggregation and efficient search capabilities.

## 🔧 Tech Stack

- **Backend**: Python, SQLite
- **Frontend**: Streamlit
- **Search**: SQLite FTS5 for full-text search
- **APIs**: arXiv API
- **Parsers**: BeautifulSoup4, XML ElementTree
- **Database**: SQLite with async background updates
- **Other Tools**: Make, Git

## ✨ Features & Improvements

### Conference Paper Search
- **Smart Database Management**: 
  - SQLite with FTS5 indexing for fast full-text search
  - Async background updates using SQLite WAL mode
  - Progress tracking for initial database population
  - Real-time paper count display

### arXiv Integration
- **Real-time arXiv Search**:
  - Direct integration with arXiv API
  - XML response parsing
  - Category-based filtering (CS.AI, CS.LG, CS.CL, CS.CV, etc.)
  - Pagination support for search results
  - Sorted by submission date (newest first)

### Enhanced UI/UX
- **Tabbed Interface**:
  - Separate tabs for conference and arXiv papers
  - Clean, responsive layout
  - Abstract preview in dialog windows
  - Paper metadata display

### Database Architecture
- **Efficient Schema**:
  - FTS5 virtual tables for fast search
  - Indexes on common query fields
  - Optimized for concurrent reads
  - Background write operations

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cerebro.git
cd cerebro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize and run:
```bash
make all    # Complete setup and launch
# OR
make init   # Just initialize database
make run    # Just run the application
```

## 💡 Usage

1. **Conference Papers**:
   - Search across indexed conference papers
   - Filter by venue and year
   - View abstracts and paper links

2. **arXiv Papers**:
   - Real-time search in arXiv database
   - Filter by CS categories
   - Navigate through paginated results
   - Latest papers first

## 🏗️ Architecture

```
cerebro/
├── app.py              # Main Streamlit application
├── config.py           # Configuration and constants
├── utils.py            # Helper functions
├── db/
│   └── paper_db.py     # SQLite database management
├── parsers/
│   ├── base.py         # Abstract parser class
│   ├── acl_parser.py   # ACL Anthology parser
│   ├── arxiv_parser.py # arXiv API parser
│   └── ml_parser.py    # ML conference parser
└── assets/            # Static files
```

### Key Components:
- **Database**: SQLite with FTS5 for full-text search
- **Web UI**: Streamlit for reactive interface
- **APIs**: arXiv API integration, ACL Anthology/Neurips/ICML/ICLR scraping
- **Background Tasks**: Async database updates
- **Search Engine**: SQLite FTS5 with ranking

## 🤝 Contributing

Contributions welcome! Feel free to submit a Pull Request.

## 📝 License

MIT License - see LICENSE file for details.