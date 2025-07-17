#!/usr/bin/env python3
"""
Test script to demonstrate the resume parser functionality.
"""

import sys
import os
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_loader import FileLoader
from parsers.rule_based_parser import RuleBasedParser
from parsers.semantic_parser import SemanticParser


def test_parser(file_path, parser_type='rule'):
    """Test the parser with a sample resume."""
    print(f"\n=== Testing {parser_type.upper()} Parser ===")
    print(f"File: {file_path}")
    
    try:
        # Load the file
        text = FileLoader.load_file(file_path)
        print(f"Text length: {len(text)} characters")
        
        # Initialize parser
        if parser_type == 'rule':
            parser = RuleBasedParser()
        else:
            print("Loading semantic model (this may take a moment)...")
            parser = SemanticParser()
        
        # Parse the resume
        result = parser.parse(text)
        
        # Display results
        print("\n--- Parsing Results ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    """Run tests on sample resumes."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Test files
    test_files = [
        os.path.join(script_dir, 'sample_resume_1.txt'),
        os.path.join(script_dir, 'sample_resume_2.txt')
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n{'='*60}")
            print(f"Testing with: {os.path.basename(test_file)}")
            print('='*60)
            
            # Test rule-based parser
            test_parser(test_file, 'rule')
            
            # Test semantic parser (comment out if you want to skip)
            # print(f"\n{'-'*40}")
            # test_parser(test_file, 'semantic')
        else:
            print(f"Warning: Test file not found: {test_file}")
    
    print(f"\n{'='*60}")
    print("Test completed!")
    print("To test semantic parsing, uncomment the semantic test lines in this script.")


if __name__ == '__main__':
    main()