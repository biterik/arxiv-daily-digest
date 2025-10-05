"""
OpenAI summarization module
Copyright (c) 2025 Erik Bitzek
Licensed under GNU AGPL v3

This module uses OpenAI's API to generate concise summaries of arXiv papers.
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI


class PaperSummarizer:
    """Generates AI summaries of academic papers using OpenAI."""
    
    def __init__(self, model: str = "gpt-4o-mini", max_tokens: int = 150,
                 temperature: float = 0.3):
        """
        Initialize the summarizer.
        
        Args:
            model: OpenAI model to use (gpt-4o-mini is cost-effective)
            max_tokens: Maximum tokens for each summary
            temperature: Sampling temperature (0-1, lower = more focused)
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Please set it with your OpenAI API key."
            )
        
        self.client = OpenAI(api_key=api_key)
    
    def summarize_paper(self, paper: Dict) -> Optional[str]:
        """
        Generate a concise summary of a single paper.
        
        Args:
            paper: Dictionary containing paper information (title, abstract, etc.)
            
        Returns:
            AI-generated summary string, or None if error occurs
        """
        prompt = self._build_prompt(paper)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a materials science researcher. Summarize "
                            "academic papers concisely, focusing on key findings, "
                            "methods, and significance. Keep summaries under 100 words."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error generating summary for '{paper['title']}': {e}")
            return None
    
    def summarize_papers(self, papers: List[Dict], 
                        show_progress: bool = True) -> List[Dict]:
        """
        Generate summaries for multiple papers.
        
        Args:
            papers: List of paper dictionaries
            show_progress: Whether to print progress updates
            
        Returns:
            List of paper dictionaries with added 'summary' field
        """
        summarized = []
        
        for i, paper in enumerate(papers, 1):
            if show_progress:
                print(f"Summarizing paper {i}/{len(papers)}: {paper['title'][:60]}...")
            
            summary = self.summarize_paper(paper)
            
            # Add summary to paper dict
            paper_with_summary = paper.copy()
            paper_with_summary['summary'] = summary if summary else "Summary unavailable"
            
            summarized.append(paper_with_summary)
        
        return summarized
    
    def _build_prompt(self, paper: Dict) -> str:
        """
        Build the prompt for summarization.
        
        Args:
            paper: Paper dictionary
            
        Returns:
            Formatted prompt string
        """
        authors_str = ", ".join(paper['authors'][:3])
        if len(paper['authors']) > 3:
            authors_str += " et al."
        
        prompt = f"""Title: {paper['title']}

Authors: {authors_str}

Abstract: {paper['abstract']}

Please provide a concise summary (2-3 sentences) highlighting:
1. What problem/question the paper addresses
2. The main approach or method used
3. Key findings or contributions

Keep it accessible to materials science researchers."""
        
        return prompt


def test_summarizer():
    """Test function to demonstrate usage."""
    # This requires OPENAI_API_KEY to be set
    try:
        summarizer = PaperSummarizer()
        
        # Test with a sample paper
        sample_paper = {
            'title': 'Machine Learning Interatomic Potentials for Materials Science',
            'authors': ['Smith, J.', 'Doe, A.', 'Johnson, B.'],
            'abstract': (
                'We present a novel approach to developing machine learning '
                'interatomic potentials using graph neural networks. Our method '
                'achieves quantum mechanical accuracy at classical computational '
                'cost for materials simulations. We demonstrate applications to '
                'crystal structure prediction and defect energetics.'
            )
        }
        
        summary = summarizer.summarize_paper(sample_paper)
        print(f"Generated summary:\n{summary}")
        
    except ValueError as e:
        print(f"Cannot test: {e}")
        print("Set OPENAI_API_KEY environment variable to test this module.")


if __name__ == "__main__":
    test_summarizer()