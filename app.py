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
from datetime import datetime

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

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure Google AI
genai.configure(api_key=os.environ.get('GOOGLE_AI_API_KEY', 'AIzaSyDUPxvPmawZHRJf2KD6GAGvhY8uVkTh-u4'))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)  # 'student' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    qtype = db.Column(db.String(20), default='mcq')  # 'mcq' or 'subjective'
    marks = db.Column(db.Integer, default=1)

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

        return questions

    except Exception as e:
        print(f"Error in generate_quiz: {str(e)}")
        return None

def process_document(file_path):
    """Process uploaded document to extract content"""
    try:
        # Ensure NLTK data is available
        ensure_nltk_data()
        
        content = ""
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text()
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

        if not content.strip():
            return None

        tokens = word_tokenize(content.lower())
        stop_words = set(stopwords.words('english'))
        meaningful_words = [word for word in tokens if word.isalnum() and word not in stop_words]

        if not meaningful_words:
            return None

        word_freq = Counter(meaningful_words)
        main_topic = word_freq.most_common(1)[0][0].capitalize()
        return main_topic

    except Exception as e:
        print(f"Error processing document: {str(e)}")
        return None

# Routes
@app.route('/')
def home():
    try:
        # Initialize database on first access
        init_db()
        return render_template('home.html')
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        # Return a simple HTML response instead of trying to render error template
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>UniTest - Error</title></head>
        <body>
            <h1>UniTest AI Learning Platform</h1>
            <p>Error: {str(e)}</p>
            <p>Please check the logs for more details.</p>
        </body>
        </html>
        """, 500

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

@app.route('/sitemap.xml')
def sitemap():
    return send_file('static/sitemap.xml', mimetype='application/xml')

@app.route('/robots.txt')
def robots():
    return send_file('static/robots.txt', mimetype='text/plain')

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
                return """
                <!DOCTYPE html>
                <html>
                <head><title>Sign Up - UniTest</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                    <h2>Create Account</h2>
                    <div style="background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        Please fill in all fields
                    </div>
                    <form method="POST">
                        <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="email" name="email" placeholder="Email" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="confirm_password" placeholder="Confirm Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><select name="role" style="width: 100%; padding: 10px; margin: 5px 0;">
                            <option value="student">Student</option>
                            <option value="teacher">Teacher</option>
                        </select></p>
                        <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Sign Up</button></p>
                    </form>
                    <p><a href="/login">Already have an account? Login</a></p>
                    <p><a href="/">← Back to Home</a></p>
                </body>
                </html>
                """

            if password != confirm_password:
                return """
                <!DOCTYPE html>
                <html>
                <head><title>Sign Up - UniTest</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                    <h2>Create Account</h2>
                    <div style="background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        Passwords do not match
                    </div>
                    <form method="POST">
                        <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="email" name="email" placeholder="Email" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="confirm_password" placeholder="Confirm Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><select name="role" style="width: 100%; padding: 10px; margin: 5px 0;">
                            <option value="student">Student</option>
                            <option value="teacher">Teacher</option>
                        </select></p>
                        <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Sign Up</button></p>
                    </form>
                    <p><a href="/login">Already have an account? Login</a></p>
                    <p><a href="/">← Back to Home</a></p>
                </body>
                </html>
                """

            # Check if user exists
            existing_user = db.session.query(User).filter_by(username=username).first()
            if existing_user:
                return """
                <!DOCTYPE html>
                <html>
                <head><title>Sign Up - UniTest</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                    <h2>Create Account</h2>
                    <div style="background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        Username already exists
                    </div>
                    <form method="POST">
                        <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="email" name="email" placeholder="Email" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="confirm_password" placeholder="Confirm Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><select name="role" style="width: 100%; padding: 10px; margin: 5px 0;">
                            <option value="student">Student</option>
                            <option value="teacher">Teacher</option>
                        </select></p>
                        <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Sign Up</button></p>
                    </form>
                    <p><a href="/login">Already have an account? Login</a></p>
                    <p><a href="/">← Back to Home</a></p>
                </body>
                </html>
                """

            existing_email = db.session.query(User).filter_by(email=email).first()
            if existing_email:
                return """
                <!DOCTYPE html>
                <html>
                <head><title>Sign Up - UniTest</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                    <h2>Create Account</h2>
                    <div style="background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        Email already exists
                    </div>
                    <form method="POST">
                        <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="email" name="email" placeholder="Email" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="confirm_password" placeholder="Confirm Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><select name="role" style="width: 100%; padding: 10px; margin: 5px 0;">
                            <option value="student">Student</option>
                            <option value="teacher">Teacher</option>
                        </select></p>
                        <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Sign Up</button></p>
                    </form>
                    <p><a href="/login">Already have an account? Login</a></p>
                    <p><a href="/">← Back to Home</a></p>
                </body>
                </html>
                """

            # Create new user
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role=role if role in ['student','teacher'] else 'student'
            )
            db.session.add(user)
            db.session.commit()

            return """
            <!DOCTYPE html>
            <html>
            <head><title>Sign Up Success - UniTest</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                <h2>Account Created Successfully!</h2>
                <div style="background: #e8f5e8; color: #2e7d32; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    Your account has been created. Please login to continue.
                </div>
                <p><a href="/login" style="display: inline-block; background: #4285f4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login Now</a></p>
                <p><a href="/">← Back to Home</a></p>
            </body>
            </html>
            """
        except Exception as e:
            print(f"Error in signup: {str(e)}")
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Sign Up Error - UniTest</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                <h2>Create Account</h2>
                <div style="background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    An error occurred: {str(e)}
                </div>
                <form method="POST">
                    <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                    <p><input type="email" name="email" placeholder="Email" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                    <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                    <p><input type="password" name="confirm_password" placeholder="Confirm Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                    <p><select name="role" style="width: 100%; padding: 10px; margin: 5px 0;">
                        <option value="student">Student</option>
                        <option value="teacher">Teacher</option>
                    </select></p>
                    <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Sign Up</button></p>
                </form>
                <p><a href="/login">Already have an account? Login</a></p>
                <p><a href="/">← Back to Home</a></p>
            </body>
            </html>
            """

    return """
    <!DOCTYPE html>
    <html>
    <head><title>Sign Up - UniTest</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
        <h2>Create Account</h2>
        <form method="POST">
            <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
            <p><input type="email" name="email" placeholder="Email" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
            <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
            <p><input type="password" name="confirm_password" placeholder="Confirm Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
            <p><select name="role" style="width: 100%; padding: 10px; margin: 5px 0;">
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
            </select></p>
            <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Sign Up</button></p>
        </form>
        <p><a href="/login">Already have an account? Login</a></p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']

            user = db.session.query(User).filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return """
                <!DOCTYPE html>
                <html>
                <head><title>Login Success - UniTest</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                    <h2>Login Successful!</h2>
                    <div style="background: #e8f5e8; color: #2e7d32; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        Welcome back, {username}! You are now logged in.
                    </div>
                    <p><a href="/dashboard" style="display: inline-block; background: #4285f4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Dashboard</a></p>
                    <p><a href="/">← Back to Home</a></p>
                </body>
                </html>
                """.format(username=username)
            else:
                return """
                <!DOCTYPE html>
                <html>
                <head><title>Login Error - UniTest</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                    <h2>Login</h2>
                    <div style="background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; margin: 10px 0;">
                        Invalid username or password
                    </div>
                    <form method="POST">
                        <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                        <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Login</button></p>
                    </form>
                    <p><a href="/signup">Don't have an account? Sign Up</a></p>
                    <p><a href="/">← Back to Home</a></p>
                </body>
                </html>
                """
        except Exception as e:
            print(f"Error in login: {str(e)}")
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>Login Error - UniTest</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
                <h2>Login</h2>
                <div style="background: #ffebee; color: #c62828; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    An error occurred: {str(e)}
                </div>
                <form method="POST">
                    <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                    <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
                    <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Login</button></p>
                </form>
                <p><a href="/signup">Don't have an account? Sign Up</a></p>
                <p><a href="/">← Back to Home</a></p>
            </body>
            </html>
            """

    return """
    <!DOCTYPE html>
    <html>
    <head><title>Login - UniTest</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px;">
        <h2>Login</h2>
        <form method="POST">
            <p><input type="text" name="username" placeholder="Username" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
            <p><input type="password" name="password" placeholder="Password" required style="width: 100%; padding: 10px; margin: 5px 0;"></p>
            <p><button type="submit" style="width: 100%; padding: 10px; background: #4285f4; color: white; border: none; border-radius: 5px;">Login</button></p>
        </form>
        <p><a href="/signup">Don't have an account? Sign Up</a></p>
        <p><a href="/">← Back to Home</a></p>
    </body>
    </html>
    """

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
    return render_template('dashboard.html', progress_records=progress_records, my_quizzes=my_quizzes, my_submissions=my_submissions)

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

            questions = generate_quiz(topic, difficulty if difficulty in ['beginner','intermediate','advanced'] else 'beginner', 'mcq', count) or []
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
            opts = q.get('options', [])
            qq = QuizQuestion(
                quiz_id=quiz.id,
                question=q.get('question', ''),
                options_json=json.dumps(opts) if opts else None,
                answer=q.get('answer', ''),
                qtype='mcq',
                marks=int(q.get('marks', 1))
            )
            db.session.add(qq)

        db.session.commit()
        session.pop('preview_quiz', None)
        flash(f'Quiz created! Share code: {code}', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        print(f"Finalize error: {e}")
        flash('Error finalizing quiz.', 'error')
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
    q_rows = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()
    # Parse options JSON server-side to avoid template errors
    parsed_questions = []
    for q in q_rows:
        try:
            options = json.loads(q.options_json) if q.options_json else []
        except Exception:
            options = []
        parsed_questions.append({
            'id': q.id,
            'question': q.question,
            'qtype': q.qtype,
            'marks': q.marks,
            'options': options,
        })
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
    questions = db.session.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()

    total_marks = 0.0
    scored_marks = 0.0
    from datetime import timedelta
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

        if q.qtype == 'mcq':
            is_correct = (user_ans.split('. ')[0] == (q.answer or '')) if user_ans else False
            gained = float(q.marks or 1) if is_correct else 0.0
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
            scored_marks=gained
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
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                file.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            # Process the PDF to extract topic
            topic = process_document(tmp_path)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            if topic:
                return jsonify({'success': True, 'topic': topic})
            else:
                return jsonify({'success': False, 'error': 'Could not extract topic from PDF'})
                
        except Exception as e:
            return jsonify({'success': False, 'error': f'Error processing PDF: {str(e)}'})
    
    return jsonify({'success': False, 'error': 'Invalid file format. Please upload a PDF.'})

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
            print("Database tables created successfully!")
            print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        # Continue running the app even if database fails

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

