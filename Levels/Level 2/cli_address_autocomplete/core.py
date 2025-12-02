"""Core logic for address autocomplete using trigram indexing."""

import csv
import logging
from collections import defaultdict
from typing import List, Dict, Set


class AddressAutocomplete:
    """Address autocomplete using trigram index for fast fuzzy matching."""

    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.index: Dict[str, Set[str]] = defaultdict(set)
        self.addresses: List[str] = []
        self._build_index()

    def _build_index(self):
        """Build trigram index from address dataset."""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        address = row[0].strip()
                        if address:
                            self.addresses.append(address)
                            trigrams = self._get_trigrams(address.lower())
                            for trigram in trigrams:
                                self.index[trigram].add(address)
            logging.info(f"Built index with {len(self.addresses)} addresses and {len(self.index)} trigrams")
        except FileNotFoundError:
            logging.error(f"Dataset file not found: {self.dataset_path}")
            raise
        except Exception as e:
            logging.error(f"Error building index: {e}")
            raise

    def _get_trigrams(self, text: str) -> Set[str]:
        """Generate trigrams from text."""
        trigrams = set()
        text = text.replace(',', '').replace(' ', '')  # remove punctuation for simplicity
        for i in range(len(text) - 2):
            trigrams.add(text[i:i+3])
        return trigrams

    def search(self, query: str, limit: int = 10, page: int = 1) -> List[str]:
        """Search for addresses matching the query."""
        normalized_query = query.strip().lower()
        cleaned_query = normalized_query.replace(',', '').replace(' ', '')

        if not cleaned_query:
            return []

        if len(cleaned_query) == 1:
            return []

        if len(cleaned_query) < 3:
            matches = [addr for addr in self.addresses if normalized_query in addr.lower()]
            start = (page - 1) * limit
            end = start + limit
            return matches[start:end]

        query_trigrams = self._get_trigrams(normalized_query)
        if not query_trigrams:
            return []

        # Find candidates: addresses that share at least one trigram
        candidates = set()
        for trigram in query_trigrams:
            candidates.update(self.index.get(trigram, set()))

        # Score candidates by number of matching trigrams
        scored = []
        for addr in candidates:
            addr_trigrams = self._get_trigrams(addr.lower())
            score = len(query_trigrams & addr_trigrams)
            if score > 0:
                scored.append((score, addr))

        # Sort by score descending, then by address
        scored.sort(key=lambda x: (-x[0], x[1]))

        # Pagination
        start = (page - 1) * limit
        end = start + limit
        results = [addr for _, addr in scored[start:end]]

        return results
