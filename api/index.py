import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import json
import re
from collections import Counter
import io
from datetime import datetime

app = Flask(__name__, instance_path='/tmp')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
elif database_url and database_url.startswith('postgresql://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unittest.db'
    print("Warning: Using SQLite database. Set DATABASE_URL environment variable for production.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
print(f"Database URL configured: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")

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
    password_hash = db.Column(db.String(255), nullable=False)  # Increased from 120 to 255
    role = db.Column(db.String(20), default='student', nullable=False)  # 'student' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    bloom_level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

def generate_quiz(topic, difficulty_level, question_type="mcq", num_questions=5):
    if not genai:
        return None

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
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

# Routes
@app.route('/')
def home():
    """Public home route - no login required, accessible to everyone"""
    # This route must be public for SEO and Google indexing
    try:
        # Use the proper home template - no database initialization needed
        return render_template('home.html')
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        import traceback
        traceback.print_exc()
        # Fallback HTML if template fails
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>UNITEST - AI-Powered Learning Platform</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5;">
            <div style="max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px;">
                <h1 style="color: #4285f4; text-align: center;">🎓 UNITEST AI Learning Platform</h1>
                <p style="text-align: center; margin: 20px 0;">
                    <a href="/signup" style="background: #4285f4; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 5px;">Sign Up</a>
                    <a href="/login" style="background: #34a853; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 5px;">Login</a>
                </p>
                <p>Welcome to UNITEST - Search "UNITEST" to find the best AI-powered quiz generator platform.</p>
            </div>
        </body>
        </html>
        """

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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Public signup route - no login required"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
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
                role=role if role in ['student', 'teacher'] else 'student'
            )
            db.session.add(user)
            db.session.commit()

            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error in signup: {str(e)}")
            import traceback
            traceback.print_exc()
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
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Exception as e:
            print(f"Error in login: {str(e)}")
            flash('An error occurred. Please try again.', 'error')

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
    return render_template('dashboard.html', progress_records=progress_records)

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'GET':
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
        
        if not topic:
            flash('Please enter a topic.', 'error')
            return redirect(url_for('quiz'))

        progress = db.session.query(Progress).filter_by(user_id=current_user.id, topic=topic).first()
        bloom_level = progress.bloom_level if progress else 1

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
    
    user_answers = []
    for i in range(len(questions)):
        question = questions[i]
        if question.get('type') == 'mcq':
            answer = request.form.get(f'question_{i}')
        else:
            answer = request.form.get(f'subjective_answers[{i}]')
        
        if not answer:
            return jsonify({'error': f'Please answer question {i+1}'})
        user_answers.append(answer)

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

    has_subjective = any(q.get('type') == 'subjective' for q in questions)
    
    if has_subjective:
        percentage = (scored_marks / total_marks) * 100 if total_marks > 0 else 0
        passed = percentage >= 60
        final_score = f"{scored_marks:.1f}/{total_marks} marks"
    else:
        percentage = (correct_answers / len(questions)) * 100 if questions else 0
        passed = percentage >= 60
        final_score = f"{correct_answers}/{len(questions)}"

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
    session.pop('current_quiz', None)

    return render_template('quiz_results.html', 
                         results=results, 
                         final_score=final_score, 
                         percentage=percentage, 
                         passed=passed,
                         topic=topic,
                         bloom_level=bloom_level,
                         difficulty_level=difficulty_level)

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

# For Vercel deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # This is the entry point for Vercel
    pass
