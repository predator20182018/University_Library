from typing import List
from enum import Enum
import re
from .models import Book


class SearchType(Enum):
    ALL = "all"
    TITLE = "title"
    AUTHOR = "author"


class SearchEngine:
    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def prepare_search_terms(query: str) -> List[str]:
        normalized = SearchEngine.normalize_text(query)
        return [term for term in normalized.split() if term]

    @staticmethod
    def text_matches_query(text: str, search_terms: List[str]) -> bool:
        if not search_terms:
            return True
        normalized_text = SearchEngine.normalize_text(text)
        return all(term in normalized_text for term in search_terms)

    @staticmethod
    def search_books(books: List[Book], query: str,
                     show_available: bool = False,
                     show_borrowed: bool = False,
                     search_type: SearchType = SearchType.ALL) -> List[Book]:
        search_terms = SearchEngine.prepare_search_terms(query)
        filtered_books = []

        for book in books:
            if show_available and not book.available:
                continue
            if show_borrowed and book.available:
                continue

            matches = False
            if search_type == SearchType.ALL:
                matches = (SearchEngine.text_matches_query(book.title, search_terms) or
                           SearchEngine.text_matches_query(book.author, search_terms))
            elif search_type == SearchType.TITLE:
                matches = SearchEngine.text_matches_query(book.title, search_terms)
            elif search_type == SearchType.AUTHOR:
                matches = SearchEngine.text_matches_query(book.author, search_terms)

            if matches:
                filtered_books.append(book)

        return filtered_books