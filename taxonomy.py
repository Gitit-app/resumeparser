#!/usr/bin/env python3
"""
Taxonomy Module for Resume Parser POC

This module defines comprehensive taxonomies for all resume fields including synonyms,
n-gram phrases, and variations to support both rule-based and semantic parsing.

Author: Resume Parser POC
Version: 1.0
"""

from typing import Dict, List, Set
import re


class ResumeTaxonomy:
    """
    A comprehensive taxonomy system for resume parsing that includes field mappings,
    synonyms, and pattern definitions for all major resume sections.
    """
    
    # Section Header Taxonomy
    SECTION_TAXONOMY = {
        'experience': [
            'experience', 'work experience', 'professional experience', 'employment',
            'employment history', 'work history', 'career history', 'professional history',
            'work background', 'professional background', 'career background',
            'professional summary', 'career summary', 'work summary',
            'professional achievements', 'career achievements', 'accomplishments',
            'positions held', 'roles', 'professional roles', 'career highlights',
            'employment record', 'work record', 'professional record'
        ],
        
        'education': [
            'education', 'educational background', 'academic background',
            'academic qualifications', 'educational qualifications', 'qualifications',
            'academic history', 'educational history', 'academic record',
            'academic credentials', 'educational credentials', 'credentials',
            'academic achievements', 'educational achievements',
            'degrees', 'academic degrees', 'university', 'college',
            'schooling', 'academic training', 'formal education'
        ],
        
        'skills': [
            'skills', 'technical skills', 'professional skills', 'core skills',
            'key skills', 'relevant skills', 'core competencies', 'competencies',
            'technical competencies', 'professional competencies',
            'expertise', 'technical expertise', 'areas of expertise',
            'proficiencies', 'technical proficiencies', 'abilities',
            'technical abilities', 'capabilities', 'technical capabilities',
            'knowledge', 'technical knowledge', 'specializations',
            'programming skills', 'software skills', 'technology skills'
        ],
        
        'projects': [
            'projects', 'personal projects', 'professional projects',
            'academic projects', 'key projects', 'notable projects',
            'selected projects', 'relevant projects', 'major projects',
            'portfolio', 'work samples', 'project experience',
            'development projects', 'software projects', 'technical projects',
            'research projects', 'case studies', 'implementations'
        ],
        
        'certifications': [
            'certifications', 'certificates', 'professional certifications',
            'technical certifications', 'industry certifications',
            'credentials', 'professional credentials', 'licenses',
            'professional licenses', 'accreditations', 'qualifications',
            'professional qualifications', 'awards', 'honors',
            'achievements', 'recognition', 'professional recognition'
        ]
    }
    
    # Technical Skills Taxonomy
    TECHNICAL_SKILLS = {
        'programming_languages': [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c',
            'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala',
            'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
            'objective-c', 'dart', 'lua', 'haskell', 'clojure'
        ],
        
        'web_technologies': [
            'html', 'css', 'html5', 'css3', 'sass', 'scss', 'less',
            'bootstrap', 'tailwind', 'react', 'angular', 'vue',
            'vue.js', 'react.js', 'angular.js', 'jquery', 'node.js',
            'express', 'express.js', 'next.js', 'nuxt.js', 'gatsby',
            'svelte', 'ember', 'backbone'
        ],
        
        'frameworks_libraries': [
            'django', 'flask', 'fastapi', 'spring', 'spring boot',
            'laravel', 'symfony', 'codeigniter', 'rails', 'ruby on rails',
            'asp.net', '.net', 'dotnet', 'tensorflow', 'pytorch',
            'keras', 'scikit-learn', 'pandas', 'numpy', 'opencv'
        ],
        
        'databases': [
            'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis',
            'elasticsearch', 'oracle', 'sql server', 'cassandra',
            'dynamodb', 'neo4j', 'couchdb', 'influxdb', 'mariadb'
        ],
        
        'cloud_platforms': [
            'aws', 'amazon web services', 'azure', 'microsoft azure',
            'gcp', 'google cloud', 'google cloud platform',
            'heroku', 'digitalocean', 'linode', 'vultr'
        ],
        
        'devops_tools': [
            'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions',
            'terraform', 'ansible', 'puppet', 'chef', 'vagrant',
            'prometheus', 'grafana', 'elk stack', 'nginx', 'apache'
        ],
        
        'version_control': [
            'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial'
        ],
        
        'operating_systems': [
            'linux', 'ubuntu', 'centos', 'debian', 'windows', 'macos',
            'unix', 'fedora', 'arch linux', 'red hat'
        ]
    }
    
    # Contact Information Patterns
    CONTACT_PATTERNS = {
        'email': [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b'
        ],
        
        'phone': [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\+?[1-9]\d{1,14}',  # International format
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}'
        ],
        
        'linkedin': [
            r'linkedin\.com/in/[\w-]+',
            r'www\.linkedin\.com/in/[\w-]+',
            r'/in/[\w-]+',
            r'linkedin\.com/pub/[\w-]+',
        ],
        
        'github': [
            r'github\.com/[\w-]+',
            r'www\.github\.com/[\w-]+',
            r'git\.hub/[\w-]+'
        ]
    }
    
    # Education Patterns
    EDUCATION_PATTERNS = {
        'degrees': [
            r'\b(Bachelor|B\.?A\.?|B\.?S\.?|B\.?Sc\.?|B\.?E\.?|B\.?Tech\.?)\b',
            r'\b(Master|M\.?A\.?|M\.?S\.?|M\.?Sc\.?|M\.?E\.?|M\.?Tech\.?|MBA)\b',
            r'\b(Doctor|Ph\.?D\.?|D\.?Phil\.?|Ph\.?D|Doctorate)\b',
            r'\b(Associate|A\.?A\.?|A\.?S\.?)\b',
            r'\bJD\b|\bJ\.D\.\b|\bJuris Doctor\b',
            r'\bMD\b|\bM\.D\.\b|\bDoctor of Medicine\b'
        ],
        
        'institutions': [
            'university', 'college', 'institute', 'school', 'academy',
            'polytechnic', 'technical college', 'community college'
        ],
        
        'fields_of_study': [
            'computer science', 'software engineering', 'information technology',
            'electrical engineering', 'mechanical engineering', 'civil engineering',
            'business administration', 'finance', 'economics', 'mathematics',
            'physics', 'chemistry', 'biology', 'psychology', 'marketing'
        ]
    }
    
    # Experience Indicators
    EXPERIENCE_INDICATORS = {
        'job_titles': [
            'engineer', 'developer', 'programmer', 'analyst', 'manager',
            'director', 'lead', 'senior', 'junior', 'associate',
            'consultant', 'specialist', 'architect', 'designer',
            'scientist', 'researcher', 'coordinator', 'supervisor'
        ],
        
        'company_indicators': [
            'inc', 'corp', 'corporation', 'company', 'ltd', 'llc',
            'technologies', 'systems', 'solutions', 'services',
            'enterprises', 'group', 'international', 'global'
        ],
        
        'action_verbs': [
            'developed', 'created', 'built', 'designed', 'implemented',
            'managed', 'led', 'coordinated', 'supervised', 'analyzed',
            'optimized', 'improved', 'enhanced', 'maintained',
            'delivered', 'achieved', 'established', 'collaborated'
        ]
    }
    
    @staticmethod
    def normalize_field_name(field_text: str) -> str:
        """
        Normalize field text to standard field names.
        
        Args:
            field_text (str): Raw field text from resume
            
        Returns:
            str: Normalized field name or 'unknown'
        """
        field_text = field_text.lower().strip()
        field_text = re.sub(r'[^\w\s]', ' ', field_text)
        field_text = re.sub(r'\s+', ' ', field_text)
        
        for field_name, synonyms in ResumeTaxonomy.SECTION_TAXONOMY.items():
            for synonym in synonyms:
                if synonym in field_text or field_text in synonym:
                    return field_name
        
        return 'unknown'
    
    @staticmethod
    def get_all_skill_keywords() -> Set[str]:
        """
        Get all technical skill keywords for pattern matching.
        
        Returns:
            Set[str]: Set of all skill keywords
        """
        all_skills = set()
        for category, skills in ResumeTaxonomy.TECHNICAL_SKILLS.items():
            all_skills.update(skills)
        return all_skills
    
    @staticmethod
    def categorize_skill(skill: str) -> str:
        """
        Categorize a skill into its technical category.
        
        Args:
            skill (str): Skill to categorize
            
        Returns:
            str: Category name or 'other'
        """
        skill_lower = skill.lower().strip()
        
        for category, skills in ResumeTaxonomy.TECHNICAL_SKILLS.items():
            if skill_lower in skills:
                return category
        
        return 'other'
    
    @staticmethod
    def get_section_keywords(section: str) -> List[str]:
        """
        Get all keywords for a specific section.
        
        Args:
            section (str): Section name
            
        Returns:
            List[str]: List of keywords for the section
        """
        return ResumeTaxonomy.SECTION_TAXONOMY.get(section, [])
    
    @staticmethod
    def is_section_header(text: str, threshold: float = 0.6) -> tuple:
        """
        Check if text is likely a section header and return the best match.
        
        Args:
            text (str): Text to analyze
            threshold (float): Similarity threshold
            
        Returns:
            tuple: (is_header: bool, section_name: str, confidence: float)
        """
        text_clean = text.lower().strip()
        text_clean = re.sub(r'[^\w\s]', ' ', text_clean)
        text_clean = re.sub(r'\s+', ' ', text_clean)
        
        best_match = None
        best_score = 0.0
        
        for section, synonyms in ResumeTaxonomy.SECTION_TAXONOMY.items():
            for synonym in synonyms:
                # Exact match
                if text_clean == synonym:
                    return True, section, 1.0
                
                # Partial match
                if synonym in text_clean or text_clean in synonym:
                    score = min(len(synonym), len(text_clean)) / max(len(synonym), len(text_clean))
                    if score > best_score:
                        best_score = score
                        best_match = section
        
        if best_score >= threshold:
            return True, best_match, best_score
        
        return False, 'unknown', 0.0


# Example usage and testing
if __name__ == "__main__":
    taxonomy = ResumeTaxonomy()
    
    # Test section header detection
    test_headers = [
        "Professional Experience",
        "Technical Skills",
        "Educational Background",
        "Notable Projects",
        "Certifications and Licenses"
    ]
    
    print("Testing section header detection:")
    for header in test_headers:
        is_header, section, confidence = taxonomy.is_section_header(header)
        print(f"'{header}' -> {section} (confidence: {confidence:.2f})")
    
    # Test skill categorization
    test_skills = ["Python", "React", "AWS", "MySQL", "Docker"]
    print("\nTesting skill categorization:")
    for skill in test_skills:
        category = taxonomy.categorize_skill(skill)
        print(f"'{skill}' -> {category}")
    
    # Test field normalization
    test_fields = ["Work Experience", "Technical Expertise", "Academic Background"]
    print("\nTesting field normalization:")
    for field in test_fields:
        normalized = taxonomy.normalize_field_name(field)
        print(f"'{field}' -> {normalized}")