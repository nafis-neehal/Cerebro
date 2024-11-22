from abc import ABC, abstractmethod


class ConferencePaperParser(ABC):
    """Abstract base class for conference paper parsers"""

    @abstractmethod
    def fetch_papers(self, venue: str, year: int) -> list:
        """Fetch papers for a given venue and year"""
        pass
