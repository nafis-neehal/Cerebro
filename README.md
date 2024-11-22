# Cerebro - AI Conference Paper Search Engine 🧠

Cerebro is a modern, streamlined search engine for discovering and exploring papers from major AI/ML conferences. Built with Streamlit, it provides real-time paper aggregation and search capabilities across venues like NeurIPS, ICML, ICLR, and the ACL Anthology.

![Cerebro Interface](https://via.placeholder.com/800x400)

## Features ✨

- **Real-time Paper Aggregation**: Fetches latest papers from major AI conferences
- **Smart Search**: Search papers by title with instant filtering
- **Conference Coverage**:
  - **ML Conferences**: NeurIPS, ICML, ICLR
  - **ACL Venues**: ACL, EMNLP, NAACL, EACL, CoNLL, and more
- **Paper Details**:
  - Title and authors
  - Conference venue and year
  - Direct links to papers
  - Paper abstracts with expandable view
- **Modern UI**:
  - Responsive grid layout
  - Clean card-based paper display
  - Pagination controls
  - Custom styling with smooth transitions

## Installation 🚀

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cerebro.git
cd cerebro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage 💡

1. Select a conference venue from the dropdown menu
2. Choose the desired year
3. Click "Get Papers" to fetch the papers
4. Use the search box to filter papers by title
5. Click "View Abstract" on any paper card to read its abstract
6. Navigate between pages using the Previous/Next buttons

## Architecture 🏗️

- `app.py`: Main Streamlit application with UI components
- `config.py`: Configuration constants and venue definitions
- `utils.py`: Helper functions for search and display
- `parsers/`:
  - `base.py`: Abstract base class for paper parsers
  - `acl_parser.py`: Parser for ACL Anthology papers
  - `ml_parser.py`: Parser for ML conference papers

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📝

This project is licensed under the MIT License - see the LICENSE file for details.
