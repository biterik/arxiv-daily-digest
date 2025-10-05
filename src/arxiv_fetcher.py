"""
arXiv API fetcher module
Copyright (c) 2025 Erik Bitzek
Licensed under GNU AGPL v3

This module handles querying the arXiv API for recent papers matching
specified keywords and categories.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import time


class ArxivFetcher:
    """Fetches papers from arXiv API based on search criteria."""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    NAMESPACE = {'atom': 'http://www.w3.org/2005/Atom'}
    
    def __init__(self, categories: List[str], time_window_hours: int = 24, 
                 max_results: int = 100):
        """
        Initialize the arXiv fetcher.
        
        Args:
            categories: List of arXiv categories (e.g., ['cond-mat.mtrl-sci'])
            time_window_hours: How many hours back to search
            max_results: Maximum number of results to retrieve
        """
        self.categories = categories
        self.time_window_hours = time_window_hours
        self.max_results = max_results
        # Make cutoff_date timezone-aware (UTC)
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
    
    def build_query(self, keyword_groups: List[List[str]]) -> str:
        """
        Build arXiv API query string from keyword groups.
        
        Each inner list is AND'ed together, outer lists are OR'ed.
        Example: [["dislocation", "MD"], ["atomistic"]] becomes:
        (all:dislocation AND all:MD) OR (all:atomistic)
        
        Args:
            keyword_groups: List of keyword lists
            
        Returns:
            Query string for arXiv API
        """
        # Build category part
        cat_query = " OR ".join([f"cat:{cat}" for cat in self.categories])
        
        # Build keyword part
        keyword_parts = []
        for group in keyword_groups:
            if len(group) == 1:
                keyword_parts.append(f"all:{group[0]}")
            else:
                and_terms = " AND ".join([f"all:{kw}" for kw in group])
                keyword_parts.append(f"({and_terms})")
        
        keyword_query = " OR ".join(keyword_parts)
        
        # Combine: (category_filter) AND (keyword_filter)
        full_query = f"({cat_query}) AND ({keyword_query})"
        
        return full_query
    
    def fetch_papers(self, keyword_groups: List[List[str]]) -> List[Dict]:
        """
        Fetch papers from arXiv matching the criteria.
        
        Args:
            keyword_groups: List of keyword lists for Boolean search
            
        Returns:
            List of paper dictionaries with keys: id, title, authors, 
            abstract, published, updated, pdf_url, arxiv_url
        """
        query = self.build_query(keyword_groups)
        
        # Build URL with parameters
        params = {
            'search_query': query,
            'start': 0,
            'max_results': self.max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }
        
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        
        print(f"Querying arXiv with: {query}")
        print(f"Full URL: {url}\n")
        
        # Make request
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
        except Exception as e:
            print(f"Error fetching from arXiv: {e}")
            return []
        
        # Parse XML response
        root = ET.fromstring(data)
        
        papers = []
        for entry in root.findall('atom:entry', self.NAMESPACE):
            paper = self._parse_entry(entry)
            
            # Filter by date
            if paper and paper['published'] >= self.cutoff_date:
                papers.append(paper)
        
        print(f"Found {len(papers)} papers in the last {self.time_window_hours} hours")
        return papers
    
    def _parse_entry(self, entry: ET.Element) -> Optional[Dict]:
        """
        Parse a single entry from arXiv XML response.
        
        Args:
            entry: XML element for a single paper
            
        Returns:
            Dictionary with paper information
        """
        try:
            # Extract basic info
            arxiv_id = entry.find('atom:id', self.NAMESPACE).text
            title = entry.find('atom:title', self.NAMESPACE).text.strip()
            abstract = entry.find('atom:summary', self.NAMESPACE).text.strip()
            
            # Parse dates
            published_str = entry.find('atom:published', self.NAMESPACE).text
            updated_str = entry.find('atom:updated', self.NAMESPACE).text
            published = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            updated = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
            
            # Extract authors
            authors = []
            for author in entry.findall('atom:author', self.NAMESPACE):
                name = author.find('atom:name', self.NAMESPACE).text
                authors.append(name)
            
            # Get PDF link
            pdf_url = None
            for link in entry.findall('atom:link', self.NAMESPACE):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                    break
            
            return {
                'id': arxiv_id.split('/abs/')[-1],
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'published': published,
                'updated': updated,
                'pdf_url': pdf_url,
                'arxiv_url': arxiv_id
            }
        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None


def test_fetcher():
    """Test function to demonstrate usage."""
    fetcher = ArxivFetcher(
        categories=['cond-mat.mtrl-sci'],
        time_window_hours=24,
        max_results=50
    )
    
    # Test with sample keywords
    keyword_groups = [
        ["dislocation", "molecular dynamics"],
        ["atomistic simulation"]
    ]
    
    papers = fetcher.fetch_papers(keyword_groups)
    
    print(f"\n{'='*80}")
    print(f"Found {len(papers)} papers:")
    for paper in papers[:3]:  # Show first 3
        print(f"\nTitle: {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'][:3])}")
        print(f"Published: {paper['published']}")
        print(f"URL: {paper['arxiv_url']}")


if __name__ == "__main__":
    test_fetcher()