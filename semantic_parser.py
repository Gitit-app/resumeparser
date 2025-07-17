#!/usr/bin/env python3
"""
Semantic Parser Module for Resume Parser POC

This module implements a semantic-based approach for parsing resumes using
FAISS similarity search and pre-trained sentence transformers for contextual understanding.

Author: Resume Parser POC
Version: 1.0
"""

import re
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from taxonomy import ResumeTaxonomy

# Required imports for semantic parsing
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class SemanticParser:
    """
    A semantic resume parser that uses FAISS for fast similarity search
    and sentence transformers for contextual understanding of resume content.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic parser with FAISS indices and transformer model.
        
        Args:
            model_name (str): Name of the sentence transformer model to use
        """
        self.taxonomy = ResumeTaxonomy()
        self.model_name = model_name
        self.model = None
        self.faiss_indices = {}
        self.field_mappings = {}
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        
        # Check if dependencies are available
        if not FAISS_AVAILABLE or not TRANSFORMERS_AVAILABLE:
            missing = []
            if not FAISS_AVAILABLE:
                missing.append("faiss-cpu")
            if not TRANSFORMERS_AVAILABLE:
                missing.append("sentence-transformers")
            raise ImportError(f"Missing dependencies for semantic parsing: {', '.join(missing)}")
        
        # Initialize model and FAISS indices
        self._initialize_model()
        self._build_faiss_indices()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            print(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"✅ Model loaded successfully: {self.model_name} (embedding_dim: {self.embedding_dim})")
        except Exception as e:
            raise Exception(f"Failed to load model {self.model_name}: {e}")
    
    def _build_faiss_indices(self):
        """Build FAISS indices for each resume field category."""
        print("🔧 Building FAISS indices for semantic search...")
        
        # Build indices for section headers
        for field_name, synonyms in self.taxonomy.SECTION_TAXONOMY.items():
            self._create_field_index(f"section_{field_name}", synonyms)
        
        # Build indices for technical skills
        for category, skills in self.taxonomy.TECHNICAL_SKILLS.items():
            self._create_field_index(f"skill_{category}", skills)
        
        # Build index for common job titles
        job_titles = [
            "Software Engineer", "Senior Software Engineer", "Software Developer",
            "Full Stack Developer", "Frontend Developer", "Backend Developer",
            "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
            "Product Manager", "Technical Lead", "Engineering Manager",
            "System Administrator", "Database Administrator", "Cloud Architect"
        ]
        self._create_field_index("job_titles", job_titles)
        
        # Build index for educational institutions
        institutions = [
            "University", "College", "Institute of Technology", "Technical College",
            "Community College", "State University", "Private University"
        ]
        self._create_field_index("institutions", institutions)
        
        print(f"🎯 Successfully built {len(self.faiss_indices)} FAISS indices for semantic search")
    
    def _create_field_index(self, field_name: str, texts: List[str]):
        """
        Create a FAISS index for a specific field.
        
        Args:
            field_name (str): Name of the field
            texts (List[str]): List of texts to index
        """
        if not texts:
            return
        
        try:
            # Generate embeddings using sentence transformer
            print(f"  Generating embeddings for {field_name}...")
            embeddings = self.model.encode(texts, show_progress_bar=False)
            embeddings = embeddings.astype('float32')
            
            # Create FAISS index for similarity search
            index = faiss.IndexFlatL2(self.embedding_dim)
            index.add(embeddings)
            
            # Store index and mappings
            self.faiss_indices[field_name] = index
            self.field_mappings[field_name] = texts
            
            print(f"  ✅ Index created for {field_name}: {len(texts)} items")
            
        except Exception as e:
            raise Exception(f"Failed to create index for {field_name}: {e}")
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text using semantic analysis and FAISS similarity search.
        
        Args:
            text (str): Raw resume text
            
        Returns:
            Dict[str, Any]: Structured resume data
        """
        print("🧠 Starting semantic parsing with FAISS similarity search...")
        
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
                'parsing_method': 'semantic_faiss',
                'model_used': self.model_name,
                'text_length': len(text),
                'chunks_processed': 0,
                'semantic_scores': {}
            }
        }
        
        # Extract basic contact information (still use regex for these)
        result['name'] = self._extract_name(text)
        result['email'] = self._extract_email(text)
        result['phone'] = self._extract_phone(text)
        result['linkedin'] = self._extract_linkedin(text)
        result['github'] = self._extract_github(text)
        
        # Create semantic chunks
        chunks = self._create_semantic_chunks(text)
        result['metadata']['chunks_processed'] = len(chunks)
        
        # Classify chunks using FAISS
        classified_chunks = self._classify_chunks_with_faiss(chunks)
        
        # Extract structured information from classified chunks
        result['skills'] = self._extract_skills_semantic(classified_chunks)
        result['education'] = self._extract_education_semantic(classified_chunks)
        result['experience'] = self._extract_experience_semantic(classified_chunks)
        result['projects'] = self._extract_projects_semantic(classified_chunks)
        result['certifications'] = self._extract_certifications_semantic(classified_chunks)
        
        return result
    
    def _create_semantic_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Create semantic chunks from resume text.
        
        Args:
            text (str): Resume text
            
        Returns:
            List[Dict[str, Any]]: List of text chunks with metadata
        """
        chunks = []
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        
        for para in paragraphs:
            para = para.strip()
            if len(para) < 20:  # Skip very short paragraphs
                continue
            
            # Further split long paragraphs
            if len(para) > 500:
                sentences = re.split(r'[.!?]+', para)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    if len(current_chunk) + len(sentence) < 300:
                        current_chunk += " " + sentence if current_chunk else sentence
                    else:
                        if current_chunk:
                            chunks.append({
                                'text': current_chunk,
                                'length': len(current_chunk),
                                'type': 'sentence_group'
                            })
                        current_chunk = sentence
                
                if current_chunk:
                    chunks.append({
                        'text': current_chunk,
                        'length': len(current_chunk),
                        'type': 'sentence_group'
                    })
            else:
                chunks.append({
                    'text': para,
                    'length': len(para),
                    'type': 'paragraph'
                })
        
        return chunks
    
    def _classify_chunks_with_faiss(self, chunks: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Classify text chunks using FAISS similarity search.
        
        Args:
            chunks (List[Dict[str, Any]]): List of text chunks
            
        Returns:
            Dict[str, List[Dict]]: Classified chunks by category
        """
        classified = {
            'skills': [],
            'education': [],
            'experience': [],
            'projects': [],
            'certifications': [],
            'unknown': []
        }
        
        for chunk in chunks:
            try:
                # Generate embedding for the chunk
                chunk_embedding = self.model.encode([chunk['text']])[0]
                
                # Find best matching field
                best_field, best_score = self._find_best_field_match(chunk_embedding)
                
                # Classify based on field match
                chunk['best_field'] = best_field
                chunk['confidence'] = best_score
                
                if best_score > 0.7:  # High confidence threshold
                    if 'section_skills' in best_field:
                        classified['skills'].append(chunk)
                    elif 'section_education' in best_field:
                        classified['education'].append(chunk)
                    elif 'section_experience' in best_field:
                        classified['experience'].append(chunk)
                    elif 'section_projects' in best_field:
                        classified['projects'].append(chunk)
                    elif 'section_certifications' in best_field:
                        classified['certifications'].append(chunk)
                    else:
                        classified['unknown'].append(chunk)
                elif best_score > 0.5:  # Medium confidence - check content
                    category = self._classify_by_content(chunk['text'])
                    classified[category].append(chunk)
                else:
                    classified['unknown'].append(chunk)
                    
            except Exception as e:
                print(f"Error classifying chunk: {e}")
                classified['unknown'].append(chunk)
        
        return classified
    
    def _find_best_field_match(self, embedding: np.ndarray) -> Tuple[str, float]:
        """
        Find the best matching field for an embedding using FAISS.
        
        Args:
            embedding (np.ndarray): Text embedding
            
        Returns:
            Tuple[str, float]: Best field name and similarity score
        """
        best_field = "unknown"
        best_score = 0.0
        
        embedding = embedding.reshape(1, -1).astype('float32')
        
        for field_name, index in self.faiss_indices.items():
            try:
                # Search for nearest neighbors
                distances, indices = index.search(embedding, k=1)
                
                # Convert L2 distance to similarity score
                distance = distances[0][0]
                similarity = 1.0 / (1.0 + distance)
                
                if similarity > best_score:
                    best_score = similarity
                    best_field = field_name
                    
            except Exception as e:
                print(f"Error searching in index {field_name}: {e}")
        
        return best_field, best_score
    
    def _classify_by_content(self, text: str) -> str:
        """
        Classify text by content analysis when FAISS classification is uncertain.
        
        Args:
            text (str): Text to classify
            
        Returns:
            str: Classification category
        """
        text_lower = text.lower()
        
        # Skill indicators
        skill_indicators = ['programming', 'languages', 'technologies', 'framework', 'library']
        if any(indicator in text_lower for indicator in skill_indicators):
            return 'skills'
        
        # Education indicators
        edu_indicators = ['university', 'college', 'degree', 'bachelor', 'master', 'phd']
        if any(indicator in text_lower for indicator in edu_indicators):
            return 'education'
        
        # Experience indicators
        exp_indicators = ['engineer', 'developer', 'manager', 'analyst', 'company', 'role']
        if any(indicator in text_lower for indicator in exp_indicators):
            return 'experience'
        
        # Project indicators
        proj_indicators = ['project', 'built', 'developed', 'created', 'implemented']
        if any(indicator in text_lower for indicator in proj_indicators):
            return 'projects'
        
        # Certification indicators
        cert_indicators = ['certified', 'certification', 'license', 'credential']
        if any(indicator in text_lower for indicator in cert_indicators):
            return 'certifications'
        
        return 'unknown'
    
    def _extract_skills_semantic(self, classified_chunks: Dict[str, List[Dict]]) -> List[str]:
        """
        Extract skills using semantic analysis.
        
        Args:
            classified_chunks (Dict[str, List[Dict]]): Classified text chunks
            
        Returns:
            List[str]: List of extracted skills
        """
        all_skills = set()
        
        # Look in skills chunks first
        skill_chunks = classified_chunks.get('skills', [])
        for chunk in skill_chunks:
            skills = self._extract_individual_skills(chunk['text'])
            all_skills.update(skills)
        
        # Also check other chunks for skills mentions
        for category in ['experience', 'projects', 'unknown']:
            for chunk in classified_chunks.get(category, []):
                skills = self._extract_individual_skills(chunk['text'])
                all_skills.update(skills)
        
        return list(all_skills)[:25]  # Limit to 25 skills
    
    def _categorize_skill_semantic(self, skill: str) -> str:
        """
        Categorize a skill using semantic similarity.
        
        Args:
            skill (str): Skill to categorize
            
        Returns:
            str: Skill category
        """
        try:
            skill_embedding = self.model.encode([skill])[0]
            
            best_category = 'other'
            best_score = 0.0
            
            # Check against skill category indices
            for field_name, index in self.faiss_indices.items():
                if field_name.startswith('skill_'):
                    embedding = skill_embedding.reshape(1, -1).astype('float32')
                    distances, indices = index.search(embedding, k=1)
                    
                    distance = distances[0][0]
                    similarity = 1.0 / (1.0 + distance)
                    
                    if similarity > best_score and similarity > 0.6:
                        best_score = similarity
                        best_category = field_name.replace('skill_', '')
            
            return best_category
            
        except Exception as e:
            print(f"Error categorizing skill {skill}: {e}")
            return 'other'
    
    def _extract_individual_skills(self, text: str) -> List[str]:
        """
        Extract individual skills from text.
        
        Args:
            text (str): Text containing skills
            
        Returns:
            List[str]: List of extracted skills
        """
        skills = set()
        
        # Use taxonomy for skill extraction
        all_skills = self.taxonomy.get_all_skill_keywords()
        text_lower = text.lower()
        
        for skill in all_skills:
            if skill in text_lower:
                skills.add(skill.title())
        
        # Extract comma-separated skills
        lines = text.split('\n')
        for line in lines:
            if ',' in line and len(line.split(',')) > 2:
                potential_skills = [s.strip() for s in line.split(',')]
                for skill in potential_skills:
                    if 2 <= len(skill) <= 30 and not any(char.isdigit() for char in skill):
                        skills.add(skill)
        
        return list(skills)
    
    def _extract_education_semantic(self, classified_chunks: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """
        Extract education information using semantic analysis.
        
        Args:
            classified_chunks (Dict[str, List[Dict]]): Classified text chunks
            
        Returns:
            List[Dict[str, Any]]: List of education entries
        """
        education = []
        edu_chunks = classified_chunks.get('education', [])
        
        for chunk in edu_chunks:
            edu_entry = {
                'degree': None,
                'institution': None,
                'year': None,
                'field_of_study': None,
                'semantic_confidence': chunk.get('confidence', 0.0),
                'raw_text': chunk['text']
            }
            
            # Extract degree using regex
            degree_patterns = self.taxonomy.EDUCATION_PATTERNS['degrees']
            for pattern in degree_patterns:
                match = re.search(pattern, chunk['text'], re.IGNORECASE)
                if match:
                    edu_entry['degree'] = match.group(0)
                    break
            
            # Extract year
            year_match = re.search(r'\b(19|20)\d{2}\b', chunk['text'])
            if year_match:
                edu_entry['year'] = year_match.group(0)
            
            # Extract institution using semantic similarity
            edu_entry['institution'] = self._find_institution_semantic(chunk['text'])
            
            education.append(edu_entry)
        
        return education
    
    def _find_institution_semantic(self, text: str) -> Optional[str]:
        """
        Find educational institution using semantic similarity.
        
        Args:
            text (str): Text containing institution information
            
        Returns:
            Optional[str]: Institution name or None
        """
        if 'institutions' not in self.faiss_indices:
            return None
        
        try:
            text_embedding = self.model.encode([text])[0]
            embedding = text_embedding.reshape(1, -1).astype('float32')
            
            distances, indices = self.faiss_indices['institutions'].search(embedding, k=1)
            
            distance = distances[0][0]
            similarity = 1.0 / (1.0 + distance)
            
            if similarity > 0.6:
                idx = indices[0][0]
                return self.field_mappings['institutions'][idx]
            
        except Exception as e:
            print(f"Error finding institution: {e}")
        
        return None
    
    def _extract_experience_semantic(self, classified_chunks: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """
        Extract experience information using semantic analysis.
        
        Args:
            classified_chunks (Dict[str, List[Dict]]): Classified text chunks
            
        Returns:
            List[Dict[str, Any]]: List of experience entries
        """
        experience = []
        exp_chunks = classified_chunks.get('experience', [])
        
        for chunk in exp_chunks:
            exp_entry = {
                'title': None,
                'company': None,
                'duration': None,
                'description': [],
                'semantic_confidence': chunk.get('confidence', 0.0),
                'raw_text': chunk['text']
            }
            
            # Extract job title using semantic similarity
            exp_entry['title'] = self._find_job_title_semantic(chunk['text'])
            
            # Extract dates
            date_match = re.search(r'\b(19|20)\d{2}\b.*\b(19|20)\d{2}\b', chunk['text'])
            if date_match:
                exp_entry['duration'] = date_match.group(0)
            
            # Extract description
            lines = chunk['text'].split('\n')
            for line in lines:
                if line.strip().startswith(('•', '-', '*')):
                    exp_entry['description'].append(line.strip())
            
            experience.append(exp_entry)
        
        return experience
    
    def _find_job_title_semantic(self, text: str) -> Optional[str]:
        """
        Find job title using semantic similarity.
        
        Args:
            text (str): Text containing job title
            
        Returns:
            Optional[str]: Job title or None
        """
        if 'job_titles' not in self.faiss_indices:
            return None
        
        try:
            lines = text.split('\n')
            
            for line in lines[:3]:  # Check first few lines
                line = line.strip()
                if len(line) > 5 and len(line) < 100:
                    text_embedding = self.model.encode([line])[0]
                    embedding = text_embedding.reshape(1, -1).astype('float32')
                    
                    distances, indices = self.faiss_indices['job_titles'].search(embedding, k=1)
                    
                    distance = distances[0][0]
                    similarity = 1.0 / (1.0 + distance)
                    
                    if similarity > 0.6:
                        return line
            
        except Exception as e:
            print(f"Error finding job title: {e}")
        
        return None
    
    def _extract_projects_semantic(self, classified_chunks: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """
        Extract project information using semantic analysis.
        
        Args:
            classified_chunks (Dict[str, List[Dict]]): Classified text chunks
            
        Returns:
            List[Dict[str, Any]]: List of project entries
        """
        projects = []
        proj_chunks = classified_chunks.get('projects', [])
        
        for chunk in proj_chunks:
            project_entry = {
                'name': None,
                'description': [],
                'technologies': [],
                'semantic_confidence': chunk.get('confidence', 0.0),
                'raw_text': chunk['text']
            }
            
            lines = chunk['text'].split('\n')
            if lines:
                project_entry['name'] = lines[0].strip()
            
            # Extract description and technologies
            for line in lines[1:]:
                line = line.strip()
                if line:
                    project_entry['description'].append(line)
                    
                    # Extract technologies
                    techs = self._extract_individual_skills(line)
                    project_entry['technologies'].extend(techs)
            
            # Remove duplicates
            project_entry['technologies'] = list(set(project_entry['technologies']))
            
            projects.append(project_entry)
        
        return projects
    
    def _extract_certifications_semantic(self, classified_chunks: Dict[str, List[Dict]]) -> List[str]:
        """
        Extract certifications using semantic analysis.
        
        Args:
            classified_chunks (Dict[str, List[Dict]]): Classified text chunks
            
        Returns:
            List[str]: List of certifications
        """
        certifications = []
        cert_chunks = classified_chunks.get('certifications', [])
        
        for chunk in cert_chunks:
            lines = chunk['text'].split('\n')
            
            for line in lines:
                line = line.strip()
                if line:
                    # Remove bullet points
                    line = re.sub(r'^[•\-\*]\s*', '', line)
                    if len(line) > 5:
                        certifications.append(line)
        
        return list(set(certifications))  # Remove duplicates
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract name using regex patterns."""
        lines = text.split('\n')[:10]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines with contact info
            if '@' in line or re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line):
                continue
            
            words = line.split()
            if 2 <= len(words) <= 4:
                if all(re.match(r'^[A-Za-z\.\-]+$', word) for word in words):
                    return line
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email using regex."""
        match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone using regex."""
        patterns = [
            r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) >= 3:
                    return f"({match.group(1)}) {match.group(2)}-{match.group(3)}"
                else:
                    return match.group(0)
        
        return None
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL using regex."""
        match = re.search(r'linkedin\.com/in/[\w-]+', text)
        return match.group(0) if match else None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL using regex."""
        match = re.search(r'github\.com/[\w-]+', text)
        return match.group(0) if match else None
    
    def get_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        try:
            embeddings = self.model.encode([text1, text2])
            # Calculate cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0


# Example usage and testing
if __name__ == "__main__":
    # Sample resume text for testing
    sample_resume = """
    Jane Doe
    jane.doe@techcompany.com
    (555) 987-6543
    linkedin.com/in/janedoe
    
    Professional Experience
    Senior Machine Learning Engineer | AI Corp | 2021-2023
    • Developed deep learning models using TensorFlow and PyTorch
    • Implemented MLOps pipelines with Kubernetes and Docker
    • Led a team of 3 data scientists
    
    Technical Skills
    Programming: Python, R, SQL, JavaScript
    ML/AI: TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy
    Cloud: AWS, Google Cloud Platform, Azure
    
    Education
    Master of Science in Data Science
    MIT | 2019
    
    Projects
    Recommendation System
    • Built collaborative filtering system using Python and Redis
    • Achieved 95% accuracy in user preference prediction
    
    Certifications
    AWS Certified Machine Learning - Specialty
    Google Cloud Professional Data Engineer
    """
    
    parser = SemanticParser()
    result = parser.parse(sample_resume)
    
    print("Semantic Parser Results:")
    print(json.dumps(result, indent=2))