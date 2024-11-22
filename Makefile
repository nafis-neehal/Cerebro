.PHONY: clean init run

clean:
	rm -f papers.db*

init: clean
	python3 -c "from db.paper_db import PaperDB; PaperDB()"

run:
	streamlit run app.py

all: clean init run