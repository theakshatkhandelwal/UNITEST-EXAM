import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import json
import re
import PyPDF2
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
from datetime import datetime, timedelta
import requests

# Download NLTK data only when needed
def ensure_nltk_data():
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)

app = Flask(__name__, instance_path='/tmp')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
# Database configuration - use PostgreSQL on Vercel/NeonDB, SQLite locally
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Fix for Vercel/NeonDB PostgreSQL URL format
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
elif database_url and database_url.startswith('postgresql://'):
    # Already in correct format for NeonDB
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unittest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add SSL configuration for NeonDB
if database_url and 'neon.tech' in database_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require'
        }
    }

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Google AI
genai.configure(api_key=os.environ.get('GOOGLE_AI_API_KEY', 'AIzaSyBKYJLje8mR0VP5XxmrpG3PfXAleNXU_-c'))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased from 120 to 255
    role = db.Column(db.String(20), default='student', nullable=False)  # 'student' or 'teacher'
    is_admin = db.Column(db.Boolean, default=False, nullable=False)  # Admin access flag
    last_login = db.Column(db.DateTime)  # Last login timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    login_history = db.relationship('LoginHistory', backref='user', lazy=True, cascade='all, delete-orphan')

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    bloom_level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Shared Quiz Models
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    difficulty = db.Column(db.String(20), default='beginner')  # beginner/intermediate/advanced
    duration_minutes = db.Column(db.Integer)  # optional time limit for test
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text)  # JSON array for MCQ options like ["A. ...","B. ...","C. ...","D. ..."]
    answer = db.Column(db.String(10))  # For MCQ store letter like 'A'; for subjective can store sample answer
    qtype = db.Column(db.String(20), default='mcq')  # 'mcq', 'subjective', or 'coding'
    marks = db.Column(db.Integer, default=1)
    # For coding questions
    test_cases_json = db.Column(db.Text)  # JSON array of test cases: [{"input": "...", "expected_output": "...", "is_hidden": false}]
    language_constraints = db.Column(db.Text)  # JSON array of allowed languages: ["python", "java", "cpp", "c"]
    time_limit_seconds = db.Column(db.Integer)  # Time limit per test case
    memory_limit_mb = db.Column(db.Integer)  # Memory limit in MB
    sample_input = db.Column(db.Text)  # Sample input for display
    sample_output = db.Column(db.Text)  # Sample output for display
    starter_code = db.Column(db.Text)  # JSON object with starter code per language

class QuizSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    passed = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    # unlock review after 15 minutes
    review_unlocked_at = db.Column(db.DateTime)
    # flag if student exited fullscreen during test
    fullscreen_exit_flag = db.Column(db.Boolean, default=False)
    # counts to determine clean vs hold
    answered_count = db.Column(db.Integer, default=0)
    question_count = db.Column(db.Integer, default=0)
    is_full_completion = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

class QuizAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('quiz_submission.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_question.id'), nullable=False)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    ai_score = db.Column(db.Float)  # 0..1 for subjective
    scored_marks = db.Column(db.Float, default=0.0)
    # For coding questions
    code_language = db.Column(db.String(20))  # Language used: python, java, cpp, c
    test_results_json = db.Column(db.Text)  # JSON array of test case results
    passed_test_cases = db.Column(db.Integer, default=0)
    total_test_cases = db.Column(db.Integer, default=0)

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45))  # IPv6 can be up to 45 characters
    user_agent = db.Column(db.String(255))  # Browser/user agent string

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def evaluate_subjective_answer(question, student_answer, model_answer):
    """Use AI to evaluate subjective answers"""
    if not genai or not student_answer.strip():
        return 0.0

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Evaluate this student's answer for the given question:

        Question: {question}
        Student Answer: {student_answer}
        Model Answer: {model_answer}

        Rate the student's answer on a scale of 0.0 to 1.0 based on:
        - Accuracy and correctness
        - Completeness
        - Understanding demonstrated
        - Relevance to the question

        Return only a number between 0.0 and 1.0 (e.g., 0.8 for 80% correct)
        """

        response = model.generate_content(prompt)
        score_text = response.text.strip()

        # Extract number from response
        score_match = re.search(r'(\d*\.?\d+)', score_text)
        if score_match:
            score = float(score_match.group(1))
            return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1

        return 0.5  # Default if can't parse
    except Exception as e:
        print(f"Error in evaluate_subjective_answer: {str(e)}")
        return 0.5  # Default on error

def execute_code(code, language, test_input, time_limit=2, memory_limit=256):
    """Execute code using Piston API (free, no API key needed)"""
    piston_url = "https://emkc.org/api/v2/piston/execute"
    
    piston_languages = {
        'python': 'python3',
        'python3': 'python3',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c'
    }
    
    piston_lang = piston_languages.get(language.lower(), 'python3')
    
    try:
        payload = {
            "language": piston_lang,
            "version": "*",
            "files": [{"content": code}],
            "stdin": test_input,
            "args": [],
            "compile_timeout": 10000,
            "run_timeout": time_limit * 1000,
            "compile_memory_limit": memory_limit * 1024 * 1024,
            "run_memory_limit": memory_limit * 1024 * 1024
        }
        
        response = requests.post(piston_url, json=payload, timeout=15)
        
        if response.status_code == 200:
            try:
                result = response.json()
                if not result:
                    return {
                        'status': 'error',
                        'message': 'Empty response from execution API',
                        'output': '',
                        'stderr': ''
                    }
                
                if result.get('run'):
                    run_result = result['run']
                    if not run_result:
                        return {
                            'status': 'error',
                            'message': 'Invalid run result from API',
                            'output': '',
                            'stderr': ''
                        }
                    
                    if run_result.get('code') == 0:
                        return {
                            'status': 'success',
                            'output': run_result.get('stdout', '').strip(),
                            'stderr': run_result.get('stderr', '').strip()
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': 'Runtime Error',
                            'output': run_result.get('stdout', '').strip(),
                            'stderr': run_result.get('stderr', '').strip() or run_result.get('stdout', '')
                        }
                else:
                    # No 'run' key in response - return error
                    return {
                        'status': 'error',
                        'message': 'Unexpected API response format',
                        'output': '',
                        'stderr': str(result) if result else 'No response data'
                    }
            except (ValueError, KeyError) as e:
                return {
                    'status': 'error',
                    'message': f'Failed to parse API response: {str(e)}',
                    'output': '',
                    'stderr': ''
                }
        else:
            return {
                'status': 'error',
                'message': f'API returned status {response.status_code}',
                'output': '',
                'stderr': response.text[:200] if hasattr(response, 'text') else ''
            }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f'Network error: {str(e)}',
            'output': '',
            'stderr': ''
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Execution error: {str(e)}',
            'output': '',
            'stderr': ''
        }

def run_test_cases(code, language, test_cases, time_limit=2, memory_limit=256):
    """Run multiple test cases and return results"""
    results = []
    passed = 0
    
    for test_case in test_cases:
        test_input = test_case.get('input', '') if isinstance(test_case, dict) else ''
        expected_output = test_case.get('expected_output', '').strip() if isinstance(test_case, dict) else ''
        is_hidden = test_case.get('is_hidden', False) if isinstance(test_case, dict) else False
        
        exec_result = execute_code(code, language, test_input, time_limit, memory_limit)
        
        # Ensure exec_result is not None and is a dict
        if not exec_result or not isinstance(exec_result, dict):
            exec_result = {
                'status': 'error',
                'message': 'Execution returned invalid result',
                'output': '',
                'stderr': ''
            }
        
        if exec_result.get('status') == 'success':
            actual_output = exec_result.get('output', '').strip()
            is_correct = actual_output == expected_output
            if is_correct:
                passed += 1
        else:
            actual_output = exec_result.get('stderr', '') or exec_result.get('message', 'Error')
            is_correct = False
        
        results.append({
            'input': test_input,
            'expected_output': expected_output,
            'actual_output': actual_output,
            'is_correct': is_correct,
            'is_hidden': is_hidden
        })
    
    total = len(test_cases)
    percentage = (passed / total * 100) if total > 0 else 0
    
    return {
        'results': results,
        'passed': passed,
        'total': total,
        'percentage': percentage
    }

def get_difficulty_from_bloom_level(bloom_level):
    """Map Bloom's taxonomy level to difficulty level"""
    if bloom_level <= 2:
        return "beginner"
    elif bloom_level <= 4:
        return "intermediate"
    else:
        return "difficult"

def generate_quiz(topic, difficulty_level, question_type="mcq", num_questions=5):
    if not genai:
        return None

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Map difficulty levels to Bloom's taxonomy levels and descriptions
        difficulty_mapping = {
            "beginner": {
                "bloom_level": 1,
                "description": "Remembering and Understanding level - basic facts, definitions, and simple concepts"
            },
            "intermediate": {
                "bloom_level": 3,
                "description": "Applying and Analyzing level - practical application and analysis of concepts"
            },
            "difficult": {
                "bloom_level": 5,
                "description": "Evaluating and Creating level - critical thinking, evaluation, and synthesis"
            }
        }
        
        difficulty_info = difficulty_mapping.get(difficulty_level, difficulty_mapping["beginner"])
        bloom_level = difficulty_info["bloom_level"]
        level_description = difficulty_info["description"]
        
        # Add randomization seed to prompt for variety
        import random
        random_seed = random.randint(1000, 9999)

        if question_type == "mcq":
            prompt = f"""
                Generate a multiple-choice quiz on {topic} at {difficulty_level.upper()} level ({level_description}).
                - Include exactly {num_questions} questions.
                - Each question should have 4 answer choices.
                - Make questions diverse and varied - avoid repetitive patterns.
                - Use randomization seed {random_seed} to ensure variety.
                - Include a "level" key specifying the Bloom's Taxonomy level (Remembering, Understanding, Applying, etc.).
                - Return output in valid JSON format: 
                [
                    {{"question": "What is AI?", "options": ["A. option1", "B. option2", "C. option3", "D. option4"], "answer": "A", "type": "mcq"}},
                    ...
                ]
            """
        elif question_type == "coding":
            prompt = f"""
CRITICAL: You MUST generate exactly {num_questions} coding programming problems on the topic: {topic}

Difficulty Level: {difficulty_level.upper()} ({level_description})

IMPORTANT REQUIREMENTS:
1. Generate EXACTLY {num_questions} coding problems (not MCQ, not subjective, but actual programming problems)
2. Each problem MUST have the following structure:
   - "question": A clear problem statement describing what the student needs to code
   - "type": MUST be exactly "coding" (not "mcq" or anything else)
   - "sample_input": Sample input that demonstrates the problem
   - "sample_output": Expected output for the sample input
   - "test_cases": An array with at least 3-5 test cases, each with:
     * "input": The test input as a string
     * "expected_output": The expected output as a string
     * "is_hidden": boolean (false for visible test cases, true for hidden ones)
   - "time_limit_seconds": 2 (default)
   - "memory_limit_mb": 256 (default)
   - "starter_code": An object with starter code templates for each language:
     * "python": Python starter code
     * "java": Java starter code  
     * "cpp": C++ starter code
     * "c": C starter code

3. Problems should be diverse and test different programming concepts related to {topic}
4. Use randomization seed {random_seed} to ensure variety

EXAMPLE FORMAT (follow this EXACT structure):
[
    {{
        "question": "Write a function to find the maximum element in an array. The function should take an array of integers and return the maximum value.",
        "type": "coding",
        "sample_input": "5\\n1 3 5 2 4",
        "sample_output": "5",
        "test_cases": [
            {{"input": "3\\n1 2 3", "expected_output": "3", "is_hidden": false}},
            {{"input": "4\\n10 5 8 12", "expected_output": "12", "is_hidden": false}},
            {{"input": "5\\n-1 -5 -3 -2 -4", "expected_output": "-1", "is_hidden": true}},
            {{"input": "1\\n42", "expected_output": "42", "is_hidden": true}}
        ],
        "time_limit_seconds": 2,
        "memory_limit_mb": 256,
        "starter_code": {{
            "python": "def find_max(arr):\\n    # Your code here\\n    pass",
            "java": "public class Solution {{\\n    public static int findMax(int[] arr) {{\\n        // Your code here\\n        return 0;\\n    }}\\n}}",
            "cpp": "#include <iostream>\\n#include <vector>\\nusing namespace std;\\n\\nint findMax(vector<int>& arr) {{\\n    // Your code here\\n    return 0;\\n}}",
            "c": "#include <stdio.h>\\n\\nint findMax(int arr[], int n) {{\\n    // Your code here\\n    return 0;\\n}}"
        }}
    }}
]

Return ONLY valid JSON array. Do NOT include any markdown code blocks, explanations, or text outside the JSON array.
            """
        else:  # subjective
            prompt = f"""
                Generate subjective questions on {topic} at {difficulty_level.upper()} level ({level_description}).
                - Include exactly {num_questions} questions.
                - Questions should be open-ended and require detailed answers.
                - Make questions diverse and varied - avoid repetitive patterns.
                - Use randomization seed {random_seed} to ensure variety.
                - Include a "level" key specifying the Bloom's Taxonomy level.
                - Vary the marks between 5, 10, 15, and 20 marks for different questions.
                - Return output in valid JSON format: 
                [
                    {{"question": "Explain the concept of AI and its applications", "answer": "Sample answer explaining AI...", "type": "subjective", "marks": 10}},
                    ...
                ]
            """

        response = model.generate_content(prompt)

        if not response.text:
            raise ValueError("Empty response from AI")

        json_match = re.search(r"```json\n(.*)\n```", response.text, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group(1))
        else:
            try:
                questions = json.loads(response.text)
            except:
                raise ValueError("Invalid response format from AI")

        # Validate that questions match the requested type
        if questions:
            # Ensure all questions have the correct type
            for q in questions:
                if 'type' not in q:
                    q['type'] = question_type
                elif q.get('type') != question_type:
                    print(f"WARNING: Question type mismatch. Expected {question_type}, got {q.get('type')}")
                    q['type'] = question_type  # Force correct type
            
            print(f"DEBUG: Validated {len(questions)} questions, all have type: {question_type}")

        return questions

    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")
        return None

def process_document(file_path):
    """Process uploaded document to extract content and topic"""
    try:
        # Ensure NLTK data is available
        ensure_nltk_data()
        
        content = ""
        if file_path.lower().endswith('.pdf'):
            try:
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    # Check if PDF is encrypted
                    if pdf_reader.is_encrypted:
                        print("PDF is encrypted, attempting to decrypt...")
                        try:
                            pdf_reader.decrypt('')
                        except Exception as decrypt_error:
                            print(f"Could not decrypt PDF: {decrypt_error}")
                            # Try using AI to extract topic from filename or metadata
                            return extract_topic_from_pdf_metadata(file_path)
                    
                    # Extract text from all pages
                    num_pages = len(pdf_reader.pages)
                    print(f"Processing PDF with {num_pages} pages...")
                    
                    for i, page in enumerate(pdf_reader.pages):
                        try:
                            page_text = page.extract_text()
                            if page_text:
                                content += page_text + " "
                        except Exception as page_error:
                            print(f"Error extracting text from page {i+1}: {page_error}")
                            continue
                    
                    # If no content extracted, try metadata
                    if not content.strip():
                        print("No text extracted from PDF pages, trying metadata...")
                        metadata_topic = extract_topic_from_pdf_metadata(file_path)
                        if metadata_topic:
                            return metadata_topic
                        
                        # If still no content, try using AI with filename
                        print("Attempting AI-based topic extraction from filename...")
                        return extract_topic_from_filename(file_path)
                        
            except Exception as pdf_error:
                print(f"Error reading PDF file: {pdf_error}")
                # Fallback to filename-based extraction
                return extract_topic_from_filename(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as text_file:
                content = text_file.read()

        # If still no content, return None
        if not content or not content.strip():
            print("No content extracted from document")
            return extract_topic_from_filename(file_path)

        # Extract topic using word frequency analysis
        try:
            tokens = word_tokenize(content.lower())
            stop_words = set(stopwords.words('english'))
            meaningful_words = [word for word in tokens if word.isalnum() and len(word) > 2 and word not in stop_words]

            if not meaningful_words:
                print("No meaningful words found after filtering")
                return extract_topic_from_filename(file_path)

            word_freq = Counter(meaningful_words)
            # Get top 3 most common words to better identify topic
            top_words = word_freq.most_common(5)
            print(f"Top words found: {top_words}")
            
            # Filter out common generic words
            generic_words = {'chapter', 'page', 'section', 'question', 'answer', 'example', 'figure', 'table'}
            for word, count in top_words:
                if word not in generic_words and len(word) > 3:
                    main_topic = word.capitalize()
                    print(f"Extracted topic: {main_topic}")
                    return main_topic
            
            # If all top words are generic, use the first one
            if top_words:
                main_topic = top_words[0][0].capitalize()
                print(f"Extracted topic (fallback): {main_topic}")
                return main_topic
                
        except Exception as token_error:
            print(f"Error in tokenization: {token_error}")
            return extract_topic_from_filename(file_path)

        return None

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback
        traceback.print_exc()
        # Final fallback: try to extract from filename
        return extract_topic_from_filename(file_path)

def extract_topic_from_pdf_metadata(file_path):
    """Extract topic from PDF metadata"""
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            metadata = pdf_reader.metadata
            
            if metadata:
                # Try to extract topic from title or subject
                title = metadata.get('/Title', '')
                subject = metadata.get('/Subject', '')
                
                if title:
                    # Extract first meaningful word from title
                    words = title.split()
                    for word in words:
                        if len(word) > 3 and word.isalnum():
                            return word.capitalize()
                
                if subject:
                    words = subject.split()
                    for word in words:
                        if len(word) > 3 and word.isalnum():
                            return word.capitalize()
    except Exception as e:
        print(f"Error extracting from metadata: {e}")
    
    return None

def extract_topic_from_filename(file_path):
    """Extract topic from filename as last resort"""
    try:
        import os
        # Get filename from path
        filename = os.path.basename(file_path)
        # Remove extension
        filename_without_ext = os.path.splitext(filename)[0]
        
        print(f"Attempting to extract topic from filename: {filename_without_ext}")
        
        # Try to extract meaningful words from filename
        # Remove common prefixes/suffixes and clean up
        filename_clean = filename_without_ext.replace('_', ' ').replace('-', ' ').replace('.', ' ')
        # Remove multiple spaces
        filename_clean = ' '.join(filename_clean.split())
        words = filename_clean.split()
        
        print(f"Words extracted from filename: {words}")
        
        # Filter out common words (expanded list)
        common_words = {'pdf', 'document', 'file', 'quiz', 'question', 'bank', 'qb', 'notes', 'paper', 'exam', 'test', 'assignment', 'hw', 'homework'}
        
        # First pass: look for meaningful words (longer than 3 chars, not common)
        for word in words:
            word_clean = word.lower().strip('.,!?()[]{}')
            # Remove any non-alphanumeric characters except numbers
            word_clean = ''.join(c for c in word_clean if c.isalnum() or c.isdigit())
            if len(word_clean) > 3 and word_clean not in common_words:
                topic = word_clean.capitalize()
                print(f"Extracted topic from filename (first pass): {topic}")
                return topic
        
        # Second pass: look for any word longer than 2 characters (includes codes like "BCS702")
        for word in words:
            word_clean = word.upper().strip('.,!?()[]{}')
            # Keep alphanumeric characters (including numbers)
            word_clean = ''.join(c for c in word_clean if c.isalnum() or c.isdigit())
            if len(word_clean) >= 3 and word_clean not in common_words:
                # Check if it looks like a course code (e.g., BCS702, CS101)
                if any(c.isdigit() for c in word_clean) and any(c.isalpha() for c in word_clean):
                    topic = word_clean
                    print(f"Extracted topic from filename (course code): {topic}")
                    return topic
                elif len(word_clean) > 3:
                    topic = word_clean.capitalize()
                    print(f"Extracted topic from filename (second pass): {topic}")
                    return topic
        
        # Third pass: use first meaningful word (minimum 2 chars)
        for word in words:
            word_clean = word.upper().strip('.,!?()[]{}')
            word_clean = ''.join(c for c in word_clean if c.isalnum() or c.isdigit())
            if len(word_clean) >= 2 and word_clean not in common_words:
                topic = word_clean
                print(f"Extracted topic from filename (third pass): {topic}")
                return topic
        
        # Last resort: use first 10 characters of filename (cleaned)
        if filename_without_ext:
            # Remove special characters
            topic_clean = ''.join(c for c in filename_without_ext[:15] if c.isalnum() or c.isspace())
            topic_clean = topic_clean.strip()
            if topic_clean:
                topic = topic_clean.capitalize()
                print(f"Using filename as topic (fallback): {topic}")
                return topic
            
    except Exception as e:
        print(f"Error extracting from filename: {e}")
        import traceback
        traceback.print_exc()
    
    return None

# Routes
@app.route('/')
def home():
    """Home page - PUBLIC ROUTE (no auth required)"""
    # Don't initialize database here - it can cause 401 errors if DB fails
    # Database will be initialized when needed (lazy initialization)
    try:
        return render_template('home.html')
    except Exception as e:
        print(f"Error rendering home template: {e}")
        # Fallback HTML if template fails - ensures home page is always accessible
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>UNITEST - AI-Powered Learning Platform</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h1>Welcome to UNITEST</h1>
            <p>AI-Powered Quiz Generator & Learning Platform</p>
            <a href="/login">Login</a> | <a href="/signup">Sign Up</a>
        </body>
        </html>
        ''', 200

@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content response

@app.route('/favicon.png')
def favicon_png():
    return '', 204  # No content response

@app.route('/test')
def test():
    """Simple test route"""
    return jsonify({
        'message': 'Flask app is working!',
        'environment': 'production' if os.environ.get('DATABASE_URL') else 'development',
        'secret_key_set': bool(os.environ.get('SECRET_KEY')),
        'database_url_set': bool(os.environ.get('DATABASE_URL')),
        'api_key_set': bool(os.environ.get('GOOGLE_AI_API_KEY'))
    })

@app.route('/health')
def health_check():
    """Health check endpoint for debugging"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'environment': 'production' if os.environ.get('DATABASE_URL') else 'development'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'database': 'disconnected'
        }), 500

@app.route('/test-sitemap')
def test_sitemap():
    """Test endpoint to verify sitemap is accessible"""
    try:
        from flask import Response
        from datetime import datetime, timezone
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        return jsonify({
            'status': 'success',
            'sitemap_url': 'https://unitest.in/sitemap.xml',
            'current_date': current_date,
            'message': 'Sitemap should be accessible at /sitemap.xml'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/sitemap.xml', methods=['GET', 'HEAD'])
def sitemap():
    """Serve sitemap.xml for Google Search Console - PUBLIC ROUTE (no auth required)"""
    from flask import Response
    from datetime import datetime, timezone
    
    # Get current date in UTC to avoid timezone issues - format: YYYY-MM-DD
    current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Always return inline sitemap with current date - most reliable for Vercel serverless
    sitemap_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://unitest.in/</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://unitest.in/login</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://unitest.in/signup</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://unitest.in/dashboard</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://unitest.in/quiz</loc>
    <lastmod>{current_date}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>'''
    
    response = Response(sitemap_content, mimetype='application/xml')
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    # Allow all user agents including Googlebot
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/robots.txt')
def robots():
    return send_file('static/robots.txt', mimetype='text/plain')

@app.route('/google77cd707098d48f23.html')
def google_verification():
    """Google Search Console verification file"""
    return send_file('static/google77cd707098d48f23.html', mimetype='text/html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_file(f'static/{filename}')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            role = request.form.get('role', 'student')

            if not all([username, email, password, confirm_password]):
                flash('Please fill in all fields', 'error')
                return redirect(url_for('signup'))

            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('signup'))

            # Check if user exists
            existing_user = db.session.query(User).filter_by(username=username).first()
            if existing_user:
                flash('Username already exists', 'error')
                return redirect(url_for('signup'))

            existing_email = db.session.query(User).filter_by(email=email).first()
            if existing_email:
                flash('Email already exists', 'error')
                return redirect(url_for('signup'))

            # Create new user
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role=role if role in ['student','teacher'] else 'student'
            )
            db.session.add(user)
            db.session.commit()

            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error in signup: {str(e)}")
            db.session.rollback()
            flash(f'Signup failed: {str(e)}', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            user = db.session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                # Track login
                login_time = datetime.utcnow()
                user.last_login = login_time
                
                # Record login history
                login_history = LoginHistory(
                    user_id=user.id,
                    login_time=login_time,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', 'Unknown')
                )
                db.session.add(login_history)
                db.session.commit()
                
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Error in login: {str(e)}")
            db.session.rollback()
            flash(f'Login error: {str(e)}', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    progress_records = db.session.query(Progress).filter_by(user_id=current_user.id).all()
    # Teacher's quizzes
    my_quizzes = []
    if getattr(current_user, 'role', 'student') == 'teacher':
        my_quizzes = db.session.query(Quiz).filter_by(created_by=current_user.id).all()
    # Student shared quiz history
    my_submissions = []
    if getattr(current_user, 'role', 'student') == 'student':
        my_submissions = db.session.query(QuizSubmission).filter_by(student_id=current_user.id).order_by(QuizSubmission.submitted_at.desc()).all()
    current_time = datetime.utcnow()  # For 15-minute review unlock
    return render_template('dashboard.html', progress_records=progress_records, my_quizzes=my_quizzes, my_submissions=my_submissions, current_time=current_time)

def generate_quiz_code(length=6):
    import random, string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def require_teacher():
    if getattr(current_user, 'role', 'student') != 'teacher':
        flash('Teacher access required', 'error')
        return redirect(url_for('dashboard'))
    return None

# Teacher: create quiz (form + post)
@app.route('/teacher/quiz/new', methods=['GET', 'POST'])
@login_required
def teacher_create_quiz():
    guard = require_teacher()
    if guard:
        return guard

    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            questions_raw = request.form.get('questions_json', '').strip()
            if not title or not questions_raw:
                flash('Title and questions are required', 'error')
                return redirect(url_for('teacher_create_quiz'))

            # parse questions json
            questions = json.loads(questions_raw)
            # generate unique code
            code = generate_quiz_code()
            while db.session.query(Quiz).filter_by(code=code).first() is not None:
                code = generate_quiz_code()

            quiz = Quiz(title=title, code=code, created_by=current_user.id)
            db.session.add(quiz)
            db.session.flush()  # get quiz.id

            for q in questions:
                qtype = q.get('type', 'mcq')
                opts = q.get('options', []) if qtype == 'mcq' else []
                qq = QuizQuestion(
                    quiz_id=quiz.id,
                    question=q.get('question', ''),
                    options_json=json.dumps(opts) if opts else None,
                    answer=q.get('answer', ''),
                    qtype=qtype,
                    marks=int(q.get('marks', 1))
                )
                db.session.add(qq)

            db.session.commit()
            flash(f'Quiz created! Share code: {code}', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Error creating quiz: {str(e)}")
            flash('Error creating quiz. Ensure valid JSON.', 'error')
            return redirect(url_for('teacher_create_quiz'))

    return render_template('create_quiz.html')

# Teacher: simple create by topic and number of questions
@app.route('/teacher/quiz/new_simple', methods=['GET', 'POST'])
@login_required
def teacher_create_quiz_simple():
    guard = require_teacher()
    if guard:
        return guard

    if request.method == 'POST':
        try:
            topic = request.form.get('topic', '').strip()
            count = int(request.form.get('count', '0') or 0)
            title = request.form.get('title', '').strip()
            difficulty = request.form.get('difficulty', 'beginner').strip()
            marks = int(request.form.get('marks', '1') or 1)
            duration = request.form.get('duration', '').strip()
            duration_minutes = int(duration) if duration else None
            question_type = request.form.get('question_type', 'mcq').strip()  # Get question type

            if not topic or count <= 0:
                flash('Please provide topic and number of questions (>0).', 'error')
                return redirect(url_for('teacher_create_quiz_simple'))

            # If PDF uploaded, extract better topic context
            if 'notes_pdf' in request.files and request.files['notes_pdf'].filename:
                file = request.files['notes_pdf']
                if file and file.filename.lower().endswith('.pdf'):
                    import tempfile, os
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        file.save(tmp.name)
                        extracted = process_document(tmp.name)
                    try:
                        os.unlink(tmp.name)
                    except Exception:
                        pass
                    if extracted:
                        topic = f"{topic} - {extracted}"

            questions = generate_quiz(topic, difficulty if difficulty in ['beginner','intermediate','advanced'] else 'beginner', question_type, count) or []
            if not questions:
                flash('Failed to generate questions. Try again.', 'error')
                return redirect(url_for('teacher_create_quiz_simple'))

            if not title:
                title = f"{topic} Quiz"

            # Default marks fill
            for q in questions:
                q['marks'] = marks

            # Store in session for preview
            session['preview_quiz'] = {
                'title': title,
                'topic': topic,
                'difficulty': difficulty,
                'duration_minutes': duration_minutes,
                'question_type': question_type,
                'questions': questions
            }
            return render_template('preview_quiz.html', data=session['preview_quiz'])
        except Exception as e:
            db.session.rollback()
            print(f"Error creating simple quiz: {str(e)}")
            flash('Error creating quiz. Please try again.', 'error')
            return redirect(url_for('teacher_create_quiz_simple'))

    return render_template('create_quiz_simple.html')

# Preview step for teacher to adjust marks before finalizing
@app.route('/teacher/quiz/preview', methods=['POST'])
@login_required
def teacher_quiz_preview():
    guard = require_teacher()
    if guard:
        return guard
    try:
        # Rebuild inputs
        title = request.form.get('title', '').strip()
        topic = request.form.get('topic', '').strip()
        count = int(request.form.get('count', '0') or 0)
        difficulty = request.form.get('difficulty', 'beginner').strip()
        marks = int(request.form.get('marks', '1') or 1)
        duration = request.form.get('duration', '').strip()
        duration_minutes = int(duration) if duration else None

        if not topic or count <= 0:
            flash('Provide topic and number of questions.', 'error')
            return redirect(url_for('teacher_create_quiz_simple'))

        questions = generate_quiz(topic, difficulty if difficulty in ['beginner','intermediate','advanced'] else 'beginner', 'mcq', count) or []
        if not questions:
            flash('Failed to generate questions.', 'error')
            return redirect(url_for('teacher_create_quiz_simple'))

        # Default marks fill
        for q in questions:
            q['marks'] = marks

        # Store in session for finalize
        session['preview_quiz'] = {
            'title': title or f"{topic} Quiz",
            'topic': topic,
            'difficulty': difficulty,
            'duration_minutes': duration_minutes,
            'questions': questions
        }
        return render_template('preview_quiz.html', data=session['preview_quiz'])
    except Exception as e:
        print(f"Preview error: {e}")
        flash('Error preparing preview.', 'error')
        return redirect(url_for('teacher_create_quiz_simple'))

@app.route('/teacher/quiz/finalize', methods=['POST'])
@login_required
def teacher_quiz_finalize():
    guard = require_teacher()
    if guard:
        return guard
    data = session.get('preview_quiz')
    if not data:
        flash('No quiz in preview.', 'error')
        return redirect(url_for('teacher_create_quiz_simple'))
    try:
        # Read marks overrides
        q_overrides = []
        for i, q in enumerate(data['questions']):
            new_marks = request.form.get(f'marks_{i}')
            try:
                q['marks'] = int(new_marks)
            except Exception:
                pass
            q_overrides.append(q)

        code = generate_quiz_code()
        while db.session.query(Quiz).filter_by(code=code).first() is not None:
            code = generate_quiz_code()

        quiz = Quiz(title=data['title'], code=code, created_by=current_user.id, difficulty=data['difficulty'], duration_minutes=data['duration_minutes'])
        db.session.add(quiz)
        db.session.flush()

        for q in q_overrides:
            qtype = q.get('type', data.get('question_type', 'mcq'))
            opts = q.get('options', [])
            
            qq = QuizQuestion(
                quiz_id=quiz.id,
                question=q.get('question', ''),
                options_json=json.dumps(opts) if opts else None,
                answer=q.get('answer', ''),
                qtype=qtype,
                marks=int(q.get('marks', 1))
            )
            
            # Handle coding questions
            if qtype == 'coding':
                qq.test_cases_json = json.dumps(q.get('test_cases', []))
                qq.language_constraints = json.dumps(q.get('language_constraints', ['python', 'java', 'cpp', 'c']))
                qq.time_limit_seconds = q.get('time_limit_seconds', 2)
                qq.memory_limit_mb = q.get('memory_limit_mb', 256)
                qq.sample_input = q.get('sample_input', '')
                qq.sample_output = q.get('sample_output', '')
                qq.starter_code = json.dumps(q.get('starter_code', {}))
            
            db.session.add(qq)

        db.session.commit()
        session.pop('preview_quiz', None)
        flash(f'Quiz created! Share code: {code}', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = str(e)
        traceback.print_exc()
        print(f"Finalize error: {error_details}")
        # Check if it's a database column error
        if 'no column named' in error_details.lower() or 'column' in error_details.lower():
            flash(f'Database migration needed! Error: {error_details}. Please run: python migrate_new_features.py', 'error')
        else:
            flash(f'Error finalizing quiz: {error_details}', 'error')
        return redirect(url_for('teacher_create_quiz_simple'))

# Student: join quiz by code
@app.route('/quiz/join', methods=['GET', 'POST'])
@login_required
def join_quiz():
    if request.method == 'POST':
        code = request.form.get('code', '').strip().upper()
        quiz = db.session.query(Quiz).filter_by(code=code).first()
        if not quiz:
            flash('Invalid quiz code', 'error')
            return redirect(url_for('join_quiz'))
        return redirect(url_for('take_shared_quiz', code=code))
    return render_template('join_quiz.html')

# Take shared quiz
@app.route('/quiz/take/<code>')
@login_required
def take_shared_quiz(code):
    quiz = db.session.query(Quiz).filter_by(code=code.upper()).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('join_quiz'))
    
    # Check if student has already completed this quiz
    existing_completed = db.session.query(QuizSubmission).filter_by(
        quiz_id=quiz.id, 
        student_id=current_user.id, 
        completed=True
    ).first()
    
    if existing_completed:
        flash('You have already attempted this quiz. You can only take it once.', 'error')
        return redirect(url_for('dashboard'))
    
    q_rows = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()
    # Parse options JSON server-side to avoid template errors
    parsed_questions = []
    for q in q_rows:
        try:
            options = json.loads(q.options_json) if q.options_json else []
        except Exception:
            options = []
        
        question_data = {
            'id': q.id,
            'question': q.question,
            'qtype': q.qtype,
            'marks': q.marks,
            'options': options,
        }
        
        # Add coding question data
        if q.qtype == 'coding':
            try:
                question_data['test_cases'] = json.loads(q.test_cases_json) if q.test_cases_json else []
                question_data['language_constraints'] = json.loads(q.language_constraints) if q.language_constraints else ['python', 'java', 'cpp', 'c']
                question_data['time_limit_seconds'] = q.time_limit_seconds or 2
                question_data['memory_limit_mb'] = q.memory_limit_mb or 256
                question_data['sample_input'] = q.sample_input or ''
                question_data['sample_output'] = q.sample_output or ''
                question_data['starter_code'] = json.loads(q.starter_code) if q.starter_code else {}
            except Exception as e:
                print(f"Error parsing coding question data: {e}")
                question_data['test_cases'] = []
                question_data['language_constraints'] = ['python', 'java', 'cpp', 'c']
        
        parsed_questions.append(question_data)
    
    # Ensure a started submission exists (one per student/quiz if not completed)
    existing = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id, student_id=current_user.id, completed=False).first()
    if not existing:
        existing = QuizSubmission(quiz_id=quiz.id, student_id=current_user.id, question_count=len(q_rows))
        db.session.add(existing)
        db.session.commit()
    return render_template('take_shared_quiz.html', quiz=quiz, questions=parsed_questions)

# Submit shared quiz
@app.route('/quiz/submit/<code>', methods=['POST'])
@login_required
def submit_shared_quiz(code):
    quiz = db.session.query(Quiz).filter_by(code=code.upper()).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('join_quiz'))
    
    # Check if student has already completed this quiz
    existing_completed = db.session.query(QuizSubmission).filter_by(
        quiz_id=quiz.id, 
        student_id=current_user.id, 
        completed=True
    ).first()
    
    if existing_completed:
        flash('You have already attempted this quiz. You can only take it once.', 'error')
        return redirect(url_for('dashboard'))
    
    questions = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()

    total_marks = 0.0
    scored_marks = 0.0
    submission = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id, student_id=current_user.id, completed=False).first()
    if not submission:
        submission = QuizSubmission(quiz_id=quiz.id, student_id=current_user.id)
        db.session.add(submission)
        db.session.flush()

    answered_count = 0
    for q in questions:
        total_marks += float(q.marks or 1)
        key = f'q_{q.id}'
        user_ans = request.form.get(key, '').strip()
        is_correct = None
        ai_score = None
        gained = 0.0
        code_language = None
        test_results_json = None
        passed_test_cases = 0
        total_test_cases = 0

        if q.qtype == 'mcq':
            is_correct = (user_ans.split('. ')[0] == (q.answer or '')) if user_ans else False
            gained = float(q.marks or 1) if is_correct else 0.0
        elif q.qtype == 'coding':
            # Handle coding question submission
            code_data = request.form.get(f'code_{q.id}', '').strip()
            language = request.form.get(f'language_{q.id}', 'python')
            
            if code_data:
                try:
                    test_cases = json.loads(q.test_cases_json) if q.test_cases_json else []
                    time_limit = q.time_limit_seconds or 2
                    memory_limit = q.memory_limit_mb or 256
                    
                    test_results = run_test_cases(code_data, language, test_cases, time_limit, memory_limit)
                    
                    passed_test_cases = test_results['passed']
                    total_test_cases = test_results['total']
                    percentage_passed = test_results['percentage'] / 100.0
                    
                    gained = float(q.marks or 1) * percentage_passed
                    is_correct = percentage_passed == 1.0
                    code_language = language
                    test_results_json = json.dumps(test_results['results'])
                    user_ans = code_data
                except Exception as e:
                    print(f"Error evaluating coding question: {e}")
                    gained = 0.0
                    is_correct = False
                    code_language = language
                    test_results_json = json.dumps([])
                    user_ans = code_data
        else:
            # subjective via AI
            if user_ans:
                ai_score = evaluate_subjective_answer(q.question, user_ans, q.answer or '')
                gained = float(q.marks or 1) * float(ai_score or 0.0)
                is_correct = (ai_score or 0.0) >= 0.6
            else:
                ai_score = 0.0
                is_correct = False

        scored_marks += gained
        ans = QuizAnswer(
            submission_id=submission.id,
            question_id=q.id,
            user_answer=user_ans,
            is_correct=is_correct,
            ai_score=ai_score,
            scored_marks=gained,
            code_language=code_language,
            test_results_json=test_results_json,
            passed_test_cases=passed_test_cases,
            total_test_cases=total_test_cases
        )
        db.session.add(ans)
        if user_ans:
            answered_count += 1

    percentage = (scored_marks / total_marks) * 100 if total_marks > 0 else 0
    passed = percentage >= 60
    submission.score = scored_marks
    submission.total = total_marks
    submission.percentage = percentage
    submission.passed = passed
    # set review unlock time 15 minutes after submission
    submission.review_unlocked_at = datetime.utcnow() + timedelta(minutes=15)
    # check if student exited fullscreen during test
    submission.fullscreen_exit_flag = request.form.get('fullscreen_exit') == 'true'
    submission.answered_count = answered_count
    submission.question_count = len(questions)
    submission.is_full_completion = (answered_count == len(questions)) and (not submission.fullscreen_exit_flag)
    submission.completed = True
    db.session.commit()

    flash(f'Submitted. Score: {scored_marks:.1f}/{total_marks} ({percentage:.0f}%).', 'success')
    return redirect(url_for('dashboard'))

# Auto-submit partial answers on fullscreen exit or tab close
@app.route('/quiz/auto_submit/<code>', methods=['POST'])
@login_required
def auto_submit_partial(code):
    try:
        quiz = db.session.query(Quiz).filter_by(code=code.upper()).first()
        if not quiz:
            return ('', 204)
        questions = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()
        submission = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id, student_id=current_user.id, completed=False).first()
        if not submission:
            submission = QuizSubmission(quiz_id=quiz.id, student_id=current_user.id)
            db.session.add(submission)
            db.session.flush()

        total_marks = 0.0
        scored_marks = 0.0
        answered_count = 0
        data = request.get_json(silent=True) or {}

        for q in questions:
            total_marks += float(q.marks or 1)
            key = f'q_{q.id}'
            user_ans = (data.get(key) or '').strip()
            is_correct = None
            ai_score = None
            gained = 0.0
            if q.qtype == 'mcq':
                is_correct = (user_ans.split('. ')[0] == (q.answer or '')) if user_ans else False
                gained = float(q.marks or 1) if is_correct else 0.0
            else:
                if user_ans:
                    ai_score = evaluate_subjective_answer(q.question, user_ans, q.answer or '')
                    gained = float(q.marks or 1) * float(ai_score or 0.0)
                    is_correct = (ai_score or 0.0) >= 0.6
                else:
                    ai_score = 0.0
                    is_correct = False
            if user_ans:
                answered_count += 1
            # Upsert answer
            existing_ans = db.session.query(QuizAnswer).filter_by(submission_id=submission.id, question_id=q.id).first()
            if existing_ans:
                existing_ans.user_answer = user_ans
                existing_ans.is_correct = is_correct
                existing_ans.ai_score = ai_score
                existing_ans.scored_marks = gained
            else:
                db.session.add(QuizAnswer(
                    submission_id=submission.id,
                    question_id=q.id,
                    user_answer=user_ans,
                    is_correct=is_correct,
                    ai_score=ai_score,
                    scored_marks=gained
                ))

        submission.score = scored_marks
        submission.total = total_marks
        submission.percentage = (scored_marks / total_marks) * 100 if total_marks > 0 else 0
        submission.passed = submission.percentage >= 60
        from datetime import timedelta
        submission.review_unlocked_at = datetime.utcnow() + timedelta(minutes=15)
        submission.fullscreen_exit_flag = True
        submission.answered_count = answered_count
        submission.question_count = len(questions)
        submission.is_full_completion = False
        submission.completed = True
        db.session.commit()
        return ('', 204)
    except Exception as e:
        db.session.rollback()
        return ('', 204)

# Teacher: view results
@app.route('/teacher/quiz/<code>/results')
@login_required
def teacher_quiz_results(code):
    guard = require_teacher()
    if guard:
        return guard
    quiz = db.session.query(Quiz).filter_by(code=code.upper(), created_by=current_user.id).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('dashboard'))
    submissions = db.session.query(QuizSubmission).filter_by(quiz_id=quiz.id).order_by(QuizSubmission.submitted_at.desc()).all()
    # Join with users
    student_map = {u.id: u for u in db.session.query(User).filter(User.id.in_([s.student_id for s in submissions])).all()}
    return render_template('teacher_results.html', quiz=quiz, submissions=submissions, student_map=student_map)

# Student: view quiz result (after 15 minutes)
@app.route('/quiz/result/<int:submission_id>')
@login_required
def view_quiz_result(submission_id):
    submission = db.session.query(QuizSubmission).filter_by(
        id=submission_id, 
        student_id=current_user.id
    ).first()
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if 15 minutes have passed
    current_time = datetime.utcnow()
    if submission.review_unlocked_at and submission.review_unlocked_at > current_time:
        flash('Results will be available 15 minutes after submission', 'info')
        return redirect(url_for('dashboard'))
    
    # Get quiz and questions
    quiz = db.session.query(Quiz).filter_by(id=submission.quiz_id).first()
    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('dashboard'))
    
    questions = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).order_by(QuizQuestion.id).all()
    answers = db.session.query(QuizAnswer).filter_by(submission_id=submission.id).all()
    
    answer_map = {ans.question_id: ans for ans in answers}
    
    # Format results for template
    results = []
    for q in questions:
        ans = answer_map.get(q.id)
        if q.qtype == 'mcq':
            options = json.loads(q.options_json) if q.options_json else []
            user_answer = ans.user_answer if ans else ''
            correct_option = next((opt for opt in options if opt.startswith(f"{q.answer}.")), '') if q.answer else ''
            
            results.append({
                'question': q.question,
                'user_answer': user_answer,
                'correct_answer': correct_option,
                'is_correct': ans.is_correct if ans else False,
                'type': 'mcq',
                'marks': q.marks
            })
        elif q.qtype == 'subjective':
            results.append({
                'question': q.question,
                'user_answer': ans.user_answer if ans else '',
                'sample_answer': q.answer or 'N/A',
                'ai_score': ans.ai_score if ans else 0.0,
                'scored_marks': ans.scored_marks if ans else 0.0,
                'marks': q.marks,
                'type': 'subjective'
            })
        elif q.qtype == 'coding':
            test_results = json.loads(ans.test_results_json) if ans and ans.test_results_json else []
            results.append({
                'question': q.question,
                'user_answer': ans.user_answer if ans else '',
                'code_language': ans.code_language if ans else '',
                'passed_test_cases': ans.passed_test_cases if ans else 0,
                'total_test_cases': ans.total_test_cases if ans else 0,
                'test_results': test_results,
                'scored_marks': ans.scored_marks if ans else 0.0,
                'marks': q.marks,
                'type': 'coding',
                'sample_input': q.sample_input,
                'sample_output': q.sample_output
            })
    
    final_score = f"{submission.score:.1f}/{submission.total:.1f}"
    percentage = submission.percentage
    passed = submission.passed
    
    return render_template('shared_quiz_results.html', 
                         quiz=quiz,
                         submission=submission,
                         results=results,
                         final_score=final_score,
                         percentage=percentage,
                         passed=passed)

# Teacher: allow student to retake quiz
@app.route('/teacher/quiz/<code>/allow-retake/<int:submission_id>', methods=['POST'])
@login_required
def allow_student_retake(code, submission_id):
    guard = require_teacher()
    if guard:
        return guard
    
    # Verify quiz ownership
    quiz = db.session.query(Quiz).filter_by(code=code.upper(), created_by=current_user.id).first()
    if not quiz:
        flash('Quiz not found or you do not have permission', 'error')
        return redirect(url_for('dashboard'))
    
    # Get the submission and verify it belongs to this quiz
    submission = db.session.query(QuizSubmission).filter_by(
        id=submission_id,
        quiz_id=quiz.id
    ).first()
    
    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('teacher_quiz_results', code=code))
    
    # Get student name
    student = db.session.query(User).filter_by(id=submission.student_id).first()
    student_name = student.username if student else f"Student {submission.student_id}"
    
    # Delete all answers
    db.session.query(QuizAnswer).filter_by(submission_id=submission.id).delete()
    
    # Delete submission
    db.session.delete(submission)
    db.session.commit()
    
    flash(f'Successfully allowed {student_name} to retake the quiz. Their previous submission has been reset.', 'success')
    return redirect(url_for('teacher_quiz_results', code=code))

# API endpoints for code testing
@app.route('/api/test_code', methods=['POST'])
@login_required
def test_code():
    """Test code execution for coding questions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        code = data.get('code', '')
        language = data.get('language', 'python')
        test_input = data.get('test_input', '')
        time_limit = int(data.get('time_limit', 2))
        memory_limit = int(data.get('memory_limit', 256))
        
        if not code:
            return jsonify({'success': False, 'error': 'No code provided'}), 400
        
        result = execute_code(code, language, test_input, time_limit, memory_limit)
        return jsonify({'success': True, 'result': result})
        
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'Invalid JSON: {str(e)}'}), 400
    except Exception as e:
        print(f"Error in test_code API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run_test_cases', methods=['POST'])
@login_required
def api_run_test_cases():
    """Run test cases for coding questions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        code = data.get('code', '')
        language = data.get('language', 'python')
        test_cases = data.get('test_cases', [])
        time_limit = int(data.get('time_limit', 2))
        memory_limit = int(data.get('memory_limit', 256))
        
        if not code:
            return jsonify({'success': False, 'error': 'Code is required'}), 400
        if not test_cases or not isinstance(test_cases, list):
            return jsonify({'success': False, 'error': 'Test cases must be a non-empty list'}), 400
        
        result = run_test_cases(code, language, test_cases, time_limit, memory_limit)
        return jsonify({'success': True, 'result': result})
        
    except json.JSONDecodeError as e:
        return jsonify({'success': False, 'error': f'Invalid JSON: {str(e)}'}), 400
    except Exception as e:
        print(f"Error in run_test_cases API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Migration route - run once to add new columns
@app.route('/run-migration')
@login_required
def run_migration_route():
    """Run database migration for new features"""
    try:
        from migrate_new_features import migrate_database
        migrate_database()
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Migration Complete</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
            </style>
        </head>
        <body>
            <h1>✅ Migration Complete!</h1>
            <div class="success">
                Database migration has been completed successfully. All new columns have been added.
            </div>
            <p>You can now:</p>
            <ul>
                <li>Create quizzes with coding questions</li>
                <li>Use the 15-minute review unlock feature</li>
                <li>Enable one attempt per student</li>
                <li>Allow students to retake quizzes (teacher feature)</li>
            </ul>
            <a href="/dashboard" class="btn">Go to Dashboard</a>
            <a href="/teacher/quiz/new_simple" class="btn">Create Quiz</a>
        </body>
        </html>
        """
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Migration Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .error {{ background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }}
                pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>❌ Migration Error</h1>
            <div class="error">
                <strong>Error:</strong> {error_msg}
            </div>
            <p>If you see a "column already exists" error, that's okay - the migration may have partially completed.</p>
            <p>Try creating a quiz now. If it still fails, run the SQL commands directly in NeonDB (see instructions below).</p>
            <h3>Alternative: Run SQL in NeonDB</h3>
            <p>Go to your NeonDB dashboard → SQL Editor → Run these commands:</p>
            <pre>
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS test_cases_json TEXT;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS language_constraints TEXT;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS time_limit_seconds INTEGER;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS memory_limit_mb INTEGER;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS sample_input TEXT;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS sample_output TEXT;
ALTER TABLE quiz_question ADD COLUMN IF NOT EXISTS starter_code TEXT;
ALTER TABLE quiz_answer ADD COLUMN IF NOT EXISTS code_language VARCHAR(20);
ALTER TABLE quiz_answer ADD COLUMN IF NOT EXISTS test_results_json TEXT;
ALTER TABLE quiz_answer ADD COLUMN IF NOT EXISTS passed_test_cases INTEGER DEFAULT 0;
ALTER TABLE quiz_answer ADD COLUMN IF NOT EXISTS total_test_cases INTEGER DEFAULT 0;
            </pre>
            <a href="/dashboard" class="btn">Go to Dashboard</a>
        </body>
        </html>
        """

# Temporary helper: run lightweight migration for SQLite (adds missing columns/tables)
@app.route('/dev/migrate')
def dev_migrate():
    try:
        # Only for SQLite local use
        from sqlalchemy import text
        with db.engine.begin() as conn:
            # Check if 'role' column exists on user
            has_role = False
            try:
                res = conn.execute(text("PRAGMA table_info(user);"))
                for row in res:
                    if str(row[1]) == 'role':
                        has_role = True
                        break
            except Exception:
                pass

            if not has_role:
                try:
                    conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'student';"))
                except Exception as e:
                    print(f"ALTER TABLE role add failed (may already exist): {e}")

            # Add difficulty and duration to quiz if missing
            try:
                res = conn.execute(text("PRAGMA table_info(quiz);"))
                cols = [str(r[1]) for r in res]
                if 'difficulty' not in cols:
                    conn.execute(text("ALTER TABLE quiz ADD COLUMN difficulty VARCHAR(20) DEFAULT 'beginner';"))
                if 'duration_minutes' not in cols:
                    conn.execute(text("ALTER TABLE quiz ADD COLUMN duration_minutes INTEGER;"))
            except Exception as e:
                print(f"ALTER TABLE quiz add columns failed (may exist): {e}")

            # Add review_unlocked_at and fullscreen_exit_flag to quiz_submission if missing
            try:
                res = conn.execute(text("PRAGMA table_info(quiz_submission);"))
                cols = [str(r[1]) for r in res]
                if 'review_unlocked_at' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN review_unlocked_at DATETIME;"))
                if 'fullscreen_exit_flag' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN fullscreen_exit_flag BOOLEAN DEFAULT 0;"))
                if 'answered_count' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN answered_count INTEGER DEFAULT 0;"))
                if 'question_count' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN question_count INTEGER DEFAULT 0;"))
                if 'is_full_completion' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN is_full_completion BOOLEAN DEFAULT 0;"))
                if 'started_at' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN started_at DATETIME;"))
                if 'completed' not in cols:
                    conn.execute(text("ALTER TABLE quiz_submission ADD COLUMN completed BOOLEAN DEFAULT 0;"))
            except Exception as e:
                print(f"ALTER TABLE quiz_submission add columns failed (may exist): {e}")

        # Create any new tables
        db.create_all()
        flash('Migration completed. If you were logged in, reload the page. Next, visit /dev/promote_me.', 'success')
    except Exception as e:
        print(f"Migration error: {e}")
        flash('Migration failed. See server logs.', 'error')
    return redirect(url_for('dashboard'))

# Temporary helper: promote current user to teacher (local/dev use)
@app.route('/dev/promote_me')
@login_required
def dev_promote_me():
    try:
        current_user.role = 'teacher'
        db.session.commit()
        flash('Your account is now a Teacher. You can create shared quizzes.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Promote error: {e}")
        flash('Failed to promote user.', 'error')
    return redirect(url_for('dashboard'))

# Database migration helper
@app.route('/dev/migrate_db')
def migrate_database():
    """Manual database migration to fix column lengths"""
    try:
        from sqlalchemy import text
        with db.engine.begin() as conn:
            # Add role column if missing
            try:
                result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='role'"))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE \"user\" ADD COLUMN role VARCHAR(20) DEFAULT 'student'"))
                    print("✅ Added role column")
            except Exception as e:
                print(f"Role column: {e}")
            
            # Update password_hash column length
            try:
                result = conn.execute(text("SELECT character_maximum_length FROM information_schema.columns WHERE table_name='user' AND column_name='password_hash'"))
                row = result.fetchone()
                if row and row[0] < 255:
                    conn.execute(text("ALTER TABLE \"user\" ALTER COLUMN password_hash TYPE VARCHAR(255)"))
                    print("✅ Updated password_hash column to VARCHAR(255)")
                else:
                    print("✅ Password_hash column already correct length")
            except Exception as e:
                print(f"Password hash column: {e}")
        
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Database Migration - UniTest</title>
            <link rel="stylesheet" href="/static/style.css">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        </head>
        <body>
            <div class="auth-container">
                <div class="auth-card">
                    <div class="auth-header">
                        <h1 class="auth-title">✅ Database Migration Complete</h1>
                        <p class="auth-subtitle">Database schema has been updated successfully</p>
                    </div>
                    
                    <div class="alert alert-success">
                        <span class="alert-icon">✅</span>
                        Database migration completed! You can now sign up and login without errors.
                    </div>
                    
                    <div class="auth-links">
                        <a href="/signup" class="btn" style="display: inline-block; text-align: center; margin-bottom: 20px;">Try Sign Up Now</a><br>
                        <a href="/login" class="auth-link">Sign In</a><br>
                        <a href="/" class="auth-link">← Back to Home</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Migration Error - UniTest</title>
            <link rel="stylesheet" href="/static/style.css">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        </head>
        <body>
            <div class="auth-container">
                <div class="auth-card">
                    <div class="auth-header">
                        <h1 class="auth-title">❌ Migration Error</h1>
                        <p class="auth-subtitle">Database migration failed</p>
                    </div>
                    
                    <div class="alert alert-error">
                        <span class="alert-icon">⚠️</span>
                        Error: {str(e)}
                    </div>
                    
                    <div class="auth-links">
                        <a href="/" class="auth-link">← Back to Home</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'GET':
        # Handle topic parameter from AI learning modal or next/retry level
        topic = request.args.get('topic', '')
        difficulty = request.args.get('difficulty', '')
        action = request.args.get('action', '')
        
        if topic:
            return render_template('quiz.html', 
                                 prefill_topic=topic, 
                                 prefill_difficulty=difficulty,
                                 action=action)
    
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        question_type = request.form.get('question_type', 'mcq')
        mcq_count = int(request.form.get('mcq_count', 3))
        subj_count = int(request.form.get('subj_count', 2))
        difficulty_level = request.form.get('difficulty_level', 'beginner')
        
        # Check if PDF file was uploaded
        if 'file_upload' in request.files and request.files['file_upload'].filename:
            file = request.files['file_upload']
            if file and file.filename.lower().endswith('.pdf'):
                try:
                    # Save file temporarily
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        file.save(tmp_file.name)
                        tmp_path = tmp_file.name
                    
                    # Process the PDF to extract topic
                    extracted_topic = process_document(tmp_path)
                    
                    # Clean up temporary file
                    os.unlink(tmp_path)
                    
                    if extracted_topic:
                        topic = extracted_topic
                        flash(f'Topic extracted from PDF: {topic}', 'success')
                    else:
                        flash('Could not extract topic from PDF. Please enter a topic manually.', 'error')
                        return redirect(url_for('quiz'))
                        
                except Exception as e:
                    flash(f'Error processing PDF: {str(e)}', 'error')
                    return redirect(url_for('quiz'))
        
        # Ensure we have a topic
        if not topic:
            flash('Please either enter a topic OR upload a PDF file.', 'error')
            return redirect(url_for('quiz'))

        # Get user's current bloom level for this topic (for progress tracking)
        progress = db.session.query(Progress).filter_by(user_id=current_user.id, topic=topic).first()
        bloom_level = progress.bloom_level if progress else 1

        # Generate questions using difficulty level
        questions = []
        if question_type == "both":
            mcq_questions = generate_quiz(topic, difficulty_level, "mcq", mcq_count)
            subj_questions = generate_quiz(topic, difficulty_level, "subjective", subj_count)
            if mcq_questions and subj_questions:
                questions = mcq_questions + subj_questions
        else:
            num_q = mcq_count if question_type == "mcq" else subj_count
            questions = generate_quiz(topic, difficulty_level, question_type, num_q)

        if questions:
            session['current_quiz'] = {
                'questions': questions,
                'topic': topic,
                'bloom_level': bloom_level,
                'difficulty_level': difficulty_level
            }
            return redirect(url_for('take_quiz'))
        else:
            flash('Failed to generate quiz questions', 'error')

    return render_template('quiz.html')

@app.route('/take_quiz')
@login_required
def take_quiz():
    quiz_data = session.get('current_quiz')
    if not quiz_data:
        flash('No quiz available', 'error')
        return redirect(url_for('quiz'))
    
    return render_template('take_quiz.html', quiz_data=quiz_data)

@app.route('/submit_quiz', methods=['POST'])
@login_required
def submit_quiz():
    quiz_data = session.get('current_quiz')
    if not quiz_data:
        return jsonify({'error': 'No quiz available'})

    questions = quiz_data['questions']
    topic = quiz_data['topic']
    bloom_level = quiz_data['bloom_level']
    difficulty_level = quiz_data.get('difficulty_level', 'beginner')
    
    # Get answers for each question
    user_answers = []
    for i in range(len(questions)):
        question = questions[i]
        if question.get('type') == 'mcq':
            # For MCQ questions, get from question group
            answer = request.form.get(f'question_{i}')
        else:
            # For subjective questions, get from subjective_answers array
            answer = request.form.get(f'subjective_answers[{i}]')
        
        if not answer:
            return jsonify({'error': f'Please answer question {i+1}'})
        user_answers.append(answer)

    # Calculate scores
    correct_answers = 0
    total_marks = 0
    scored_marks = 0
    results = []

    for i, (q, user_ans) in enumerate(zip(questions, user_answers)):
        if q.get('type') == 'mcq':
            user_choice = user_ans.split(". ")[0] if user_ans else ""
            is_correct = user_choice == q["answer"]
            if is_correct:
                correct_answers += 1
            results.append({
                'question': q['question'],
                'user_answer': user_ans,
                'correct_answer': next((opt for opt in q["options"] if opt.startswith(f"{q['answer']}.")), ""),
                'is_correct': is_correct,
                'type': 'mcq'
            })
        else:  # subjective
            marks = q.get('marks', 10)
            total_marks += marks
            
            if user_ans.strip():
                ai_score = evaluate_subjective_answer(q['question'], user_ans, q.get('answer', ''))
                scored_marks += ai_score * marks
                if ai_score >= 0.6:
                    correct_answers += 1
            else:
                ai_score = 0.0

            results.append({
                'question': q['question'],
                'user_answer': user_ans,
                'sample_answer': q.get('answer', 'N/A'),
                'marks': marks,
                'ai_score': ai_score,
                'scored_marks': ai_score * marks,
                'type': 'subjective'
            })

    # Calculate final score
    has_subjective = any(q.get('type') == 'subjective' for q in questions)
    
    if has_subjective:
        percentage = (scored_marks / total_marks) * 100 if total_marks > 0 else 0
        passed = percentage >= 60
        final_score = f"{scored_marks:.1f}/{total_marks} marks"
    else:
        percentage = (correct_answers / len(questions)) * 100 if questions else 0
        passed = percentage >= 60
        final_score = f"{correct_answers}/{len(questions)}"

    # Update progress
    progress = db.session.query(Progress).filter_by(user_id=current_user.id, topic=topic).first()
    if progress:
        if passed and bloom_level + 1 > progress.bloom_level:
            progress.bloom_level = bloom_level + 1
    else:
        new_progress = Progress(
            user_id=current_user.id,
            topic=topic,
            bloom_level=bloom_level + 1 if passed else bloom_level
        )
        db.session.add(new_progress)
    
    db.session.commit()

    # Clear quiz session
    session.pop('current_quiz', None)

    return render_template('quiz_results.html', 
                         results=results, 
                         final_score=final_score, 
                         percentage=percentage, 
                         passed=passed,
                         topic=topic,
                         bloom_level=bloom_level,
                         difficulty_level=difficulty_level)

@app.route('/next_level', methods=['POST'])
@login_required
def next_level():
    """Automatically generate next level quiz and redirect to take_quiz"""
    try:
        topic = request.form.get('topic', '').strip()
        difficulty_level = request.form.get('difficulty_level', 'beginner').strip()
        
        if not topic:
            flash('Topic is required', 'error')
            return redirect(url_for('quiz'))
        
        # Determine next difficulty level
        difficulty_mapping = {
            "beginner": "intermediate",
            "intermediate": "difficult", 
            "difficult": "difficult"  # Stay at difficult if already at highest level
        }
        next_difficulty = difficulty_mapping.get(difficulty_level, "intermediate")
        
        # Generate questions for next level
        questions = generate_quiz(topic, next_difficulty, "mcq", 5)
        
        if questions:
            session['current_quiz'] = {
                'questions': questions,
                'topic': topic,
                'bloom_level': 1,  # This will be updated based on difficulty
                'difficulty_level': next_difficulty
            }
            flash(f'Generated {next_difficulty.title()} level quiz for {topic}!', 'success')
            return redirect(url_for('take_quiz'))
        else:
            flash('Failed to generate next level quiz', 'error')
            return redirect(url_for('quiz'))
    except Exception as e:
        print(f"Error in next_level: {str(e)}")
        flash('An error occurred while generating the next level quiz', 'error')
        return redirect(url_for('quiz'))

@app.route('/retry_level', methods=['POST'])
@login_required
def retry_level():
    """Automatically generate retry quiz and redirect to take_quiz"""
    try:
        topic = request.form.get('topic', '').strip()
        difficulty_level = request.form.get('difficulty_level', 'beginner').strip()
        
        if not topic:
            flash('Topic is required', 'error')
            return redirect(url_for('quiz'))
        
        # Generate questions for the same level
        questions = generate_quiz(topic, difficulty_level, "mcq", 5)
        
        if questions:
            session['current_quiz'] = {
                'questions': questions,
                'topic': topic,
                'bloom_level': 1,  # This will be updated based on difficulty
                'difficulty_level': difficulty_level
            }
            flash(f'Generated new {difficulty_level.title()} level quiz for {topic}!', 'success')
            return redirect(url_for('take_quiz'))
        else:
            flash('Failed to generate retry quiz', 'error')
            return redirect(url_for('quiz'))
    except Exception as e:
        print(f"Error in retry_level: {str(e)}")
        flash('An error occurred while generating the retry quiz', 'error')
        return redirect(url_for('quiz'))

@app.route('/continue_learning', methods=['POST'])
@login_required
def continue_learning():
    """Continue learning from where user left off based on their progress"""
    try:
        topic = request.form.get('topic', '').strip()
        
        if not topic:
            flash('Topic is required', 'error')
            return redirect(url_for('dashboard'))
        
        # Get user's current progress for this topic
        progress = db.session.query(Progress).filter_by(user_id=current_user.id, topic=topic).first()
        
        if not progress:
            flash('No progress found for this topic', 'error')
            return redirect(url_for('dashboard'))
        
        # Map bloom level to difficulty level
        difficulty_level = get_difficulty_from_bloom_level(progress.bloom_level)
        
        # Generate questions for the current level
        questions = generate_quiz(topic, difficulty_level, "mcq", 5)
        
        if questions:
            session['current_quiz'] = {
                'questions': questions,
                'topic': topic,
                'bloom_level': progress.bloom_level,
                'difficulty_level': difficulty_level
            }
            flash(f'Continuing {topic} at {difficulty_level.title()} level (Bloom Level {progress.bloom_level})!', 'success')
            return redirect(url_for('take_quiz'))
        else:
            flash('Failed to generate quiz for continuing learning', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Error in continue_learning: {str(e)}")
        flash('An error occurred while continuing your learning', 'error')
        return redirect(url_for('dashboard'))

@app.route('/upload_pdf', methods=['POST'])
@login_required
def upload_pdf():
    """Handle PDF upload and extract topic"""
    if 'file_upload' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file_upload']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if file and file.filename.lower().endswith('.pdf'):
        try:
            # Save file temporarily
            import tempfile
            import os
            
            # Ensure temp directory exists
            temp_dir = tempfile.gettempdir()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir) as tmp_file:
                file.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            original_filename = file.filename
            print(f"Processing PDF: {original_filename} (saved to {tmp_path})")
            
            # Process the PDF to extract topic
            topic = process_document(tmp_path)
            
            # If no topic extracted, try filename extraction using original filename
            if not topic:
                print("No topic extracted from PDF content, trying filename extraction...")
                # Create a mock path with original filename for extraction
                import os
                temp_dir = os.path.dirname(tmp_path)
                mock_path = os.path.join(temp_dir, original_filename)
                topic = extract_topic_from_filename(mock_path)
            
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except Exception as cleanup_error:
                print(f"Warning: Could not delete temp file: {cleanup_error}")
            
            if topic:
                print(f"Successfully extracted topic: {topic}")
                return jsonify({'success': True, 'topic': topic, 'message': f'Topic extracted: {topic}'})
            else:
                # Provide helpful error message
                error_msg = (
                    'Could not extract topic from PDF. This might happen if:\n'
                    '- The PDF is scanned (image-based)\n'
                    '- The PDF is encrypted or protected\n'
                    '- The PDF contains no text\n'
                    'Please enter the topic manually.'
                )
                return jsonify({'success': False, 'error': error_msg})
                
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            error_msg = f'Error processing PDF: {str(e)}. Please try again or enter topic manually.'
            return jsonify({'success': False, 'error': error_msg})
    
    return jsonify({'success': False, 'error': 'Invalid file format. Please upload a PDF file.'})

@app.route('/ai_learn', methods=['POST'])
@login_required
def ai_learn():
    """AI-powered learning content generation"""
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()
        level = data.get('level', 'intermediate')
        style = data.get('style', 'theoretical')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'})
        
        # Generate learning content using AI
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"""
        Create a personalized learning path for {topic} at {level} level, 
        focusing on {style} learning style.
        
        IMPORTANT: You MUST use this EXACT format with these EXACT section headers:
        
        ## OVERVIEW
        [Write a brief 2-3 sentence overview of the topic here]
        
        ## KEY CONCEPTS
        • [Write concept 1 with brief explanation here]
        • [Write concept 2 with brief explanation here]
        • [Write concept 3 with brief explanation here]
        
        ## LEARNING OBJECTIVES
        ✓ [Write objective 1 here]
        ✓ [Write objective 2 here]
        ✓ [Write objective 3 here]
        
        ## STUDY APPROACH
        [Write practical study recommendations based on {style} learning style here]
        
        ## COMMON MISCONCEPTIONS
        ⚠️ [Write misconception 1 and why it's wrong here]
        ⚠️ [Write misconception 2 and why it's wrong here]
        
        ## NEXT STEPS
        [Write what to do after understanding these basics here]
        
        CRITICAL: Start your response immediately with "## OVERVIEW" and follow the exact format above. Do not add any introductory text or explanations before the sections.
        """
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        return jsonify({'success': True, 'content': content})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error generating learning content: {str(e)}'})

@app.route('/download_pdf')
@login_required
def download_pdf():
    quiz_data = session.get('current_quiz')
    if not quiz_data:
        return jsonify({'error': 'No quiz available'})

    questions = quiz_data['questions']
    topic = quiz_data['topic']
    bloom_level = quiz_data['bloom_level']

    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.black
    )
    option_style = ParagraphStyle(
        'Option',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=6,
        textColor=colors.black
    )
    
    content = []
    content.append(Paragraph(f"Quiz: {topic}", title_style))
    content.append(Paragraph(f"Bloom's Taxonomy Level: {bloom_level}", styles['Heading2']))
    content.append(Spacer(1, 20))
    
    for i, q in enumerate(questions, 1):
        question_text = f"Q{i}. {q['question']}"
        content.append(Paragraph(question_text, question_style))
        
        if q.get('type') == 'mcq':
            for opt in q['options']:
                option_text = f"□ {opt}"
                content.append(Paragraph(option_text, option_style))
        else:
            content.append(Paragraph(f"Marks: {q.get('marks', 10)}", option_style))
            content.append(Paragraph("Answer: ________________________", option_style))
        
        content.append(Spacer(1, 20))
    
    doc.build(content)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"Quiz_{topic}_Level{bloom_level}.pdf",
        mimetype='application/pdf'
    )

@app.route('/admin/users')
@login_required
def admin_users():
    """Admin route to view user statistics - ADMIN ONLY"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Access denied: Administrator privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        from sqlalchemy import text, func
        from datetime import datetime, timedelta
        
        # Get total users
        total_users = db.session.query(func.count(User.id)).scalar()
        
        # Get users by role
        users_by_role = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        # Get users this month
        this_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        users_this_month = db.session.query(func.count(User.id)).filter(
            User.created_at >= this_month_start
        ).scalar()
        
        # Get users this week
        this_week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        this_week_start = this_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        users_this_week = db.session.query(func.count(User.id)).filter(
            User.created_at >= this_week_start
        ).scalar()
        
        # Get users today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        users_today = db.session.query(func.count(User.id)).filter(
            User.created_at >= today_start
        ).scalar()
        
        # Get recent signups (last 10)
        recent_users = db.session.query(User).order_by(
            User.created_at.desc()
        ).limit(10).all()
        
        # Get signups by date (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        signups_by_date = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= thirty_days_ago
        ).group_by(
            func.date(User.created_at)
        ).order_by(
            func.date(User.created_at).desc()
        ).all()
        
        # === LOGIN STATISTICS ===
        # Total logins (all time)
        total_logins = db.session.query(func.count(LoginHistory.id)).scalar() or 0
        
        # Unique users who have logged in
        unique_logged_in_users = db.session.query(func.count(func.distinct(LoginHistory.user_id))).scalar() or 0
        
        # Logins today
        logins_today = db.session.query(func.count(LoginHistory.id)).filter(
            LoginHistory.login_time >= today_start
        ).scalar() or 0
        
        # Logins this week
        logins_this_week = db.session.query(func.count(LoginHistory.id)).filter(
            LoginHistory.login_time >= this_week_start
        ).scalar() or 0
        
        # Logins this month
        logins_this_month = db.session.query(func.count(LoginHistory.id)).filter(
            LoginHistory.login_time >= this_month_start
        ).scalar() or 0
        
        # Logins by date (last 30 days)
        logins_by_date = db.session.query(
            func.date(LoginHistory.login_time).label('date'),
            func.count(LoginHistory.id).label('count')
        ).filter(
            LoginHistory.login_time >= thirty_days_ago
        ).group_by(
            func.date(LoginHistory.login_time)
        ).order_by(
            func.date(LoginHistory.login_time).desc()
        ).all()
        
        # Recent logins (last 20)
        recent_logins = db.session.query(LoginHistory).join(User).order_by(
            LoginHistory.login_time.desc()
        ).limit(20).all()
        
        # Most active users (by login count)
        most_active_users = db.session.query(
            User.username,
            User.email,
            func.count(LoginHistory.id).label('login_count'),
            func.max(LoginHistory.login_time).label('last_login')
        ).outerjoin(
            LoginHistory, User.id == LoginHistory.user_id
        ).group_by(
            User.id, User.username, User.email
        ).having(
            func.count(LoginHistory.id) > 0
        ).order_by(
            func.count(LoginHistory.id).desc()
        ).limit(10).all()
        
        # Convert users_by_role to dictionary
        users_by_role_dict = {role: count for role, count in users_by_role} if users_by_role else {}
        
        return render_template('admin_users.html',
            total_users=total_users or 0,
            users_by_role=users_by_role_dict,
            users_this_month=users_this_month or 0,
            users_this_week=users_this_week or 0,
            users_today=users_today or 0,
            recent_users=recent_users,
            signups_by_date=signups_by_date,
            # Login statistics
            total_logins=total_logins,
            unique_logged_in_users=unique_logged_in_users,
            logins_today=logins_today,
            logins_this_week=logins_this_week,
            logins_this_month=logins_this_month,
            logins_by_date=logins_by_date,
            recent_logins=recent_logins,
            most_active_users=most_active_users
        )
    except Exception as e:
        print(f"Error in admin_users: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading user statistics: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# Error handlers
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error="Internal Server Error"), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page Not Found"), 404

# Initialize database tables
def init_db():
    try:
        with app.app_context():
            db.create_all()
            
            # Check if we need to add the role column to existing user table
            try:
                from sqlalchemy import text
                # Check if role column exists
                result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='role'"))
                if not result.fetchone():
                    # Add role column if it doesn't exist
                    db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN role VARCHAR(20) DEFAULT 'student'"))
                    db.session.commit()
                    print("Added role column to user table")
            except Exception as e:
                print(f"Role column check/add failed (may already exist): {e}")
            
            # Check if we need to update password_hash column length
            try:
                from sqlalchemy import text
                # Check current password_hash column length
                result = db.session.execute(text("SELECT character_maximum_length FROM information_schema.columns WHERE table_name='user' AND column_name='password_hash'"))
                row = result.fetchone()
                if row and row[0] < 255:
                    # Update password_hash column to be longer
                    db.session.execute(text("ALTER TABLE \"user\" ALTER COLUMN password_hash TYPE VARCHAR(255)"))
                    db.session.commit()
                    print("Updated password_hash column length to 255")
            except Exception as e:
                print(f"Password hash column update failed (may already be correct): {e}")
            
            # Check if is_admin column exists, if not add it
            try:
                from sqlalchemy import text
                result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='is_admin'"))
                if not result.fetchone():
                    db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
                    db.session.commit()
                    print("Added is_admin column to user table")
            except Exception as e:
                print(f"is_admin column check/add failed (may already exist): {e}")
            
            # Check if last_login column exists, if not add it
            try:
                from sqlalchemy import text
                result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user' AND column_name='last_login'"))
                if not result.fetchone():
                    db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN last_login TIMESTAMP"))
                    db.session.commit()
                    print("Added last_login column to user table")
            except Exception as e:
                print(f"last_login column check/add failed (may already exist): {e}")
            
            # Create login_history table if it doesn't exist
            try:
                db.create_all()
                print("Created login_history table if it didn't exist")
            except Exception as e:
                print(f"Login history table creation failed (may already exist): {e}")
            
            print("Database tables created successfully!")
            print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        # Continue running the app even if database fails

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

