# UNITEST - AI-Powered Quiz Generator Platform

An intelligent quiz generation and learning platform powered by AI, featuring adaptive difficulty levels, code execution, proctoring, and comprehensive result analytics.

## 🚀 Features

### Core Features
- **AI-Powered Quiz Generation** - Generate MCQ, subjective, and coding questions automatically
- **PDF Processing** - Extract content from PDFs with OCR support for scanned documents
- **Adaptive Learning** - Bloom's taxonomy-based difficulty progression
- **Multiple Question Types**:
  - Multiple Choice (MCQ)
  - Subjective Questions with AI Evaluation
  - Coding Problems with Test Cases
  
### Teacher Features
- Create and manage quizzes with unique codes
- View detailed student results with sorting and filtering
- **Export Results** - Download as CSV or Excel (NEW)
- Allow student retakes
- Proctoring reports with violation tracking
- Extract questions from PDFs based on keywords

### Student Features
- Take AI-generated quizzes
- Join shared quizzes using codes
- **Strong Password Requirement** during signup (NEW)
- View results after 15-minute delay
- Practice with adaptive difficulty levels
- AI-powered learning content generation

### Security & Analytics
- Login history with geolocation tracking
- Password reset via email tokens
- Proctoring with fullscreen detection and violation tracking
- Admin dashboard with user and system metrics
- **Sorting Options** for results (8 different ways) (NEW)
- **Image Support** for questions (NEW)

## 🛠️ Tech Stack

- **Backend**: Flask + SQLAlchemy
- **Database**: PostgreSQL (NeonDB) / SQLite (local)
- **AI Integration**: Google Gemini + OpenRouter APIs
- **PDF Processing**: PyPDF2 + OCR.space API + Tesseract
- **Code Execution**: Piston API
- **Export**: ReportLab, openpyxl
- **Deployment**: Vercel

## 📦 Installation

### Prerequisites
- Python 3.9+
- pip

### Local Setup

```bash
# Clone repository
git clone https://github.com/yourusername/UNITEST-EXAM-UPDATE.git
cd UNITEST-EXAM-UPDATE

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Create .env file
cp .env.example .env
```

### Environment Variables

Create a `.env` file with:

```env
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database
DATABASE_URL=sqlite:///unittest.db  # Local
# DATABASE_URL=postgresql://user:password@host/dbname  # Production

# APIs
GOOGLE_AI_API_KEY=your-google-api-key
OPENROUTER_API_KEY=your-openrouter-key
OCR_SPACE_API_KEY=optional-ocr-api-key

# Server
PORT=5000
```

### Run Locally

```bash
python app.py
# Visit http://localhost:5000
```

## 🌐 Deployment to Vercel

### Prerequisites
- Vercel account
- NeonDB PostgreSQL database (free tier available)

### Steps

1. **Push to GitHub**:
```bash
git add .
git commit -m "feat: Add password strength, CSV/XLSX export, sorting, and image support"
git push origin main
```

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Select project settings

3. **Set Environment Variables** in Vercel:
   - `GOOGLE_AI_API_KEY`
   - `OPENROUTER_API_KEY`
   - `DATABASE_URL` (NeonDB PostgreSQL)
   - `SECRET_KEY`

4. **Deploy**:
```bash
vercel --prod
```

## 📚 API Documentation

### Quiz Generation
```python
POST /api/run_test_cases
{
  "code": "python code here",
  "language": "python",
  "test_cases": [
    {"input": "5", "expected_output": "120"}
  ]
}
```

### Results Export
````
Provide the fully rewritten file, incorporating the suggested code change. You must produce the complete file.
```

---

## 🙏 Acknowledgments

- **Google AI** for providing the Gemini AI API
- **Bootstrap** for the responsive UI framework
- **Font Awesome** for the beautiful icons
- **Flask** community for the excellent web framework

---

## 📞 Support

If you have any questions or need help:

- 📧 **Email**: [your-email@example.com]
- 🐛 **Issues**: [GitHub Issues](https://github.com/theakshatkhandelwal/unittest-ai-quiz/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/theakshatkhandelwal/unittest-ai-quiz/discussions)

---

<div align="center">

**Made with ❤️ by [Akshat Khandelwal](https://github.com/theakshatkhandelwal)**

⭐ **Star this repository if you found it helpful!**

</div>