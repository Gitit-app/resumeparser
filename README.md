# Resume Parser POC - Comprehensive Resume Analysis Tool

A powerful, dual-mode resume parser that combines traditional rule-based parsing with advanced semantic analysis using FAISS similarity search.

## 🚀 Live Demo

**Web Interface**: [https://resumeparser.onrender.com](https://resumeparser.onrender.com)

## 🌟 Features

### **Dual Parsing Architecture**
- **Rule-Based Parser**: Fast pattern matching with regex and keyword taxonomy
- **Semantic Parser**: AI-powered analysis using FAISS similarity search and sentence transformers

### **Comprehensive Extraction**
- **Contact Information**: Name, email, phone, LinkedIn, GitHub
- **Technical Skills**: Programming languages, frameworks, tools, databases
- **Education**: Degrees, institutions, graduation years, fields of study
- **Experience**: Job titles, companies, dates, descriptions
- **Projects**: Project names, descriptions, technologies used
- **Certifications**: Professional certifications and credentials

### **File Format Support**
- **PDF**: Advanced text extraction using PyMuPDF
- **DOCX**: Microsoft Word document processing
- **TXT**: Plain text file processing

### **Modern Web Interface**
- **Glassmorphism Design**: Beautiful, modern UI with blur effects
- **Drag & Drop**: Intuitive file upload interface
- **Real-time Processing**: Instant parsing results
- **JSON Visualization**: Clean, structured output display
- **Responsive Design**: Works on desktop and mobile

## 📋 Requirements

### **Core Dependencies**
- Python 3.8+
- Flask 2.0+
- NumPy 1.21+
- scikit-learn 1.0+

### **File Processing**
- PyMuPDF 1.20+ (PDF extraction)
- python-docx 0.8.11+ (DOCX processing)

### **Semantic Analysis** (Optional)
- sentence-transformers 2.2+
- faiss-cpu 1.7.2+
- torch 1.9+
- transformers 4.20+

## 🛠️ Installation

### **1. Clone Repository**
```bash
git clone https://github.com/Gitit-app/resumeparser.git
cd resumeparser
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set Environment Variables** (Optional)
```bash
export HUGGINGFACE_HUB_TOKEN=your_token_here  # For semantic parsing
```

## 🚀 Usage

### **Web Interface**
```bash
python web_app.py
```
Visit: http://localhost:5000

### **Command Line Interface**
```bash
python main.py path/to/resume.pdf --method rule
python main.py path/to/resume.pdf --method semantic
```

### **API Usage**
```bash
# Health check
curl https://resumeparser.onrender.com/health

# Parse resume
curl -X POST -F "file=@resume.pdf" -F "method=rule" https://resumeparser.onrender.com/api/parse
```

## 🎯 Parsing Methods

### **Rule-Based Parser**
- **Best for**: Standardized resume formats
- **Speed**: Very fast (< 1 second)
- **Accuracy**: High for structured resumes
- **Resource Usage**: Lightweight

### **Semantic Parser**
- **Best for**: Non-standard, creative formats
- **Speed**: Moderate (2-5 seconds)
- **Accuracy**: High for all formats
- **Resource Usage**: Moderate (requires ML models)

## 📊 Example Output

```json
{
  "name": "John Smith",
  "email": "john.smith@email.com",
  "phone": "(555) 123-4567",
  "linkedin": "linkedin.com/in/johnsmith",
  "skills": ["Python", "JavaScript", "React", "AWS"],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "institution": "Stanford University",
      "year": "2020"
    }
  ],
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Tech Corp",
      "duration": "2020-2023",
      "description": ["Developed web applications", "Led team of 5 developers"]
    }
  ]
}
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Interface                            │
│                   (Flask + HTML/CSS/JS)                        │
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                      Core Components                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   File Loader   │  │    Taxonomy     │  │   Web Server    │ │
│  │ (PDF/DOCX/TXT)  │  │   (Keywords)    │  │   (Flask API)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                     Parsing Engines                            │
│  ┌─────────────────┐              ┌─────────────────┐           │
│  │  Rule-Based     │              │   Semantic      │           │
│  │   Parser        │              │   Parser        │           │
│  │                 │              │                 │           │
│  │ • Regex         │              │ • FAISS         │           │
│  │ • Keywords      │              │ • Transformers  │           │
│  │ • Patterns      │              │ • Embeddings    │           │
│  └─────────────────┘              └─────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## 🌐 Deployment

### **Deploy to Render**
1. Fork this repository
2. Connect to Render
3. Select the `render.yaml` blueprint
4. Set environment variables:
   - `HUGGINGFACE_HUB_TOKEN` (optional)
   - `FLASK_ENV=production`

### **Deploy to Heroku**
```bash
heroku create your-app-name
git push heroku main
```

### **Deploy to Railway**
```bash
railway login
railway init
railway deploy
```

## 🔧 Configuration

### **Environment Variables**
- `HUGGINGFACE_HUB_TOKEN`: HuggingFace token for model downloads
- `FLASK_ENV`: Set to 'production' for production deployment
- `PORT`: Server port (default: 5000)

### **File Limits**
- Maximum file size: 16MB
- Supported formats: PDF, DOCX, TXT

## 🧪 Testing

```bash
# Run example parser
python examples/test_parser.py

# Test with sample resumes
python main.py examples/sample_resume_1.txt --method rule
python main.py examples/sample_resume_2.txt --method semantic
```

## 📈 Performance

| Method | Speed | Memory | Accuracy |
|--------|-------|---------|----------|
| Rule-Based | < 1s | Low | High (structured) |
| Semantic | 2-5s | Moderate | High (all formats) |

## 🔐 Security

- File validation and sanitization
- Secure filename handling
- Temporary file cleanup
- Environment variable configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🎯 Use Cases

- **HR Systems**: Automated resume screening
- **Recruitment Platforms**: Candidate profile generation
- **ATS Integration**: Applicant tracking systems
- **Data Migration**: Legacy system modernization
- **Research**: Resume analysis and insights

---

**Built with modern Python architecture and production-ready deployment capabilities.**