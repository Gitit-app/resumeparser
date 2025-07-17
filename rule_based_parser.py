#!/usr/bin/env python3
"""
Rule-Based Parser Module for Resume Parser POC

This module implements a traditional rule-based approach for parsing resumes using
regex patterns, keyword matching, and taxonomy-based section detection.

Author: Resume Parser POC
Version: 1.0
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from taxonomy import ResumeTaxonomy


class RuleBasedParser:
    """
    A rule-based resume parser that uses regex patterns and taxonomy-based
    keyword matching to extract structured information from resume text.
    """
    
    def __init__(self):
        """Initialize the rule-based parser with taxonomy and patterns."""
        self.taxonomy = ResumeTaxonomy()
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_patterns = [
            re.compile(pattern) for pattern in self.taxonomy.CONTACT_PATTERNS['phone']
        ]
        self.linkedin_patterns = [
            re.compile(pattern) for pattern in self.taxonomy.CONTACT_PATTERNS['linkedin']
        ]
        self.github_patterns = [
            re.compile(pattern) for pattern in self.taxonomy.CONTACT_PATTERNS['github']
        ]
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured information.
        
        Args:
            text (str): Raw resume text
            
        Returns:
            Dict[str, Any]: Structured resume data
        """
        # Initialize result structure
        result = {
            'name': None,
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None,
            'skills': [],
            'education': [],
            'experience': [],
            'projects': [],
            'certifications': [],
            'metadata': {
                'parsing_method': 'rule_based',
                'text_length': len(text),
                'sections_detected': 0
            }
        }
        
        # Extract contact information
        result['name'] = self._extract_name(text)
        result['email'] = self._extract_email(text)
        result['phone'] = self._extract_phone(text)
        result['linkedin'] = self._extract_linkedin(text)
        result['github'] = self._extract_github(text)
        
        # Tokenize text into sections
        sections = self._tokenize_sections(text)
        result['metadata']['sections_detected'] = len(sections)
        
        # Extract information from each section
        for section_name, section_content in sections.items():
            if section_name == 'skills':
                result['skills'].extend(self._extract_skills(section_content))
            elif section_name == 'education':
                result['education'].extend(self._extract_education(section_content))
            elif section_name == 'experience':
                result['experience'].extend(self._extract_experience(section_content))
            elif section_name == 'projects':
                result['projects'].extend(self._extract_projects(section_content))
            elif section_name == 'certifications':
                result['certifications'].extend(self._extract_certifications(section_content))
        
        # Remove duplicates and clean up
        result['skills'] = list(set(result['skills']))[:20]  # Limit to 20 skills
        
        return result
    
    def _extract_name(self, text: str) -> Optional[str]:
        """
        Extract candidate's name from resume text.
        
        Args:
            text (str): Resume text
            
        Returns:
            Optional[str]: Candidate's name or None
        """
        lines = text.split('\n')[:10]  # Check first 10 lines
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines with email or phone
            if re.search(self.email_pattern, line):
                continue
            if any(pattern.search(line) for pattern in self.phone_patterns):
                continue
            
            # Check if line looks like a name (more flexible matching)
            words = line.split()
            if 1 <= len(words) <= 5:  # Allow single names or longer names
                # Check if it's mostly alphabetic (allow some special chars)
                clean_line = re.sub(r'[^A-Za-z\s]', '', line).strip()
                if clean_line and len(clean_line) >= 3:
                    # Avoid common section headers and locations
                    exclude_keywords = ['resume', 'cv', 'curriculum', 'vitae', 'profile', 
                                      'seattle', 'washington', 'wa', 'texas', 'university',
                                      'education', 'experience', 'skills', 'projects']
                    if not any(keyword in line.lower() for keyword in exclude_keywords):
                        # Prefer lines with multiple words that look like names
                        if len(words) >= 2 and all(len(word) >= 2 for word in words[:3]):
                            return line
                        # Also consider single names if they're capitalized
                        elif len(words) == 1 and line[0].isupper() and len(line) >= 4:
                            return line
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """
        Extract email address from resume text.
        
        Args:
            text (str): Resume text
            
        Returns:
            Optional[str]: Email address or None
        """
        match = self.email_pattern.search(text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """
        Extract phone number from resume text.
        
        Args:
            text (str): Resume text
            
        Returns:
            Optional[str]: Formatted phone number or None
        """
        for pattern in self.phone_patterns:
            match = pattern.search(text)
            if match:
                if len(match.groups()) >= 3:
                    # Format as (XXX) XXX-XXXX
                    return f"({match.group(1)}) {match.group(2)}-{match.group(3)}"
                else:
                    return match.group(0)
        
        return None
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """
        Extract LinkedIn profile URL from resume text.
        
        Args:
            text (str): Resume text
            
        Returns:
            Optional[str]: LinkedIn URL or None
        """
        for pattern in self.linkedin_patterns:
            match = pattern.search(text)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """
        Extract GitHub profile URL from resume text.
        
        Args:
            text (str): Resume text
            
        Returns:
            Optional[str]: GitHub URL or None
        """
        for pattern in self.github_patterns:
            match = pattern.search(text)
            if match:
                return match.group(0)
        
        return None
    
    def _tokenize_sections(self, text: str) -> Dict[str, str]:
        """
        Tokenize resume text into labeled sections.
        
        Args:
            text (str): Resume text
            
        Returns:
            Dict[str, str]: Dictionary mapping section names to content
        """
        sections = {}
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            is_header, section_name, confidence = self.taxonomy.is_section_header(line)
            
            if is_header and confidence > 0.7:
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = section_name
                current_content = []
            elif current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from skills section.
        
        Args:
            text (str): Skills section text
            
        Returns:
            List[str]: List of extracted skills
        """
        skills = set()
        all_skill_keywords = self.taxonomy.get_all_skill_keywords()
        
        # Extract skills using keyword matching (case insensitive)
        text_lower = text.lower()
        for skill in all_skill_keywords:
            if skill.lower() in text_lower:
                skills.add(skill.title())
        
        # Extract from structured skill lines (Languages:, Libraries:, etc.)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for category-based skill listings
            if ':' in line and any(cat in line.lower() for cat in ['language', 'framework', 'librar', 'cloud', 'database', 'tool']):
                # Extract skills after the colon
                parts = line.split(':', 1)
                if len(parts) > 1:
                    skill_text = parts[1].strip()
                    # Split by various delimiters
                    potential_skills = re.split(r'[,|\|\u2022]', skill_text)
                    for skill in potential_skills:
                        skill = skill.strip()
                        if 2 <= len(skill) <= 25 and skill.replace(' ', '').replace('-', '').replace('.', '').isalnum():
                            skills.add(skill)
            
            # Extract comma-separated skills from any line
            elif ',' in line and len(line.split(',')) >= 3:
                potential_skills = [s.strip() for s in line.split(',')]
                for skill in potential_skills:
                    if 2 <= len(skill) <= 25 and not any(char.isdigit() for char in skill[:3]):
                        # Filter out common non-skills
                        if not any(word in skill.lower() for word in ['and', 'or', 'with', 'using', 'from', 'the']):
                            skills.add(skill)
            
            # Extract skills separated by pipes |                            
            elif '|' in line:
                potential_skills = [s.strip() for s in line.split('|')]
                for skill in potential_skills:
                    if 2 <= len(skill) <= 25:
                        skills.add(skill)
        
        # Additional extraction for common technical terms
        tech_pattern = r'\b(?:Python|Java|JavaScript|React|Node\.js|Django|Flask|AWS|Azure|Docker|Kubernetes|SQL|NoSQL|MongoDB|PostgreSQL|MySQL|Git|GitHub|TensorFlow|PyTorch|scikit-learn|Pandas|NumPy|HTML|CSS|TypeScript|Angular|Vue\.js|Spring|Laravel|PHP|Ruby|Go|Rust|C\+\+|C#|\.NET|Scala|Kotlin|Swift|Objective-C|MATLAB|R|Tableau|PowerBI|Elasticsearch|Redis|GraphQL|REST|API|Microservices|Jenkins|CI/CD|Linux|Unix|Windows|MacOS|Agile|Scrum|JIRA|Confluence|Slack|Zoom|Teams)\b'
        tech_matches = re.findall(tech_pattern, text, re.IGNORECASE)
        for match in tech_matches:
            skills.add(match)
        
        # Clean up and return
        cleaned_skills = []
        for skill in skills:
            # Remove common prefixes/suffixes
            skill = re.sub(r'^(and|or|with|using)\s+', '', skill, flags=re.IGNORECASE)
            skill = skill.strip()
            if skill and len(skill) >= 2:
                cleaned_skills.append(skill)
        
        return list(set(cleaned_skills))[:25]  # Limit to 25 skills and remove duplicates
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract education information from education section.
        
        Args:
            text (str): Education section text
            
        Returns:
            List[Dict[str, Any]]: List of education entries
        """
        education = []
        lines = text.split('\n')
        
        # Look for degree patterns - more flexible
        degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'bs', 'ms', 'ba', 'ma', 'mba', 'btech', 'bsc', 'msc']
        year_pattern = r'\b(19|20)\d{2}\b'
        date_range_pattern = r'\b\d{2}/\d{4}[–-]\s*\d{2}/\d{4}\b'
        
        current_entry = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for degree or institution first
            has_degree = any(keyword in line.lower() for keyword in degree_keywords)
            has_university = 'university' in line.lower() or 'college' in line.lower() or 'institute' in line.lower() or 'school' in line.lower()
            
            # If we find a degree or university, start a new entry
            if has_degree or has_university:
                if current_entry:
                    education.append(current_entry)
                
                current_entry = {
                    'degree': None,
                    'institution': None,
                    'year': None,
                    'field_of_study': None,
                    'location': None,
                    'raw_text': line
                }
                
                if has_degree:
                    current_entry['degree'] = line
                if has_university:
                    current_entry['institution'] = line
            
            elif current_entry:
                # Continue building current entry
                if not current_entry['degree'] and has_degree:
                    current_entry['degree'] = line
                elif not current_entry['institution'] and has_university:
                    current_entry['institution'] = line
                
                # Extract year from any line
                year_match = re.search(year_pattern, line)
                date_range_match = re.search(date_range_pattern, line)
                
                if year_match and not current_entry['year']:
                    current_entry['year'] = year_match.group(0)
                elif date_range_match and not current_entry['year']:
                    current_entry['year'] = date_range_match.group(0)
                
                # Extract location (city, state)
                if re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', line):
                    current_entry['location'] = line
                
                # Field of study detection
                field_keywords = ['computer science', 'data analytics', 'finance', 'engineering', 'business']
                for field in field_keywords:
                    if field in line.lower() and not current_entry['field_of_study']:
                        current_entry['field_of_study'] = field.title()
        
        # Add last entry
        if current_entry:
            education.append(current_entry)
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience information from experience section.
        
        Args:
            text (str): Experience section text
            
        Returns:
            List[Dict[str, Any]]: List of experience entries
        """
        experience = []
        lines = text.split('\n')
        
        # Enhanced patterns for job detection
        job_title_keywords = ['engineer', 'developer', 'analyst', 'manager', 'assistant', 'director', 
                            'coordinator', 'specialist', 'consultant', 'researcher', 'intern']
        date_patterns = [
            r'\b\d{2}/\d{4}[–-]\s*\d{2}/\d{4}\b',  # MM/YYYY-MM/YYYY
            r'\b(19|20)\d{2}[–-]\s*(19|20)\d{2}\b',  # YYYY-YYYY
            r'\b\d{2}/\d{4}[–-]\s*\w+\s*\d{4}\b'  # MM/YYYY-Month YYYY
        ]
        
        current_entry = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Look for job titles (not starting with bullet points)
            if not line.startswith(('•', '◦', '-', '*')) and any(keyword in line.lower() for keyword in job_title_keywords):
                # Save previous entry
                if current_entry:
                    experience.append(current_entry)
                
                current_entry = {
                    'title': line,
                    'company': None,
                    'duration': None,
                    'location': None,
                    'description': [],
                    'raw_text': line
                }
            
            elif current_entry:
                # Look for company/institution name (usually next line or contains university)
                if not current_entry['company'] and not line.startswith(('•', '◦', '-', '*')):
                    if 'university' in line.lower() or 'corp' in line.lower() or 'inc' in line.lower() or 'llc' in line.lower():
                        current_entry['company'] = line
                    # Also check if line has location pattern
                    elif re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', line):
                        # This might be company with location
                        if not current_entry['location']:
                            current_entry['company'] = line
                
                # Look for dates
                if not current_entry['duration']:
                    for pattern in date_patterns:
                        if re.search(pattern, line):
                            current_entry['duration'] = line
                            break
                
                # Look for location
                if not current_entry['location'] and re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', line):
                    current_entry['location'] = line
                
                # Collect bullet points as description
                if line.startswith(('•', '◦', '-', '*')):
                    current_entry['description'].append(line)
                # Also collect non-bullet lines that look like descriptions
                elif len(line) > 50 and not any(keyword in line.lower() for keyword in job_title_keywords):
                    current_entry['description'].append(line)
        
        # Add last entry
        if current_entry:
            experience.append(current_entry)
        
        return experience
    
    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract project information from projects section.
        
        Args:
            text (str): Projects section text
            
        Returns:
            List[Dict[str, Any]]: List of project entries
        """
        projects = []
        lines = text.split('\n')
        
        current_project = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for project titles - lines that don't start with bullets and contain project indicators
            if not line.startswith(('•', '◦', '-', '*')) and len(line) < 120:
                # Check if it looks like a project title
                project_indicators = ['demo link', 'live app', 'github', 'project', 'app', 'system', 'platform', 'tool']
                has_link = 'demo link' in line.lower() or 'live app' in line.lower() or 'github' in line.lower()
                looks_like_title = len(line.split()) <= 8 and not any(word in line.lower() for word in ['using', 'with', 'and', 'the', 'implemented'])
                
                if has_link or (looks_like_title and any(indicator in line.lower() for indicator in project_indicators)):
                    # Save previous project
                    if current_project:
                        projects.append(current_project)
                    
                    # Extract just the project name (before Demo Link or Live App)
                    project_name = re.split(r'\s+demo link|\s+live app', line, flags=re.IGNORECASE)[0].strip()
                    if project_name.endswith('-'):
                        project_name = project_name[:-1].strip()
                    
                    current_project = {
                        'name': project_name,
                        'description': [],
                        'technologies': [],
                        'links': [],
                        'raw_text': line
                    }
                    
                    # Extract links from the title line
                    if 'demo link' in line.lower() or 'live app' in line.lower():
                        current_project['links'].append(line)
            
            elif current_project:
                # Collect bullet points as description
                if line.startswith(('•', '◦', '-', '*')):
                    current_project['description'].append(line)
                # Also collect longer descriptive lines
                elif len(line) > 30 and not line.startswith(('•', '◦', '-', '*')):
                    current_project['description'].append(line)
                
                # Extract technologies mentioned in the description
                tech_pattern = r'\b(?:Python|Java|JavaScript|React|Node\.js|Django|Flask|FastAPI|AWS|Azure|Docker|Kubernetes|SQL|NoSQL|MongoDB|PostgreSQL|MySQL|Git|GitHub|TensorFlow|PyTorch|scikit-learn|Pandas|NumPy|HTML|CSS|TypeScript|Angular|Vue\.js|Spring|Laravel|PHP|Ruby|Go|Rust|C\+\+|C#|\.NET|OpenCV|Whisper|GPT|LLM|API|REST|GraphQL|Microservices|Jenkins|CI/CD|Linux|Unix|Tailwind|Bootstrap|Groq|OpenAI|Gemini|LLaVA|VGG16|ResNet|CNN|Deep Learning|Machine Learning|AI|NLP|Computer Vision)\b'
                tech_matches = re.findall(tech_pattern, line, re.IGNORECASE)
                for tech in tech_matches:
                    if tech not in current_project['technologies']:
                        current_project['technologies'].append(tech)
        
        # Add last project
        if current_project:
            projects.append(current_project)
        
        return projects
    
    def _extract_certifications(self, text: str) -> List[str]:
        """
        Extract certifications from certifications section.
        
        Args:
            text (str): Certifications section text
            
        Returns:
            List[str]: List of certifications
        """
        certifications = []
        lines = text.split('\n')
        
        # Enhanced certification patterns
        cert_patterns = [
            r'\b(?:AWS|Azure|Google Cloud|GCP)\s+[A-Za-z\s]+',
            r'\bCertified\s+[A-Za-z\s]+',
            r'\b(?:PMP|CISSP|CISM|CompTIA|ITIL|CPA|CFA)\b.*',
            r'\b[A-Za-z\s]+\s+Certification\b',
            r'\bPrompt Design in [A-Za-z\s,]+',
            r'\bKnowledge Graphs for [A-Za-z\s,]+',
            r'\bFinetuning [A-Za-z\s,]+',
            r'\bAI Agents [A-Za-z\s,]+'
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove bullet points and leading symbols
            cleaned_line = re.sub(r'^[•◦\-\*▪▫]\s*', '', line)
            
            # Check against patterns
            found_match = False
            for pattern in cert_patterns:
                matches = re.findall(pattern, cleaned_line, re.IGNORECASE)
                for match in matches:
                    certifications.append(match.strip())
                    found_match = True
            
            # If no pattern matches but line looks like a certification
            if not found_match:
                cert_keywords = ['certificate', 'certification', 'certified', 'credential', 'license']
                provider_keywords = ['google', 'aws', 'azure', 'microsoft', 'oracle', 'deeplearning.ai', 'hugging face', 'coursera', 'udacity', 'edx']
                
                if (any(keyword in cleaned_line.lower() for keyword in cert_keywords) or 
                    any(provider in cleaned_line.lower() for provider in provider_keywords)) and len(cleaned_line) < 150:
                    certifications.append(cleaned_line)
                
                # Also catch lines that mention specific technologies with provider names
                elif any(provider in cleaned_line.lower() for provider in provider_keywords) and len(cleaned_line) < 100:
                    certifications.append(cleaned_line)
        
        # Clean up certifications
        cleaned_certs = []
        for cert in certifications:
            cert = cert.strip()
            # Remove trailing punctuation and clean up
            cert = re.sub(r'[,|]+$', '', cert)
            if cert and len(cert) > 5:  # Filter out very short matches
                cleaned_certs.append(cert)
        
        return list(set(cleaned_certs))  # Remove duplicates


# Example usage and testing
if __name__ == "__main__":
    # Sample resume text for testing
    sample_resume = """
    John Smith
    john.smith@email.com
    (555) 123-4567
    linkedin.com/in/johnsmith
    
    Professional Experience
    Senior Software Engineer | TechCorp Inc | 2020-2023
    • Developed web applications using Python and React
    • Led a team of 5 developers
    • Implemented CI/CD pipelines
    
    Technical Skills
    Programming Languages: Python, JavaScript, Java, C++
    Frameworks: React, Django, Flask, Spring Boot
    Cloud: AWS, Azure, Docker, Kubernetes
    
    Education
    Bachelor of Science in Computer Science
    Stanford University | 2018
    
    Projects
    E-commerce Platform
    • Built scalable web application using React and Django
    • Integrated payment processing with Stripe
    
    Certifications
    AWS Certified Solutions Architect
    Certified Kubernetes Administrator
    """
    
    parser = RuleBasedParser()
    result = parser.parse(sample_resume)
    
    print("Rule-Based Parser Results:")
    print(json.dumps(result, indent=2))