"""
Vercel entrypoint.

Keep all application logic in `app.py` and only expose `app` here so Vercel
doesn't deploy a stale duplicated copy of the Flask app.
"""

from app import app  # noqa: F401

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



            if not all([username, email, password, confirm_password]):

                flash('Please fill in all fields', 'error')

                return redirect(url_for('signup'))



            if password != confirm_password:

                flash('Passwords do not match', 'error')

                return redirect(url_for('signup'))



            if db.session.query(User).filter_by(username=username).first():

                flash('Username already exists', 'error')

                return redirect(url_for('signup'))



            if db.session.query(User).filter_by(email=email).first():

                flash('Email already exists', 'error')

                return redirect(url_for('signup'))



            user = User(

                username=username,

                email=email,

                password_hash=generate_password_hash(password)

            )

            db.session.add(user)

            db.session.commit()



            flash('Account created successfully! Please login.', 'success')

            return redirect(url_for('login'))

        except Exception as e:

            print(f"Error in signup: {str(e)}")

            flash('An error occurred. Please try again.', 'error')

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


