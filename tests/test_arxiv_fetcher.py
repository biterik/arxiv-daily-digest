"""
Unit tests for arxiv_fetcher module
Copyright (c) 2025 Erik Bitzek
Licensed under GNU AGPL v3
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from arxiv_fetcher import ArxivFetcher


class TestArxivFetcher:
    """Test cases for ArxivFetcher class."""
    
    def test_initialization(self):
        """Test fetcher initialization."""
        fetcher = ArxivFetcher(
            categories=['cond-mat.mtrl-sci'],
            time_window_hours=24,
            max_results=50
        )
        
        assert fetcher.categories == ['cond-mat.mtrl-sci']
        assert fetcher.time_window_hours == 24
        assert fetcher.max_results == 50
    
    def test_build_query_single_keyword(self):
        """Test query building with single keyword."""
        fetcher = ArxivFetcher(categories=['cs.AI'])
        
        query = fetcher.build_query([['machine learning']])
        
        assert 'cat:cs.AI' in query
        assert 'all:machine learning' in query
    
    def test_build_query_and_logic(self):
        """Test query building with AND logic."""
        fetcher = ArxivFetcher(categories=['cond-mat.mtrl-sci'])
        
        query = fetcher.build_query([['dislocation', 'molecular dynamics']])
        
        assert 'cat:cond-mat.mtrl-sci' in query
        assert 'all:dislocation' in query
        assert 'all:molecular dynamics' in query
        assert 'AND' in query
    
    def test_build_query_or_logic(self):
        """Test query building with OR logic."""
        fetcher = ArxivFetcher(categories=['cond-mat.mtrl-sci'])
        
        query = fetcher.build_query([
            ['dislocation'],
            ['atomistic simulation']
        ])
        
        assert 'all:dislocation' in query
        assert 'all:atomistic simulation' in query
        assert 'OR' in query
    
    def test_build_query_multiple_categories(self):
        """Test query building with multiple categories."""
        fetcher = ArxivFetcher(
            categories=['cond-mat.mtrl-sci', 'physics.comp-ph']
        )
        
        query = fetcher.build_query([['simulation']])
        
        assert 'cat:cond-mat.mtrl-sci' in query
        assert 'cat:physics.comp-ph' in query
        assert 'OR' in query  # Categories are OR'ed


@pytest.mark.integration
class TestArxivAPI:
    """Integration tests that actually call arXiv API."""
    
    def test_fetch_papers_live(self):
        """
        Test fetching papers from arXiv (requires internet).
        This is an integration test and may be slow.
        """
        fetcher = ArxivFetcher(
            categories=['cs.AI'],
            time_window_hours=168,  # 1 week for better chance of results
            max_results=5
        )
        
        papers = fetcher.fetch_papers([['machine learning']])
        
        # Should get some results
        assert isinstance(papers, list)
        
        # If papers found, check structure
        if papers:
            paper = papers[0]
            assert 'id' in paper
            assert 'title' in paper
            assert 'authors' in paper
            assert 'abstract' in paper
            assert 'published' in paper
            assert 'arxiv_url' in paper


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])