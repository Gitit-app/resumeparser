#!/usr/bin/env python3
"""
Main Module for Resume Parser POC

This module provides a command-line interface for the resume parser that supports
both rule-based and semantic parsing methods.

Author: Resume Parser POC
Version: 1.0
"""

import argparse
import json
import sys
import os
from typing import Dict, Any

# Import parser modules
from file_loader import FileLoader
from rule_based_parser import RuleBasedParser
from semantic_parser import SemanticParser


def main():
    """Main function to run the resume parser CLI."""
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Resume Parser POC - Extract structured information from resumes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py resume.pdf --method rule
  python main.py resume.docx --method semantic --output result.json
  python main.py resume.txt --method both --pretty
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the resume file (PDF, DOCX, or TXT)'
    )
    
    parser.add_argument(
        '--method', '-m',
        choices=['rule', 'semantic', 'both'],
        default='both',
        help='Parsing method to use (default: both)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path for JSON results (default: stdout)'
    )
    
    parser.add_argument(
        '--pretty', '-p',
        action='store_true',
        help='Pretty print JSON output with indentation'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with processing details'
    )
    
    parser.add_argument(
        '--model',
        default='all-MiniLM-L6-v2',
        help='Sentence transformer model for semantic parsing (default: all-MiniLM-L6-v2)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load the resume file
        if args.verbose:
            print(f"Loading file: {args.input_file}")
            
        file_info = FileLoader.get_file_info(args.input_file)
        
        if not file_info['is_supported']:
            print(f"Error: Unsupported file format '{file_info['extension']}'. "
                  f"Supported formats: PDF, DOCX, TXT", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"File info: {file_info['size_kb']} KB, {file_info['extension']} format")
        
        # Extract text from file
        resume_text = FileLoader.load_file(args.input_file)
        
        if not resume_text.strip():
            print("Error: No text content found in the file.", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"Extracted text length: {len(resume_text)} characters")
        
        # Parse based on selected method(s)
        results = {}
        
        if args.method in ['rule', 'both']:
            if args.verbose:
                print("Running rule-based parsing...")
            
            rule_parser = RuleBasedParser()
            rule_result = rule_parser.parse(resume_text)
            
            if args.method == 'rule':
                results = rule_result
            else:
                results['rule_based'] = rule_result
        
        if args.method in ['semantic', 'both']:
            if args.verbose:
                print("Running semantic parsing...")
            
            semantic_parser = SemanticParser(model_name=args.model)
            semantic_result = semantic_parser.parse(resume_text)
            
            if args.method == 'semantic':
                results = semantic_result
            else:
                results['semantic'] = semantic_result
        
        # Add metadata
        if args.method == 'both':
            results['comparison'] = generate_comparison(
                results['rule_based'], 
                results['semantic']
            )
        
        # Output results
        if args.pretty:
            json_output = json.dumps(results, indent=2, ensure_ascii=False)
        else:
            json_output = json.dumps(results, ensure_ascii=False)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            
            if args.verbose:
                print(f"Results saved to: {args.output}")
        else:
            print(json_output)
        
        if args.verbose:
            print_summary(results, args.method)
    
    except Exception as e:
        print(f"Error processing resume: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def generate_comparison(rule_result: Dict[str, Any], semantic_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comparison between rule-based and semantic parsing results.
    
    Args:
        rule_result (Dict[str, Any]): Rule-based parsing result
        semantic_result (Dict[str, Any]): Semantic parsing result
        
    Returns:
        Dict[str, Any]: Comparison analysis
    """
    comparison = {
        'contact_info': {
            'name_match': rule_result.get('name') == semantic_result.get('name'),
            'email_match': rule_result.get('email') == semantic_result.get('email'),
            'phone_match': rule_result.get('phone') == semantic_result.get('phone')
        },
        'skills': {
            'rule_count': len(rule_result.get('skills', [])),
            'semantic_count': len(semantic_result.get('skills', {})),
            'rule_skills': rule_result.get('skills', []),
            'semantic_skills': semantic_result.get('skills', {})
        },
        'sections': {
            'rule_sections': len([k for k in rule_result.keys() 
                                if k in ['education', 'experience', 'projects', 'certifications'] 
                                and rule_result[k]]),
            'semantic_sections': len([k for k in semantic_result.keys() 
                                    if k in ['education', 'experience', 'projects', 'certifications'] 
                                    and semantic_result[k]])
        },
        'metadata': {
            'rule_method': rule_result.get('metadata', {}).get('parsing_method'),
            'semantic_method': semantic_result.get('metadata', {}).get('parsing_method'),
            'rule_text_length': rule_result.get('metadata', {}).get('text_length'),
            'semantic_text_length': semantic_result.get('metadata', {}).get('text_length')
        }
    }
    
    return comparison


def print_summary(results: Dict[str, Any], method: str):
    """
    Print a summary of parsing results.
    
    Args:
        results (Dict[str, Any]): Parsing results
        method (str): Parsing method used
    """
    print("\n" + "="*50, file=sys.stderr)
    print("PARSING SUMMARY", file=sys.stderr)
    print("="*50, file=sys.stderr)
    
    if method == 'both':
        rule_result = results['rule_based']
        semantic_result = results['semantic']
        comparison = results['comparison']
        
        print(f"Rule-based results:", file=sys.stderr)
        print(f"  Contact info: {bool(rule_result.get('name'))} name, "
              f"{bool(rule_result.get('email'))} email, "
              f"{bool(rule_result.get('phone'))} phone", file=sys.stderr)
        print(f"  Skills found: {len(rule_result.get('skills', []))}", file=sys.stderr)
        print(f"  Sections detected: {rule_result.get('metadata', {}).get('sections_detected', 0)}", file=sys.stderr)
        
        print(f"\nSemantic results:", file=sys.stderr)
        print(f"  Contact info: {bool(semantic_result.get('name'))} name, "
              f"{bool(semantic_result.get('email'))} email, "
              f"{bool(semantic_result.get('phone'))} phone", file=sys.stderr)
        
        if isinstance(semantic_result.get('skills'), dict):
            total_skills = sum(len(skills) for skills in semantic_result['skills'].values())
            print(f"  Skills found: {total_skills} (categorized)", file=sys.stderr)
        else:
            print(f"  Skills found: {len(semantic_result.get('skills', []))}", file=sys.stderr)
        
        print(f"  Chunks processed: {semantic_result.get('metadata', {}).get('chunks_processed', 0)}", file=sys.stderr)
        
        print(f"\nComparison:", file=sys.stderr)
        print(f"  Contact info matches: {comparison['contact_info']}", file=sys.stderr)
        print(f"  Skills count - Rule: {comparison['skills']['rule_count']}, "
              f"Semantic: {comparison['skills']['semantic_count']}", file=sys.stderr)
    
    else:
        result = results
        print(f"Method: {method}", file=sys.stderr)
        print(f"Contact info: {bool(result.get('name'))} name, "
              f"{bool(result.get('email'))} email, "
              f"{bool(result.get('phone'))} phone", file=sys.stderr)
        
        if isinstance(result.get('skills'), dict):
            total_skills = sum(len(skills) for skills in result['skills'].values())
            print(f"Skills found: {total_skills} (categorized)", file=sys.stderr)
        else:
            print(f"Skills found: {len(result.get('skills', []))}", file=sys.stderr)
        
        if 'sections_detected' in result.get('metadata', {}):
            print(f"Sections detected: {result['metadata']['sections_detected']}", file=sys.stderr)
        
        if 'chunks_processed' in result.get('metadata', {}):
            print(f"Chunks processed: {result['metadata']['chunks_processed']}", file=sys.stderr)


def validate_dependencies():
    """Check if optional dependencies are available."""
    missing_deps = []
    
    try:
        import faiss
    except ImportError:
        missing_deps.append('faiss-cpu')
    
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        missing_deps.append('sentence-transformers')
    
    try:
        import fitz  # PyMuPDF
    except ImportError:
        missing_deps.append('PyMuPDF')
    
    try:
        from docx import Document
    except ImportError:
        missing_deps.append('python-docx')
    
    if missing_deps:
        print(f"Warning: Missing optional dependencies: {', '.join(missing_deps)}", file=sys.stderr)
        print(f"Install with: pip install {' '.join(missing_deps)}", file=sys.stderr)
        print("Some features may not be available.\n", file=sys.stderr)


if __name__ == "__main__":
    # Check dependencies
    validate_dependencies()
    
    # Run main function
    main()