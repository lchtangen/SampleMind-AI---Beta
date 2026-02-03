"""
Advanced Search and Filter Engine for SampleMind TUI
Support for complex queries with filters and fuzzy matching
"""

import re
import logging
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FilterOperator(Enum):
    """Filter operators"""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


@dataclass
class SearchFilter:
    """Individual search filter"""
    field: str
    operator: FilterOperator
    value: Any
    match_type: str = "and"  # "and" or "or"

    def matches(self, value: Any) -> bool:
        """Check if value matches this filter"""
        if value is None:
            return False

        if self.operator == FilterOperator.EQUALS:
            return value == self.value
        elif self.operator == FilterOperator.NOT_EQUALS:
            return value != self.value
        elif self.operator == FilterOperator.GREATER_THAN:
            return value > self.value
        elif self.operator == FilterOperator.LESS_THAN:
            return value < self.value
        elif self.operator == FilterOperator.GREATER_EQUAL:
            return value >= self.value
        elif self.operator == FilterOperator.LESS_EQUAL:
            return value <= self.value
        elif self.operator == FilterOperator.CONTAINS:
            return str(self.value).lower() in str(value).lower()
        elif self.operator == FilterOperator.NOT_CONTAINS:
            return str(self.value).lower() not in str(value).lower()
        elif self.operator == FilterOperator.IN:
            return value in self.value
        elif self.operator == FilterOperator.NOT_IN:
            return value not in self.value

        return False


class SearchQuery:
    """Parsed search query"""

    def __init__(self, query_string: str = "") -> None:
        """Initialize search query from string"""
        self.query_string = query_string
        self.filters: List[SearchFilter] = []
        self.text_search: Optional[str] = None
        self.fuzzy_enabled = False

        if query_string:
            self._parse_query(query_string)

    def _parse_query(self, query: str) -> None:
        """Parse query string into filters"""
        # Extract filters (e.g., tempo:120-130, key:C, duration:<5)
        filter_pattern = r"(\w+):([\w\-><!=,]+)"
        matches = re.findall(filter_pattern, query)

        for field, value_str in matches:
            self._parse_filter(field, value_str)

        # Extract text search (remaining text without filters)
        remaining = re.sub(filter_pattern, "", query).strip()
        if remaining:
            self.text_search = remaining

    def _parse_filter(self, field: str, value_str: str) -> None:
        """Parse a single filter"""
        # Handle range filters (e.g., 120-130)
        if "-" in value_str and field in ["tempo", "duration"]:
            parts = value_str.split("-")
            if len(parts) == 2:
                try:
                    min_val = float(parts[0])
                    max_val = float(parts[1])

                    self.filters.append(
                        SearchFilter(field, FilterOperator.GREATER_EQUAL, min_val)
                    )
                    self.filters.append(
                        SearchFilter(field, FilterOperator.LESS_EQUAL, max_val)
                    )
                    return
                except ValueError:
                    pass

        # Handle comparison operators (>, <, >=, <=)
        for op_str, op_enum in [
            (">=", FilterOperator.GREATER_EQUAL),
            ("<=", FilterOperator.LESS_EQUAL),
            (">", FilterOperator.GREATER_THAN),
            ("<", FilterOperator.LESS_THAN),
            ("!=", FilterOperator.NOT_EQUALS),
            ("=", FilterOperator.EQUALS),
        ]:
            if value_str.startswith(op_str):
                value = value_str[len(op_str) :]
                try:
                    value = float(value)
                except ValueError:
                    pass

                self.filters.append(SearchFilter(field, op_enum, value))
                return

        # Default: exact match
        self.filters.append(SearchFilter(field, FilterOperator.EQUALS, value_str))

    def matches_item(self, item: Dict[str, Any]) -> bool:
        """Check if item matches all filters"""
        if not self.filters:
            return True

        for filter_obj in self.filters:
            value = item.get(filter_obj.field)
            if not filter_obj.matches(value):
                return False

        return True


class SearchEngine:
    """Advanced search engine with fuzzy matching and filters"""

    def __init__(self) -> None:
        """Initialize search engine"""
        self.saved_searches: Dict[str, SearchQuery] = {}

    def search(
        self,
        items: List[Dict[str, Any]],
        query: str,
        fields: Optional[List[str]] = None,
        fuzzy: bool = False,
        threshold: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """
        Search items with query and optional fuzzy matching

        Args:
            items: List of items to search
            query: Query string
            fields: Fields to search in (for text search)
            fuzzy: Enable fuzzy matching
            threshold: Fuzzy match threshold (0-1)

        Returns:
            List of matching items
        """
        if not query:
            return items

        search_query = SearchQuery(query)
        results = []

        for item in items:
            # Check filters
            if not search_query.matches_item(item):
                continue

            # Check text search
            if search_query.text_search:
                if fuzzy:
                    match = self._fuzzy_search(
                        item, search_query.text_search, fields, threshold
                    )
                else:
                    match = self._text_search(item, search_query.text_search, fields)

                if not match:
                    continue

            results.append(item)

        return results

    def _text_search(
        self, item: Dict[str, Any], text: str, fields: Optional[List[str]] = None
    ) -> bool:
        """Check if item contains text"""
        search_fields = fields or list(item.keys())
        search_text = text.lower()

        for field in search_fields:
            value = item.get(field)
            if value and search_text in str(value).lower():
                return True

        return False

    def _fuzzy_search(
        self,
        item: Dict[str, Any],
        text: str,
        fields: Optional[List[str]] = None,
        threshold: float = 0.8,
    ) -> bool:
        """Check if item matches text with fuzzy matching"""
        search_fields = fields or list(item.keys())

        for field in search_fields:
            value = item.get(field)
            if value:
                score = self._calculate_fuzzy_score(text.lower(), str(value).lower())
                if score >= threshold:
                    return True

        return False

    @staticmethod
    def _calculate_fuzzy_score(search: str, target: str) -> float:
        """Calculate fuzzy match score (0-1)"""
        if not search or not target:
            return 0.0

        # Simple fuzzy matching: count matching characters
        matches = 0
        search_idx = 0

        for char in target:
            if search_idx < len(search) and char == search[search_idx]:
                matches += 1
                search_idx += 1

        # Score based on matches and length difference
        match_score = matches / len(search)
        length_penalty = 1 - (abs(len(search) - len(target)) / len(target))

        return (match_score + length_penalty) / 2

    def save_search(self, name: str, query: str) -> None:
        """Save a search query"""
        self.saved_searches[name] = SearchQuery(query)
        logger.info(f"Saved search: {name}")

    def get_saved_search(self, name: str) -> Optional[SearchQuery]:
        """Get a saved search"""
        return self.saved_searches.get(name)

    def list_saved_searches(self) -> List[str]:
        """List all saved searches"""
        return list(self.saved_searches.keys())

    def delete_saved_search(self, name: str) -> bool:
        """Delete a saved search"""
        if name in self.saved_searches:
            del self.saved_searches[name]
            logger.info(f"Deleted search: {name}")
            return True
        return False


class QueryBuilder:
    """Helper class to build queries programmatically"""

    def __init__(self) -> None:
        """Initialize query builder"""
        self.conditions: List[str] = []

    def add_tempo_range(self, min_tempo: float, max_tempo: float) -> "QueryBuilder":
        """Add tempo range filter"""
        self.conditions.append(f"tempo:{min_tempo}-{max_tempo}")
        return self

    def add_key(self, key: str) -> "QueryBuilder":
        """Add key filter"""
        self.conditions.append(f"key:{key}")
        return self

    def add_duration_range(self, min_sec: float, max_sec: float) -> "QueryBuilder":
        """Add duration range filter"""
        self.conditions.append(f"duration:{min_sec}-{max_sec}")
        return self

    def add_text(self, text: str) -> "QueryBuilder":
        """Add text search"""
        self.conditions.append(text)
        return self

    def build(self) -> str:
        """Build query string"""
        return " ".join(self.conditions)

    def reset(self) -> None:
        """Reset builder"""
        self.conditions = []


# Global singleton instance
_search_engine: Optional[SearchEngine] = None


def get_search_engine() -> SearchEngine:
    """Get or create search engine singleton"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine
