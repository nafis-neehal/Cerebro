# Configuration constants
PAPERS_PER_PAGE = 10

# All ACL venues
ACL_VENUES = [
    "ACL", "AACL", "ANLP", "CL", "CoNLL", "EACL", "EMNLP", "Findings",
    "IWSLT", "NAACL", "SemEval", "(Star)*SEM", "TACL", "WMT", "WS"
]

# ML Conference venues
ML_VENUES = ["NEURIPS", "ICML", "ICLR"]

# All venues grouped by parser type
VENUE_GROUPS = {
    "ACL": ACL_VENUES,
    "ML": ML_VENUES
}
