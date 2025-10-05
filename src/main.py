"""
Main orchestration module for arXiv Daily Digest
Copyright (c) 2025 Erik Bitzek
Licensed under GNU AGPL v3

This module coordinates fetching, summarizing, and outputting the daily digest.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

from arxiv_fetcher import ArxivFetcher
from summarizer import PaperSummarizer
from notifier import DigestNotifier


def load_config(config_path: str = 'config.yml') -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    # If relative path, look in project root (parent of src/)
    if not os.path.isabs(config_path):
        # Get the directory containing this script
        script_dir = Path(__file__).parent
        # Look in parent directory (project root)
        config_path = script_dir.parent / config_path
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found")
        print(f"Looking in: {os.path.abspath(config_path)}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        sys.exit(1)


def run_digest(config_path: str = 'config.yml', dry_run: bool = False) -> None:
    """
    Run the complete digest workflow.
    
    Args:
        config_path: Path to configuration file
        dry_run: If True, fetch and summarize but don't output
    """
    print("=" * 80)
    print("arXiv Daily Digest")
    print("=" * 80)
    print()
    
    # Load configuration
    print("Loading configuration...")
    config = load_config(config_path)
    
    # Initialize fetcher
    print("Initializing arXiv fetcher...")
    fetcher = ArxivFetcher(
        categories=config['arxiv']['categories'],
        time_window_hours=config['arxiv']['time_window_hours'],
        max_results=config['arxiv']['max_results']
    )
    
    # Fetch papers
    print(f"\nFetching papers from arXiv...")
    print(f"Categories: {', '.join(config['arxiv']['categories'])}")
    print(f"Time window: Last {config['arxiv']['time_window_hours']} hours")
    print()
    
    papers = fetcher.fetch_papers(config['keywords'])
    
    if not papers:
        print("\nNo papers found matching your criteria.")
        print("Try:")
        print("  - Broadening your keywords")
        print("  - Increasing time_window_hours in config.yml")
        print("  - Checking different arXiv categories")
        return
    
    print(f"\n{'='*80}")
    print(f"Found {len(papers)} matching papers")
    print(f"{'='*80}\n")
    
    # Initialize summarizer
    print("Initializing OpenAI summarizer...")
    try:
        summarizer = PaperSummarizer(
            model=config['openai']['model'],
            max_tokens=config['openai']['max_tokens'],
            temperature=config['openai']['temperature']
        )
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo use AI summaries, set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nContinuing without summaries...\n")
        
        # Add placeholder summaries
        for paper in papers:
            paper['summary'] = "AI summary unavailable (no API key)"
        summarized_papers = papers
    else:
        # Generate summaries
        print(f"\nGenerating AI summaries for {len(papers)} papers...")
        print("(This may take a minute...)\n")
        summarized_papers = summarizer.summarize_papers(papers)
    
    # Output digest
    if dry_run:
        print("\n[DRY RUN] Skipping output")
        print("\nFirst paper preview:")
        print("-" * 80)
        if summarized_papers:
            p = summarized_papers[0]
            print(f"Title: {p['title']}")
            print(f"Summary: {p.get('summary', 'N/A')}")
        return
    
    print(f"\n{'='*80}")
    print("Generating output...")
    print(f"{'='*80}\n")
    
    # Make output path relative to project root
    output_file = config['output']['output_file']
    if not os.path.isabs(output_file):
        script_dir = Path(__file__).parent
        output_file = script_dir.parent / output_file
    
    notifier = DigestNotifier(
        output_format=config['output']['format'],
        output_file=str(output_file),
        include_abstract=config['output']['include_abstract']
    )
    
    email_recipient = None
    if config['output']['format'] in ['email', 'both']:
        if config['email'].get('enabled'):
            email_recipient = config['email']['recipient']
    
    notifier.output_digest(summarized_papers, email_recipient)
    
    print(f"\n{'='*80}")
    print("Digest complete!")
    print(f"{'='*80}")


def main():
    """Entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate daily arXiv digest with AI summaries'
    )
    parser.add_argument(
        '--config', 
        default='config.yml',
        help='Path to configuration file (default: config.yml)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Fetch and summarize but do not output'
    )
    
    args = parser.parse_args()
    
    try:
        run_digest(args.config, args.dry_run)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()