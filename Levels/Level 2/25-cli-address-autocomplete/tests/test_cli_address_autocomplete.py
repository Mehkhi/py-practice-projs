"""Tests for CLI Address Autocomplete."""

import pytest
import tempfile
import csv
from cli_address_autocomplete.core import AddressAutocomplete
from cli_address_autocomplete.utils import normalize_address, validate_query


class TestAddressAutocomplete:
    @pytest.fixture
    def sample_dataset(self):
        addresses = [
            "123 Main St, Anytown, USA",
            "456 Oak Ave, Somewhere, USA",
            "789 Pine Rd, Elsewhere, USA",
            "321 Elm St, Anytown, USA",
            "654 Maple Dr, Somewhere, USA"
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            for addr in addresses:
                writer.writerow([addr])
            return f.name

    def test_build_index(self, sample_dataset):
        ac = AddressAutocomplete(sample_dataset)
        assert len(ac.addresses) == 5
        assert len(ac.index) > 0

    def test_search_exact_match(self, sample_dataset):
        ac = AddressAutocomplete(sample_dataset)
        results = ac.search("Main St")
        assert "123 Main St, Anytown, USA" in results

    def test_search_fuzzy_match(self, sample_dataset):
        ac = AddressAutocomplete(sample_dataset)
        results = ac.search("Maine")  # fuzzy for Main
        assert len(results) > 0

    def test_search_no_match(self, sample_dataset):
        ac = AddressAutocomplete(sample_dataset)
        results = ac.search("Nonexistent")
        assert len(results) == 0

    def test_search_pagination(self, sample_dataset):
        ac = AddressAutocomplete(sample_dataset)
        results_page1 = ac.search("St", limit=2, page=1)
        results_page2 = ac.search("St", limit=2, page=2)
        assert len(results_page1) == 2
        assert len(results_page2) >= 0
        assert set(results_page1).isdisjoint(set(results_page2))

    def test_search_limit(self, sample_dataset):
        ac = AddressAutocomplete(sample_dataset)
        results = ac.search("USA", limit=3)
        assert len(results) <= 3

    def test_invalid_dataset(self):
        with pytest.raises(FileNotFoundError):
            AddressAutocomplete("nonexistent.csv")

    def test_empty_query(self, sample_dataset):
        ac = AddressAutocomplete(sample_dataset)
        results = ac.search("")
        assert results == []

    def test_short_query(self, sample_dataset):
        ac = AddressAutocomplete(sample_dataset)
        results = ac.search("A")
        assert results == []  # since trigrams need 3 chars


class TestUtils:
    def test_normalize_address(self):
        assert normalize_address("  123 Main St  ") == "123 main st"

    def test_validate_query(self):
        assert validate_query("abc") == True
        assert validate_query("ab") == False
        assert validate_query("") == False
