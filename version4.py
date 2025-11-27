MAIN_BG = "#ffffff"  
PRIMARY_COLOR = "#2c3e50"  
SECONDARY_COLOR = "#34495e" 
ACCENT_COLOR = "#e74c3c"
TEXT_DARK = "#2c3e50"  
TEXT_LIGHT = "#95a5a6"  

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import mysql.connector
import json
import re
import PyPDF2
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os
from PIL import Image, ImageTk
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

GRADIENT_BG = "#1a73e8"  
GRADIENT_FG = "#4285f4"  
ACCENT_COLOR = "#34a853"  
TEXT_COLOR = "#202124"   
SECONDARY_TEXT = "#5f6368" 

try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

import google.generativeai as genai

# Replace this with your new API key from https://makersuite.google.com/app/apikey
genai.configure(api_key="AIzaSyBZtUxzv3yLcOLj0kIogfZnITGxHWkWs8Q")

user_id = None
conn = mysql.connector.connect(
    host="localhost", user="root", password="Golu@2209", database="akerman_elite"
)
cursor = conn.cursor()

def add_hover_effect(widget):
    def on_enter(e):
        widget.config(bg="#4CAF50", fg="white")
    def on_leave(e):
        widget.config(bg="#2C3E50", fg="white")

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def style_button(button, is_primary=True):
    if is_primary:
        button.configure(
            bg=GRADIENT_BG,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            bd=0,
            padx=25,
            pady=10,
            cursor="hand2"
        )
    else:
        button.configure(
            bg="white",
            fg=GRADIENT_BG,
            font=("Segoe UI", 12),
            bd=1,
            padx=25,
            pady=10,
            cursor="hand2"
        )

    def on_enter(e):
        button['bg'] = ACCENT_COLOR if is_primary else "#f8f9fa"
    def on_leave(e):
        button['bg'] = GRADIENT_BG if is_primary else "white"

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

def clear_window():
    for widget in root.winfo_children():
        widget.destroy()

def add_back_button(parent, target_function=None):
    back_frame = tk.Frame(parent, bg="white")
    back_frame.pack(fill=tk.X, pady=(10,0))

    def back_to_target():
        clear_window()
        if target_function:
            target_function()
        elif user_id:  
            dashboard(user_id)
        else:  
            create_home_ui()

    back_btn = tk.Button(
        back_frame,
        text="← Back",
        bg="white",
        fg="#4285f4",
        bd=0,
        font=("Arial", 10),
        command=back_to_target
    )
    back_btn.pack(side=tk.LEFT, padx=20)

def signup():
    def register_user():
        username = entry_username.get()
        email = entry_email.get()
        password = entry_password.get()
        confirm_pass = entry_confirm.get()

        if not all([username, email, password, confirm_pass]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        if password != confirm_pass:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if not email.count("@") or not email.count("."):
            messagebox.showerror("Error", "Invalid email format")
            return

        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                         (username, email, password))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            login()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Username or email already exists")

    clear_window()
    root.configure(bg="white")
    add_back_button(root)

    tk.Label(
        root,
        text="Sign Up",
        font=("Helvetica", 28, "bold"),
        fg="#4285f4",
        bg="white"
    ).pack(pady=(20,0))

    container = tk.Frame(root, bg="white")
    container.place(relx=0.5, rely=0.5, anchor="center")

    main_frame = tk.Frame(container, bg="white", bd=2, relief="solid")
    main_frame.pack(padx=40, pady=20)

    entry_username = tk.Entry(main_frame, width=40, font=("Helvetica", 12), bd=2, relief="solid")
    entry_email = tk.Entry(main_frame, width=40, font=("Helvetica", 12), bd=2, relief="solid")
    entry_password = tk.Entry(main_frame, width=40, font=("Helvetica", 12), show='•', bd=2, relief="solid")
    entry_confirm = tk.Entry(main_frame, width=40, font=("Helvetica", 12), show='•', bd=2, relief="solid")

    fields = [
        ("Username", entry_username),
        ("Email", entry_email),
        ("Password", entry_password),
        ("Confirm Password", entry_confirm)
    ]

    for lbl, entry in fields:
        tk.Label(
            main_frame,
            text=lbl,
            fg="#333333",
            bg="white",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w", padx=20, pady=(15,5))
        entry.pack(pady=(0,10), ipady=8)

    btn_submit = tk.Button(
        main_frame,
        text="Create Account",
        bg="#4285f4",
        fg="white",
        font=("Helvetica", 14, "bold"),
        padx=30,
        pady=12,
        bd=0,
        cursor="hand2",
        command=register_user
    )
    btn_submit.pack(pady=30)

    login_frame = tk.Frame(main_frame, bg="white")
    login_frame.pack(pady=(0,20))
    tk.Label(
        login_frame,
        text="Already have an account?",
        fg="#666666",
        bg="white",
        font=("Helvetica", 10)
    ).pack(side=tk.LEFT)

    login_link = tk.Label(
        login_frame,
        text="Login",
        fg="#4285f4",
        bg="white",
        font=("Helvetica", 10, "bold"),
        cursor="hand2"
    )
    login_link.pack(side=tk.LEFT, padx=(5,0))
    login_link.bind("<Button-1>", lambda e: login())

def login():
    global user_id
    def validate_login():
        username, password = entry_username.get(), entry_password.get()
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        cursor.execute("SELECT id FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            user_id = user[0]
            dashboard(user_id)
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    clear_window()
    root.configure(bg="white")

    add_back_button(root)

    container = tk.Frame(root, bg="white", padx=50, pady=30)
    container.pack(expand=True)

    main_frame = tk.Frame(container, bg="white", bd=2, relief="solid")
    main_frame.pack(padx=20, pady=20, ipadx=30, ipady=20)

    tk.Label(
        main_frame,
        text="Welcome Back!",
        font=("Helvetica", 28, "bold"),
        fg="#4285f4",
        bg="white"
    ).pack(pady=(20,10))

    tk.Label(
        main_frame,
        text="Sign in to continue",
        font=("Helvetica", 12),
        fg="#666666",
        bg="white"
    ).pack(pady=(0,20))

    entry_username = tk.Entry(
        main_frame,
        width=40,
        font=("Helvetica", 12),
        bd=2,
        relief="solid"
    )
    entry_password = tk.Entry(
        main_frame,
        width=40,
        font=("Helvetica", 12),
        show='•',
        bd=2,
        relief="solid"
    )

    for lbl, entry in zip(["Username", "Password"], [entry_username, entry_password]):
        tk.Label(
            main_frame,
            text=lbl,
            fg="#333333",
            bg="white",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w", padx=20, pady=(15,5))
        entry.pack(pady=(0,10), ipady=8)

    btn_submit = tk.Button(
        main_frame,
        text="Login",
        bg="#4285f4",
        fg="white",
        font=("Helvetica", 14, "bold"),
        padx=30,
        pady=12,
        bd=0,
        cursor="hand2",
        command=validate_login
    )
    btn_submit.pack(pady=30)

    signup_frame = tk.Frame(main_frame, bg="white")
    signup_frame.pack(pady=(0,20))
    tk.Label(
        signup_frame,
        text="Don't have an account?",
        fg="#666666",
        bg="white",
        font=("Helvetica", 10)
    ).pack(side=tk.LEFT)

    signup_link = tk.Label(
        signup_frame,
        text="Sign Up",
        fg="#4285f4",
        bg="white",
        font=("Helvetica", 10, "bold"),
        cursor="hand2"
    )
    signup_link.pack(side=tk.LEFT, padx=(5,0))
    signup_link.bind("<Button-1>", lambda e: signup())

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
        print(f"Debug - Error in evaluate_subjective_answer: {str(e)}") # Add debug print
        return 0.5  # Default on error

def save_progress(user_id, topic, bloom_level, questions, user_answers):
    clear_window()
    root.configure(bg="white")

    add_back_button(root, lambda: dashboard(user_id))

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(pady=20, fill="both", expand=True)

    canvas = tk.Canvas(main_frame, bg="white")
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    tk.Label(scrollable_frame, text="Quiz Results", font=("Arial", 24, "bold"), fg="#4285f4", bg="white").pack(pady=10)

    correct_answers = 0
    total_questions = len(questions)
    total_marks = 0
    scored_marks = 0

    # First, process all answers and calculate scores
    for idx, (q, user_ans) in enumerate(zip(questions, user_answers), 1):
        result_frame = tk.Frame(scrollable_frame, bg="white", relief="solid", bd=1)
        result_frame.pack(fill="x", padx=20, pady=10)

        question_text = f"Q{idx}. {q['question']}"
        tk.Label(
            result_frame,
            text=question_text,
            fg="#333333",
            bg="white",
            font=("Arial", 12, "bold"),
            wraplength=600
        ).pack(anchor="w", padx=10, pady=5)

        if q.get('type') == 'mcq':
            user_choice = user_ans.split(". ")[0] if user_ans else ""

            is_correct = user_choice == q["answer"]
            if is_correct:
                correct_answers += 1

            result_color = "#34a853" if is_correct else "#ea4335"  
            tk.Label(
                result_frame,
                text=f"Your answer: {user_ans}",
                fg=result_color,
                bg="white",
                font=("Arial", 11)
            ).pack(anchor="w", padx=10)

            if not is_correct:
                correct_option = next((opt for opt in q["options"] if opt.startswith(f"{q['answer']}.")), "")
                tk.Label(
                    result_frame,
                    text=f"Correct answer: {correct_option}",
                    fg="#34a853",
                    bg="white",
                    font=("Arial", 11, "bold")
                ).pack(anchor="w", padx=10)
        else:  # subjective
            # Get user answer from text widget
            user_text = user_ans # Because it's already a string
            
            if not user_text:
                user_text = "No answer provided"

            marks = q.get('marks', 10)
            total_marks += marks

            tk.Label(
                result_frame,
                text=f"Marks: {marks}",
                fg="#666666",
                bg="white",
                font=("Arial", 10, "bold")
            ).pack(anchor="w", padx=10)

            tk.Label(
                result_frame,
                text=f"Your answer: {user_text[:200]}{'...' if len(user_text) > 200 else ''}",
                fg="#333333",
                bg="white",
                font=("Arial", 11),
                wraplength=600
            ).pack(anchor="w", padx=10)

            tk.Label(
                result_frame,
                text=f"Sample answer: {q.get('answer', 'N/A')[:200]}{'...' if len(q.get('answer', '')) > 200 else ''}",
                fg="#666666",
                bg="white",
                font=("Arial", 11),
                wraplength=600
            ).pack(anchor="w", padx=10)

            # AI evaluation for subjective
            if user_text and user_text != "No answer provided":
                ai_score = evaluate_subjective_answer(q['question'], user_text, q.get('answer', ''))
                scored_marks += ai_score * marks
                
                # Count as correct if score is above 60%
                if ai_score >= 0.6:
                    correct_answers += 1

                tk.Label(
                    result_frame,
                    text=f"AI Score: {ai_score*marks:.1f}/{marks} ({ai_score*100:.0f}%)",
                    fg="#4285f4",
                    bg="white",
                    font=("Arial", 11, "bold")
                ).pack(anchor="w", padx=10, pady=5)
            else:
                tk.Label(
                    result_frame,
                    text=f"AI Score: 0.0/{marks} (0%)",
                    fg="#ea4335",
                    bg="white",
                    font=("Arial", 11, "bold")
                ).pack(anchor="w", padx=10, pady=5)

    score_frame = tk.Frame(scrollable_frame, bg="white")
    score_frame.pack(fill="x", padx=20, pady=20)

    # Calculate if passed
    has_subjective = any(q.get('type') == 'subjective' for q in questions)
    
    if has_subjective:
        if total_marks > 0:
            percentage = (scored_marks / total_marks) * 100
            passed = percentage >= 60
        else:
            percentage = 0
            passed = False
            
        tk.Label(
            score_frame,
            text=f"Total Score: {scored_marks:.1f}/{total_marks} marks",
            fg="#4285f4",
            bg="white",
            font=("Arial", 14, "bold")
        ).pack()
        tk.Label(
            score_frame,
            text=f"Percentage: {percentage:.1f}%",
            fg="#4285f4",
            bg="white",
            font=("Arial", 12)
        ).pack()
    else:
        # MCQ scoring
        percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        passed = percentage >= 60
        
        tk.Label(
            score_frame,
            text=f"Score: {correct_answers}/{total_questions}",
            fg="#4285f4",
            bg="white",
            font=("Arial", 14, "bold")
        ).pack()
        tk.Label(
            score_frame,
            text=f"Percentage: {percentage:.1f}%",
            fg="#4285f4",
            bg="white",
            font=("Arial", 12)
        ).pack()

    # Always save progress first (even if not passed, to track the topic)
    cursor.execute("SELECT bloom_level FROM progress WHERE user_id=%s AND topic=%s", (user_id, topic))
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Update existing record only if passed and new level is higher
        if passed and bloom_level + 1 > existing_record[0]:
            new_bloom_level = bloom_level + 1
            cursor.execute("UPDATE progress SET bloom_level=%s WHERE user_id=%s AND topic=%s", 
                         (new_bloom_level, user_id, topic))
            message = f"Congratulations! Moving to Bloom's Level {new_bloom_level}"
        elif passed:
            new_bloom_level = existing_record[0]
            message = f"Great job! You've already unlocked Level {new_bloom_level}"
        else:
            new_bloom_level = existing_record[0]
            message = f"Keep practicing to improve your score! Currently at Level {new_bloom_level}"
    else:
        # Insert new record
        new_bloom_level = bloom_level + 1 if passed else bloom_level
        cursor.execute("INSERT INTO progress (user_id, topic, bloom_level) VALUES (%s, %s, %s)", 
                     (user_id, topic, new_bloom_level))
        if passed:
            message = f"Congratulations! You've unlocked Bloom's Level {new_bloom_level} for {topic}!"
        else:
            message = f"Keep practicing to improve your score! Currently at Level {bloom_level}"
    
    conn.commit()

    tk.Label(
        score_frame,
        text=message,
        fg="#666666",
        bg="white",
        font=("Arial", 12)
    ).pack(pady=10)

    button_frame = tk.Frame(scrollable_frame, bg="white")
    button_frame.pack(pady=20)

    btn_continue = tk.Button(
        button_frame,
        text="Back to Dashboard",
        bg="#4285f4",
        fg="white",
        font=("Arial", 12),
        padx=20,
        pady=10,
        bd=0,
        command=lambda: dashboard(user_id)
    )
    btn_continue.pack(side=tk.LEFT, padx=10)

    if passed:
        btn_next_level = tk.Button(
            button_frame,
            text="Try Next Level",
            bg="#34a853", 
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=10,
            bd=0,
            command=lambda: display_quiz(user_id, generate_quiz(topic, bloom_level + 1, questions[0].get('type', 'mcq'), len(questions)), topic, bloom_level + 1)
        )
        btn_next_level.pack(side=tk.LEFT, padx=10)
    else:
        btn_retry = tk.Button(
            button_frame,
            text="Retry Level",
            bg="#ea4335",  
            fg="white",
            font=("Arial", 12),
            padx=20,
            pady=10,
            bd=0,
            command=lambda: display_quiz(user_id, generate_quiz(topic, bloom_level, questions[0].get('type', 'mcq'), len(questions)), topic, bloom_level)
        )
        btn_retry.pack(side=tk.LEFT, padx=10)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def generate_quiz(topic, bloom_level, question_type="mcq", num_questions=5):
    if not genai:
        messagebox.showerror("Error", "AI service is not initialized")
        return None

    try:
        print(f"Debug - Generating quiz for topic: {topic}, type: {question_type}, count: {num_questions}")  # Debug print
        
        model = genai.GenerativeModel("gemini-2.0-flash")  

        if question_type == "mcq":
            prompt = f"""
                Generate a multiple-choice quiz on {topic} at Bloom's Taxonomy level {bloom_level}.
                - Include exactly {num_questions} questions.
                - Each question should have 4 answer choices.
                - Include a "level" key specifying the Bloom's Taxonomy level (Remembering, Understanding, Applying, etc.).
                - Return output in valid JSON format: 
                [
                    {{"question": "What is AI?", "options": ["A. option1", "B. option2", "C. option3", "D. option4"], "answer": "A", "type": "mcq"}},
                    ...
                ]
            """
        else:  # subjective
            prompt = f"""
                Generate subjective questions on {topic} at Bloom's Taxonomy level {bloom_level}.
                - Include exactly {num_questions} questions.
                - Questions should be open-ended and require detailed answers.
                - Include a "level" key specifying the Bloom's Taxonomy level.
                - Vary the marks between 5, 10, 15, and 20 marks for different questions.
                - Return output in valid JSON format: 
                [
                    {{"question": "Explain the concept of AI and its applications", "answer": "Sample answer explaining AI...", "type": "subjective", "marks": 10}},
                    ...
                ]
            """

        print(f"Debug - Sending prompt to AI")  # Debug print
        response = model.generate_content(prompt)
        print(f"Debug - Received response from AI")  # Debug print

        if not response.text:
            print("Debug - Empty response from AI")  # Debug print
            raise ValueError("Empty response from AI")

        print(f"Debug - Processing AI response")  # Debug print
        json_match = re.search(r"```json\n(.*)\n```", response.text, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group(1))
        else:
            try:
                questions = json.loads(response.text)
            except:
                print("Debug - Invalid JSON response")  # Debug print
                raise ValueError("Invalid response format from AI")

        print(f"Debug - Successfully generated {len(questions)} questions")  # Debug print
        return questions

    except Exception as e:
        print(f"Debug - Error in generate_quiz: {str(e)}")  # Debug print
        messagebox.showerror("Error", f"Could not generate quiz: {str(e)}")
        return None

def regenerate_question(topic, bloom_level, question_index, current_question, question_type="mcq", marks=10):
    """Regenerate a specific question using chatbot"""
    if not genai:
        return None

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        if question_type == "mcq":
            prompt = f"""
                Generate a new multiple-choice question on {topic} at Bloom's Taxonomy level {bloom_level}.
                Current question: {current_question}
                Generate a different question that is not similar to the current one.
                Return in JSON format:
                {{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A", "type": "mcq"}}
            """
        else:
            prompt = f"""
                Generate a new subjective question on {topic} at Bloom's Taxonomy level {bloom_level}.
                Current question: {current_question}
                Generate a different question that is not similar to the current one.
                The question should be worth {marks} marks.
                Return in JSON format:
                {{"question": "...", "answer": "Sample answer...", "type": "subjective", "marks": {marks}}}
            """

        response = model.generate_content(prompt)

        json_match = re.search(r"```json\n(.*)\n```", response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        else:
            return json.loads(response.text)
    except:
        return None

def process_chatbot_request(user_input, questions, topic, bloom_level):
    """Process chatbot requests for question modifications"""
    if not genai:
        return None

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")

        current_questions_text = "\n".join([f"Q{i+1}: {q['question']} (marks: {q.get('marks', 'N/A')})" for i, q in enumerate(questions)])

        prompt = f"""
        User request: {user_input}
        Current topic: {topic}
        Current Bloom's level: {bloom_level}
        Current questions: {current_questions_text}

        Based on the user's request, determine what action to take:
        1. If they want to change a specific question number, regenerate that question
        2. If they want to change Bloom's taxonomy level, regenerate all questions with new level
        3. If they want to change topic, regenerate all questions with new topic
        4. If they want to change marks for a question, modify that specific question's marks

        Return a JSON response with the action:
        {{"action": "regenerate_question", "question_index": 0, "marks": 15}} for single question with marks
        {{"action": "change_bloom_level", "new_level": 2}} for level change
        {{"action": "change_topic", "new_topic": "Physics"}} for topic change
        {{"action": "change_marks", "question_index": 0, "new_marks": 20}} for marks change
        {{"action": "regenerate_all"}} for regenerating all questions

        Extract question numbers from text like "question 1", "first question", etc. Convert to 0-based index.
        Extract marks from text like "15 marks", "20 points", etc.
        """

        response = model.generate_content(prompt)

        json_match = re.search(r"```json\n(.*)\n```", response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        else:
            return json.loads(response.text)
    except:
        return None

def open_quiz_chatbot(user_id, questions, topic, bloom_level):
    """Open chatbot window for quiz modifications"""
    chatbot_window = tk.Toplevel(root)
    chatbot_window.title("Quiz Assistant Chatbot")
    chatbot_window.geometry("500x600")
    chatbot_window.configure(bg="white")

    # Chat history
    chat_frame = tk.Frame(chatbot_window, bg="white")
    chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

    chat_text = tk.Text(chat_frame, bg="#f8f9fa", wrap=tk.WORD, state=tk.DISABLED)
    chat_text.pack(fill="both", expand=True)

    # Input frame
    input_frame = tk.Frame(chatbot_window, bg="white")
    input_frame.pack(fill="x", padx=10, pady=10)

    user_input = tk.Entry(input_frame, font=("Arial", 12))
    user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def add_message(sender, message):
        chat_text.config(state=tk.NORMAL)
        chat_text.insert(tk.END, f"{sender}: {message}\n\n")
        chat_text.config(state=tk.DISABLED)
        chat_text.see(tk.END)

    def send_message():
        message = user_input.get().strip()
        if not message:
            return

        add_message("You", message)
        user_input.delete(0, tk.END)

        # Process the request
        action = process_chatbot_request(message, questions, topic, bloom_level)

        if action:
            if action.get("action") == "regenerate_question":
                idx = action.get("question_index", 0)
                marks = action.get("marks", questions[idx].get('marks', 10))
                if 0 <= idx < len(questions):
                    new_q = regenerate_question(topic, bloom_level, idx, questions[idx]['question'], 
                                               questions[idx].get('type', 'mcq'), marks)
                    if new_q:
                        questions[idx] = new_q
                        add_message("Assistant", f"Question {idx+1} has been regenerated!")
                        chatbot_window.destroy()
                        display_quiz(user_id, questions, topic, bloom_level)
                    else:
                        add_message("Assistant", "Sorry, I couldn't regenerate that question.")

            elif action.get("action") == "change_marks":
                idx = action.get("question_index", 0)
                new_marks = action.get("new_marks", 10)
                if 0 <= idx < len(questions) and questions[idx].get('type') == 'subjective':
                    questions[idx]['marks'] = new_marks
                    add_message("Assistant", f"Changed question {idx+1} to {new_marks} marks!")
                    chatbot_window.destroy()
                    display_quiz(user_id, questions, topic, bloom_level)
                else:
                    add_message("Assistant", "Sorry, I can only change marks for subjective questions.")

            elif action.get("action") == "change_bloom_level":
                new_level = action.get("new_level", bloom_level)
                new_questions = generate_quiz(topic, new_level, questions[0].get('type', 'mcq'), len(questions))
                if new_questions:
                    add_message("Assistant", f"Changed to Bloom's level {new_level}!")
                    chatbot_window.destroy()
                    display_quiz(user_id, new_questions, topic, new_level)
                else:
                    add_message("Assistant", "Sorry, I couldn't change the Bloom's level.")

            elif action.get("action") == "change_topic":
                new_topic = action.get("new_topic", topic)
                new_questions = generate_quiz(new_topic, bloom_level, questions[0].get('type', 'mcq'), len(questions))
                if new_questions:
                    add_message("Assistant", f"Changed topic to {new_topic}!")
                    chatbot_window.destroy()
                    display_quiz(user_id, new_questions, new_topic, bloom_level)
                else:
                    add_message("Assistant", "Sorry, I couldn't change the topic.")

            elif action.get("action") == "regenerate_all":
                new_questions = generate_quiz(topic, bloom_level, questions[0].get('type', 'mcq'), len(questions))
                if new_questions:
                    add_message("Assistant", "All questions have been regenerated!")
                    chatbot_window.destroy()
                    display_quiz(user_id, new_questions, topic, bloom_level)
                else:
                    add_message("Assistant", "Sorry, I couldn't regenerate all questions.")
        else:
            add_message("Assistant", "I didn't understand your request. Try saying something like:\n- 'change question 1'\n- 'make question 2 worth 15 marks'\n- 'change to bloom level 3'\n- 'regenerate all questions'")

    btn_send = tk.Button(
        input_frame,
        text="Send",
        bg="#4285f4",
        fg="white",
        command=send_message
    )
    btn_send.pack(side="right")

    user_input.bind("<Return>", lambda e: send_message())

    # Initial message
    add_message("Assistant", "Hi! I can help you modify your quiz. You can ask me to:\n- Change specific questions (e.g., 'change question 2')\n- Change question marks (e.g., 'make question 1 worth 15 marks')\n- Change Bloom's taxonomy level (e.g., 'change to level 3')\n- Regenerate all questions\n- Change the topic")

def chatbot_menu(user_id):
    clear_window()
    root.configure(bg="white")

    add_back_button(root, lambda: dashboard(user_id))

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(pady=20)

    tk.Label(main_frame, text="Choose Your Learning Method", font=("Arial", 24, "bold"), fg="#4285f4", bg="white").pack(pady=10)

    topic_frame = tk.Frame(main_frame, bg="white")
    topic_frame.pack(pady=20)
    tk.Label(topic_frame, text="Enter Topic Name", fg="#666666", bg="white", font=("Arial", 14)).pack()
    entry_topic = tk.Entry(topic_frame, width=50, font=("Arial", 12))
    entry_topic.pack(pady=5)

    # Question type selection
    type_frame = tk.Frame(main_frame, bg="white")
    type_frame.pack(pady=10)
    tk.Label(type_frame, text="Question Type:", fg="#666666", bg="white", font=("Arial", 14)).pack()

    question_type = tk.StringVar(value="mcq")
    
    # Number of questions frame
    num_frame = tk.Frame(main_frame, bg="white")
    num_frame.pack(pady=10)
    
    # MCQ count frame
    mcq_frame = tk.Frame(num_frame, bg="white")
    mcq_frame.pack(pady=5)
    tk.Label(mcq_frame, text="Number of MCQ Questions:", fg="#666666", bg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=(0,10))
    mcq_count = tk.Spinbox(mcq_frame, from_=1, to=10, value=3, width=5, font=("Arial", 12))
    mcq_count.pack(side=tk.LEFT)
    
    # Subjective count frame
    subj_frame = tk.Frame(num_frame, bg="white")
    subj_frame.pack(pady=5)
    tk.Label(subj_frame, text="Number of Subjective Questions:", fg="#666666", bg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=(0,10))
    subj_count = tk.Spinbox(subj_frame, from_=1, to=10, value=2, width=5, font=("Arial", 12))
    subj_count.pack(side=tk.LEFT)

    def toggle_question_counts(q_type):
        if q_type == "mcq":
            mcq_frame.pack(pady=5)
            subj_frame.pack_forget()
        elif q_type == "subjective":
            mcq_frame.pack_forget()
            subj_frame.pack(pady=5)
        else:  # both
            mcq_frame.pack(pady=5)
            subj_frame.pack(pady=5)

    # Add radio buttons with command
    tk.Radiobutton(type_frame, text="Multiple Choice Questions (MCQ)", variable=question_type, value="mcq", 
                  bg="white", font=("Arial", 12), command=lambda: toggle_question_counts("mcq")).pack()
    tk.Radiobutton(type_frame, text="Subjective Questions", variable=question_type, value="subjective", 
                  bg="white", font=("Arial", 12), command=lambda: toggle_question_counts("subjective")).pack()
    tk.Radiobutton(type_frame, text="Both MCQ & Subjective", variable=question_type, value="both", 
                  bg="white", font=("Arial", 12), command=lambda: toggle_question_counts("both")).pack()

    # Initialize the question count frames based on default selection
    toggle_question_counts(question_type.get())

    tk.Label(main_frame, text="OR", font=("Arial", 16, "bold"), fg="#666666", bg="white").pack(pady=10)

    upload_frame = tk.Frame(main_frame, bg="white")
    upload_frame.pack(pady=20)
    tk.Label(upload_frame, text="Upload Your Document", fg="#666666", bg="white", font=("Arial", 14)).pack()

    document_path = tk.StringVar()

    def upload_file():
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Word files", "*.docx"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            document_path.set(file_path)
            entry_topic.delete(0, tk.END)  
            file_name = file_path.split("/")[-1]  
            btn_upload.config(text=f"Selected: {file_name}")

    btn_upload = tk.Button(
        upload_frame,
        text="Choose File",
        bg="#4285f4",
        fg="white",
        font=("Arial", 12),
        padx=20,
        pady=5,
        bd=0,
        command=upload_file
    )
    btn_upload.pack(pady=5)

    def start_quiz():
        try:
            topic = entry_topic.get().strip()
            doc_path = document_path.get()
            q_type = question_type.get()
            
            print(f"Debug - Question Type: {q_type}")  # Debug print
            
            if topic:
                print(f"Debug - Generating quiz for topic: {topic}")  # Debug print
                # Generate quiz from manual topic entry
                cursor.execute("SELECT MAX(bloom_level) FROM progress WHERE user_id=%s AND topic=%s", (user_id, topic))
                record = cursor.fetchone()
                bloom_level = record[0] if record and record[0] else 1
                print(f"Debug - Bloom Level: {bloom_level}")  # Debug print
                
                if q_type == "both":
                    print(f"Debug - Generating both types of questions")  # Debug print
                    # Generate both types of questions
                    mcq_num = int(mcq_count.get())
                    subj_num = int(subj_count.get())
                    print(f"Debug - MCQ Count: {mcq_num}, Subj Count: {subj_num}")  # Debug print
                    
                    mcq_questions = generate_quiz(topic, bloom_level, "mcq", mcq_num)
                    print(f"Debug - MCQ Questions Generated: {bool(mcq_questions)}")  # Debug print
                    
                    subj_questions = generate_quiz(topic, bloom_level, "subjective", subj_num)
                    print(f"Debug - Subj Questions Generated: {bool(subj_questions)}")  # Debug print
                    
                    if mcq_questions and subj_questions:
                        # Combine both types of questions
                        combined_questions = mcq_questions + subj_questions
                        print(f"Debug - Total Questions: {len(combined_questions)}")  # Debug print
                        display_quiz(user_id, combined_questions, topic, bloom_level)
                    else:
                        messagebox.showerror("Error", "Failed to generate quiz questions")
                else:
                    # Generate single type of questions
                    num_q = int(mcq_count.get()) if q_type == "mcq" else int(subj_count.get())
                    print(f"Debug - Generating {num_q} {q_type} questions")  # Debug print
                    
                    quiz_questions = generate_quiz(topic, bloom_level, q_type, num_q)
                    print(f"Debug - Questions Generated: {bool(quiz_questions)}")  # Debug print
                    
                    if quiz_questions:
                        print(f"Debug - Displaying quiz with {len(quiz_questions)} questions")  # Debug print
                        display_quiz(user_id, quiz_questions, topic, bloom_level)
                    else:
                        messagebox.showerror("Error", "Failed to generate quiz questions")
            elif doc_path:
                print(f"Debug - Processing document: {doc_path}")  # Debug print
                # Generate quiz from uploaded document
                try:
                    content = ""
                    if doc_path.lower().endswith('.pdf'):
                        with open(doc_path, 'rb') as file:
                            pdf_reader = PyPDF2.PdfReader(file)
                            for page in pdf_reader.pages:
                                content += page.extract_text()
                    else:
                        with open(doc_path, 'r', encoding='utf-8') as file:
                            content = file.read()

                    if not content.strip():
                        messagebox.showerror("Error", "Could not extract content from the document")
                        return

                    tokens = word_tokenize(content.lower())
                    stop_words = set(stopwords.words('english'))
                    meaningful_words = [word for word in tokens if word.isalnum() and word not in stop_words]

                    if not meaningful_words:
                        messagebox.showerror("Error", "Could not find meaningful content in the document")
                        return

                    from collections import Counter
                    word_freq = Counter(meaningful_words)
                    main_topic = word_freq.most_common(1)[0][0].capitalize()
                    print(f"Debug - Extracted topic: {main_topic}")  # Debug print

                    cursor.execute("SELECT MAX(bloom_level) FROM progress WHERE user_id=%s AND topic=%s", (user_id, main_topic))
                    record = cursor.fetchone()
                    bloom_level = record[0] if record and record[0] else 1
                    print(f"Debug - Bloom Level: {bloom_level}")  # Debug print

                    if q_type == "both":
                        mcq_num = int(mcq_count.get())
                        subj_num = int(subj_count.get())
                        print(f"Debug - Generating both types: MCQ={mcq_num}, Subj={subj_num}")  # Debug print
                        
                        mcq_questions = generate_quiz(main_topic, bloom_level, "mcq", mcq_num)
                        subj_questions = generate_quiz(main_topic, bloom_level, "subjective", subj_num)
                        
                        if mcq_questions and subj_questions:
                            combined_questions = mcq_questions + subj_questions
                            print(f"Debug - Total Questions: {len(combined_questions)}")  # Debug print
                            display_quiz(user_id, combined_questions, main_topic, bloom_level)
                        else:
                            messagebox.showerror("Error", "Failed to generate quiz questions")
                    else:
                        num_q = int(mcq_count.get()) if q_type == "mcq" else int(subj_count.get())
                        print(f"Debug - Generating {num_q} {q_type} questions")  # Debug print
                        
                        quiz_questions = generate_quiz(main_topic, bloom_level, q_type, num_q)
                        if quiz_questions:
                            print(f"Debug - Displaying quiz with {len(quiz_questions)} questions")  # Debug print
                            display_quiz(user_id, quiz_questions, main_topic, bloom_level)
                        else:
                            messagebox.showerror("Error", "Failed to generate quiz questions")

                except Exception as e:
                    print(f"Debug - Error processing document: {str(e)}")  # Debug print
                    messagebox.showerror("Error", f"Could not process the document: {str(e)}")
            else:
                messagebox.showerror("Error", "Please either enter a topic or upload a document")
        except Exception as e:
            print(f"Debug - Error in start_quiz: {str(e)}")  # Debug print
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    btn_submit = tk.Button(
        main_frame,
        text="Start Quiz",
        bg="#4285f4",
        fg="white",
        font=("Arial", 14, "bold"),
        padx=30,
        pady=12,
        bd=0,
        command=start_quiz
    )
    btn_submit.pack(pady=20)

def dashboard(user_id):
    clear_window()
    root.configure(bg="white")

    top_frame = tk.Frame(root, bg=GRADIENT_BG)
    top_frame.pack(fill=tk.X)

    tk.Label(
        top_frame,
        text="UniTest",
        font=("Montserrat", 24, "bold"),
        fg="white",
        bg=GRADIENT_BG
    ).pack(side=tk.LEFT, padx=20, pady=10)

    cursor.execute("SELECT username FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    username = user[0] if user else "User"

    user_frame = tk.Frame(top_frame, bg=GRADIENT_BG)
    user_frame.pack(side=tk.RIGHT, padx=20, pady=10)

    tk.Label(
        user_frame,
        text=f"Welcome, {username}!",
        font=("Segoe UI", 12),
        fg="white",
        bg=GRADIENT_BG
    ).pack(side=tk.LEFT, padx=(0,10))

    btn_logout = tk.Button(
        user_frame,
        text="Logout",
        bg="white",
        fg=GRADIENT_BG,
        font=("Segoe UI", 10),
        padx=15,
        pady=5,
        bd=0,
        command=create_home_ui
    )
    btn_logout.pack(side=tk.RIGHT)

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(pady=40, fill="both", expand=True)

    # Welcome section
    welcome_frame = tk.Frame(main_frame, bg="white")
    welcome_frame.pack(pady=20)

    tk.Label(
        welcome_frame,
        text="🎓 Ready to Learn?",
        font=("Arial", 28, "bold"),
        fg="#4285f4",
        bg="white"
    ).pack()

    tk.Label(
        welcome_frame,
        text="Start your AI-powered learning journey with personalized quizzes",
        font=("Arial", 14),
        fg="#666666",
        bg="white"
    ).pack(pady=(5,0))

    # Action buttons
    btn_frame = tk.Frame(main_frame, bg="white")
    btn_frame.pack(pady=30)

    btn_quiz = tk.Button(
        btn_frame,
        text="🚀 Start Learning",
        command=lambda: chatbot_menu(user_id),
        bg="#4285f4",
        fg="white",
        font=("Arial", 16, "bold"),
        padx=40,
        pady=15,
        bd=0,
        cursor="hand2"
    )
    btn_quiz.pack()

    # Features
    features_frame = tk.Frame(main_frame, bg="white")
    features_frame.pack(pady=20, padx=40)

    tk.Label(
        features_frame,
        text="✨ Features Available:",
        font=("Arial", 16, "bold"),
        fg="#4285f4",
        bg="white"
    ).pack()

    features = [
        "🤖 AI-Generated Questions with Chatbot Assistant",
        "📝 Both MCQ and Subjective Question Types", 
        "🎯 Bloom's Taxonomy Level Progression",
        "🔄 Regenerate Unsatisfactory Questions",
        "⚡ Instant AI Evaluation for Subjective Answers",
        "📊 Progress Tracking Across Topics"
    ]

    for feature in features:
        tk.Label(
            features_frame,
            text=feature,
            font=("Arial", 12),
            fg="#666666",
            bg="white"
        ).pack(anchor="w", pady=2)

    # Progress section
    progress_frame = tk.Frame(main_frame, bg="white")
    progress_frame.pack(pady=30, padx=40, fill="x")

    cursor.execute("SELECT topic, bloom_level FROM progress WHERE user_id=%s", (user_id,))
    records = cursor.fetchall()

    if records:
        tk.Label(
            progress_frame, 
            text="📈 Your Learning Progress", 
            font=("Arial", 18, "bold"), 
            fg="#4285f4", 
            bg="white"
        ).pack(pady=(0,10))

        for topic, bloom_level in records:
            record_frame = tk.Frame(progress_frame, bg="#f8f9fa", relief="solid", bd=1)
            record_frame.pack(fill="x", pady=5, padx=20)

            tk.Label(
                record_frame, 
                text=f"📚 {topic}", 
                fg="#333333", 
                bg="#f8f9fa", 
                font=("Arial", 12, "bold")
            ).pack(side="left", padx=15, pady=10)

            tk.Label(
                record_frame, 
                text=f"Level {bloom_level}", 
                fg="#4285f4", 
                bg="#f8f9fa", 
                font=("Arial", 12, "bold")
            ).pack(side="right", padx=15, pady=10)
    else:
        tk.Label(
            progress_frame, 
            text="🌟 Start your first quiz to track progress!", 
            fg="#666666", 
            bg="white", 
            font=("Arial", 14)
        ).pack(pady=20)

def create_home_ui():
    global user_id
    user_id = None  # Reset user_id when going to home

    root.configure(bg=MAIN_BG)

    header_frame = tk.Frame(root, bg=PRIMARY_COLOR)
    header_frame.pack(fill=tk.X)

    btn_frame = tk.Frame(header_frame, bg=PRIMARY_COLOR)
    btn_frame.pack(anchor="ne", padx=20, pady=10)

    btn_login = tk.Button(
        btn_frame,
        text="Login",
        bg=PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 12),
        bd=0,
        padx=20,
        pady=5,
        cursor="hand2",
        command=login
    )
    btn_login.pack(side=tk.RIGHT, padx=5)

    btn_signup = tk.Button(
        btn_frame,
        text="Sign Up",
        bg="white",
        fg=PRIMARY_COLOR,
        font=("Helvetica", 12),
        bd=0,
        padx=20,
        pady=5,
        cursor="hand2",
        command=signup
    )
    btn_signup.pack(side=tk.RIGHT, padx=5)

    content_frame = tk.Frame(root, bg=MAIN_BG)
    content_frame.pack(expand=True, fill="both", pady=50)

    tk.Label(
        content_frame,
        text="UniTest",
        font=("Montserrat", 40, "bold"),
        fg="#0066cc",  
        bg=MAIN_BG
    ).pack(pady=(0,10))

    tk.Label(
        content_frame,
        text="Your AI-Powered Learning Companion",
        font=("Helvetica", 18),
        fg="#0066cc",
        bg=MAIN_BG
    ).pack(pady=(0,40))

    features_frame = tk.Frame(content_frame, bg=MAIN_BG)
    features_frame.pack(pady=20, padx=40)

    features = [
        ("📚 Personalized Learning with Bloom's Taxonomy", "#6a1b9a"),  
        ("🤖 AI-Generated Smart Assessments", "#00acc1"), 
        ("📊 Progress Tracking and Analytics", "#42a5f5"),  
        ("📝 Upload Study Materials", "#00796b"),  
        ("✨ Instant Feedback System", "#3949ab")  
    ]

    for feature, color in features:
        feature_card = tk.Frame(features_frame, bg="#ffffff", bd=1, relief="solid")
        feature_card.pack(fill="x", pady=5, ipady=10)
        tk.Label(
            feature_card,
            text=feature,
            font=("Helvetica", 12),
            fg="white",  
            bg=color,
            anchor="w",
            padx=20
        ).pack(fill="x")

    btn_get_started = tk.Button(
        content_frame,
        text="Start Learning Now",
        bg=ACCENT_COLOR,
        fg="white",
        font=("Helvetica", 14, "bold"),
        padx=40,
        pady=15,
        bd=0,
        cursor="hand2",
        command=login
    )
    btn_get_started.pack(pady=40)

    def on_enter(e):
        if e.widget == btn_login:
            e.widget.config(bg=SECONDARY_COLOR)
        elif e.widget == btn_signup:
            e.widget.config(bg="#f5f6fa")
        else:  
            e.widget.config(bg="#c0392b")

    def on_leave(e):
        if e.widget == btn_login:
            e.widget.config(bg=PRIMARY_COLOR)
        elif e.widget == btn_signup:
            e.widget.config(bg="white")
        else:  
            e.widget.config(bg=ACCENT_COLOR)

    for btn in [btn_login, btn_signup, btn_get_started]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

def display_quiz(user_id, questions, topic, bloom_level):
    if not questions:
        messagebox.showerror("Error", "No questions generated")
        return

    clear_window()
    root.configure(bg="white")

    add_back_button(root, lambda: chatbot_menu(user_id))

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(pady=20, fill="both", expand=True)

    canvas = tk.Canvas(main_frame, bg="white")
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Header
    header_frame = tk.Frame(scrollable_frame, bg="white")
    header_frame.pack(fill="x", padx=20, pady=10)

    # Left side of header
    left_header = tk.Frame(header_frame, bg="white")
    left_header.pack(side="left")
    
    tk.Label(
        left_header, 
        text=f"Quiz: {topic} (Bloom's Level {bloom_level})", 
        font=("Arial", 20, "bold"), 
        fg="#4285f4", 
        bg="white"
    ).pack(side="left")

    # Right side of header (buttons)
    right_header = tk.Frame(header_frame, bg="white")
    right_header.pack(side="right")

    # Download PDF button
    btn_download = tk.Button(
        right_header,
        text="📥 Download PDF",
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10),
        padx=15,
        pady=8,
        bd=0,
        command=lambda: generate_quiz_pdf(questions, topic, bloom_level)
    )
    btn_download.pack(side="left", padx=(0, 10))

    # Chatbot button
    btn_chatbot = tk.Button(
        right_header,
        text="🤖 Quiz Assistant",
        bg="#9c27b0",
        fg="white",
        font=("Arial", 10),
        padx=15,
        pady=8,
        bd=0,
        command=lambda: open_quiz_chatbot(user_id, questions, topic, bloom_level)
    )
    btn_chatbot.pack(side="left")

    user_answers = []

    for i, q in enumerate(questions, 1):
        question_frame = tk.Frame(scrollable_frame, bg="white", relief="solid", bd=1)
        question_frame.pack(fill="x", padx=20, pady=10)

        # Question header
        q_header = tk.Frame(question_frame, bg="#f8f9fa")
        q_header.pack(fill="x")

        question_text = f"Q{i}. {q['question']}"
        tk.Label(
            q_header, 
            text=question_text, 
            fg="#333333", 
            bg="#f8f9fa", 
            font=("Arial", 12, "bold"), 
            wraplength=500,
            justify="left"
        ).pack(side="left", anchor="w", padx=15, pady=10)

        # Individual regenerate button
        def regenerate_current_question(idx=i-1, q_data=q):
            new_q = regenerate_question(topic, bloom_level, idx, q_data['question'], 
                                       q_data.get('type', 'mcq'), q_data.get('marks', 10))
            if new_q:
                questions[idx] = new_q
                display_quiz(user_id, questions, topic, bloom_level)
            else:
                messagebox.showerror("Error", "Failed to regenerate question")

        btn_regenerate = tk.Button(
            q_header,
            text="🔄",
            bg="#ff9800",
            fg="white",
            font=("Arial", 10),
            padx=8,
            pady=5,
            bd=0,
            command=regenerate_current_question
        )
        btn_regenerate.pack(side="right", padx=15, pady=5)

        # Question content
        content_frame = tk.Frame(question_frame, bg="white")
        content_frame.pack(fill="x", padx=15, pady=10)

        if q.get('type') == 'mcq':
            answer_var = tk.StringVar()
            for opt in q['options']:
                option_frame = tk.Frame(content_frame, bg="white")
                option_frame.pack(fill="x", pady=2)
                
                # Create radio button instead of checkbox
                radio = tk.Radiobutton(
                    option_frame,
                    variable=answer_var,
                    value=opt,
                    bg="white",
                    font=("Arial", 11),
                    cursor="hand2"
                )
                radio.pack(side="left", padx=(0, 5))
                
                # Create option text
                tk.Label(
                    option_frame,
                    text=opt,
                    bg="white",
                    font=("Arial", 11),
                    wraplength=600
                ).pack(side="left", fill="x", expand=True)
            user_answers.append(answer_var)
        else:  # subjective
            marks = q.get('marks', 10)
            tk.Label(
                content_frame, 
                text=f"Marks: {marks}", 
                fg="#666666", 
                bg="white", 
                font=("Arial", 10, "bold")
            ).pack(anchor="w")

            answer_text = tk.Text(content_frame, height=6, width=80, font=("Arial", 11), wrap=tk.WORD)
            answer_text.pack(pady=(5,0), fill="x")

            answer_var = AnswerHolder(answer_text)
            user_answers.append(answer_var)

    # Action buttons
    action_frame = tk.Frame(scrollable_frame, bg="white")
    action_frame.pack(pady=30)

    button_text = "Submit Answers" if any(q.get('type') == 'subjective' for q in questions) else "Submit Quiz"

    btn_submit = tk.Button(
        action_frame,
        text=button_text,
        bg="#4285f4",
        fg="white",
        font=("Arial", 14, "bold"),
        padx=30,
        pady=12,
        bd=0,
        command=lambda: submit_answers(user_id, topic, bloom_level, questions, user_answers)
    )
    btn_submit.pack(side="left", padx=10)

    btn_regenerate_all = tk.Button(
        action_frame,
        text="🔄 Regenerate All",
        bg="#ff5722",
        fg="white",
        font=("Arial", 12),
        padx=20,
        pady=12,
        bd=0,
        command=lambda: display_quiz(user_id, generate_quiz(topic, bloom_level, questions[0].get('type', 'mcq'), len(questions)), topic, bloom_level)
    )
    btn_regenerate_all.pack(side="left", padx=10)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def submit_answers(user_id, topic, bloom_level, questions, user_answers):
    # Validate and collect answers before clearing UI
    collected_answers = []

    for i, (q, ans) in enumerate(zip(questions, user_answers), 1):
        if q.get('type') == 'mcq':
            value = ans.get()
            if not value:
                messagebox.showerror("Error", f"Please answer question {i}")
                return
            collected_answers.append(value)
        elif q.get('type') == 'subjective':
            try:
                value = ans.get().strip()
            except:
                messagebox.showerror("Error", f"Error retrieving answer for question {i}")
                return
            if not value:
                messagebox.showerror("Error", f"Please answer question {i}")
                return
            collected_answers.append(value)

    # Now it's safe to call clear_window
    save_progress(user_id, topic, bloom_level, questions, collected_answers)


class AnswerHolder:
    def __init__(self, text_widget):
        self.text_widget = text_widget
    
    def get(self):
        return self.text_widget.get("1.0", tk.END).strip()

def generate_quiz_pdf(questions, topic, bloom_level):
    """Generate a PDF file containing the quiz questions"""
    try:
        # Create a file dialog to choose save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Quiz_{topic}_Level{bloom_level}.pdf"
        )
        
        if not file_path:  # User cancelled the save dialog
            return
            
        # Create the PDF document
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create styles
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
        
        # Build the content
        content = []
        
        # Add title
        content.append(Paragraph(f"Quiz: {topic}", title_style))
        content.append(Paragraph(f"Bloom's Taxonomy Level: {bloom_level}", styles['Heading2']))
        content.append(Spacer(1, 20))
        
        # Add questions
        for i, q in enumerate(questions, 1):
            # Question text
            question_text = f"Q{i}. {q['question']}"
            content.append(Paragraph(question_text, question_style))
            
            if q.get('type') == 'mcq':
                # Add options with checkboxes
                for opt in q['options']:
                    # Create a checkbox symbol (□) followed by the option
                    option_text = f"□ {opt}"
                    content.append(Paragraph(option_text, option_style))
            else:  # subjective
                content.append(Paragraph(f"Marks: {q.get('marks', 10)}", option_style))
                content.append(Paragraph("Answer: ________________________", option_style))
            
            content.append(Spacer(1, 20))
        
        # Build the PDF
        doc.build(content)
        messagebox.showinfo("Success", "Quiz PDF has been generated successfully!")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")

def create_ui():
    global root
    root = tk.Tk()
    root.title("UniTest - AI Learning Platform")
    root.geometry("900x600")
    root.state('zoomed')  # Maximize window
    icon_path = os.path.join(os.path.dirname(__file__),'logo.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    create_home_ui()
    root.mainloop()

create_ui()