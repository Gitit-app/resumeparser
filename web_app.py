#!/usr/bin/env python3
"""
Web Application for Resume Parser POC - Demo Version
Works with both rule-based and semantic parsing (with proper dependencies)
"""

import os
import json
import traceback
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename

# Import parser modules
from file_loader import FileLoader
from rule_based_parser import RuleBasedParser

# Set HuggingFace token if available
# Set HUGGINGFACE_HUB_TOKEN environment variable for full semantic parsing
# export HUGGINGFACE_HUB_TOKEN=your_token_here

app = Flask(__name__)
app.secret_key = 'resume-parser-poc-secret-key'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and parsing."""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type. Only {", ".join(ALLOWED_EXTENSIONS)} files are allowed.'}), 400
        
        # Get parsing method
        parsing_method = request.form.get('method', 'rule')
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Extract text from file
            text = FileLoader.load_file(file_path)
            
            if not text or len(text.strip()) < 10:
                return jsonify({'error': 'No readable text found in the file.'}), 400
            
            # Parse based on selected method
            if parsing_method == 'rule':
                rule_parser = RuleBasedParser()
                results = rule_parser.parse(text)
            
            elif parsing_method == 'semantic':
                # Semantic parsing not available in this deployment
                return jsonify({
                    'error': 'Semantic parsing is not available in this deployment to optimize memory usage and performance. Please use rule-based parsing instead.',
                    'reason': 'Memory optimization - semantic parsing requires heavy ML dependencies',
                    'suggested_action': 'Use rule-based parsing method',
                    'rule_based_benefits': [
                        'Fast processing (< 1 second)',
                        'Low memory usage',
                        'High accuracy for structured resumes',
                        'Reliable and stable'
                    ]
                }), 400
            
            else:
                return jsonify({'error': f'Invalid parsing method: {parsing_method}'}), 400
            
            # Add file metadata
            file_info = FileLoader.get_file_info(file_path)
            results['file_info'] = {
                'filename': file_info['filename'],
                'size_kb': file_info['size_kb'],
                'extension': file_info['extension']
            }
            
            return jsonify(results)
        
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
    
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}\\n{traceback.format_exc()}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/parse', methods=['POST'])
def api_parse():
    """API endpoint for programmatic access."""
    return upload_file()

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'resume-parser-poc',
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'parsing_methods': ['rule'],
        'semantic_status': 'disabled_for_performance',
        'message': 'Optimized for rule-based parsing - fast, reliable, and memory-efficient'
    })

def categorize_skill_demo(skill):
    """Demo skill categorization for semantic parsing."""
    skill_lower = skill.lower()
    if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'c++', 'go']):
        return 'programming_languages'
    elif any(fw in skill_lower for fw in ['react', 'django', 'flask', 'angular']):
        return 'web_frameworks'
    elif any(db in skill_lower for db in ['sql', 'mongodb', 'postgresql', 'mysql']):
        return 'databases'
    elif any(cloud in skill_lower for cloud in ['aws', 'azure', 'gcp', 'docker']):
        return 'cloud_platforms'
    elif any(ml in skill_lower for ml in ['tensorflow', 'pytorch', 'scikit', 'pandas']):
        return 'machine_learning'
    else:
        return 'other'

if __name__ == '__main__':
    print("🚀 Resume Parser POC - Web Interface (Demo Version)")
    print("=" * 60)
    print("🌐 Starting web server...")
    print("📄 Supported formats: PDF, DOCX, TXT")
    print("🔗 Access URL: http://localhost:5000")
    print("📋 API endpoint: http://localhost:5000/api/parse")
    print("💊 Health check: http://localhost:5000/health")
    print("=" * 60)
    print("✅ Rule-based parsing: Available")
    print("🧠 Semantic parsing: Demo mode (enhanced rule-based)")
    print("=" * 60)
    
    # Get port from environment for production deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug, host='0.0.0.0', port=port)