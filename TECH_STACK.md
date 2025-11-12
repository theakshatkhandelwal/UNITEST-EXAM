# 🛠️ Tech Stack - UniTest AI Learning Platform

## Tech Stack Overview

**UniTest** is built as a modern, full-stack web application leveraging cutting-edge AI technology and robust backend infrastructure. The platform is powered by **Python 3.11+** with **Flask 3.0.0** as the core web framework, providing a lightweight yet powerful backend architecture. For data persistence, the application uses **PostgreSQL** hosted on **NeonDB** for production deployments, with **SQLite** as a fallback for local development, managed through **Flask-SQLAlchemy 3.1.1** for seamless ORM functionality. User authentication and session management are handled by **Flask-Login 0.6.3**, while **Werkzeug 3.0.1** provides secure password hashing and cryptographic utilities.

The platform's AI capabilities are driven by **Google Gemini 2.0 Flash** (via `google-generativeai 0.8.3`), which powers intelligent question generation, adaptive difficulty adjustment, and automated evaluation of subjective answers. For natural language processing tasks such as PDF text extraction and topic analysis, the application integrates **NLTK 3.8.1** for tokenization and stopword removal, along with **PyPDF2 3.0.1** for parsing and extracting content from uploaded PDF documents. Code execution for programming questions is handled through the **Piston API** (emkc.org), supporting multiple programming languages including Python, Java, C, and C++ with configurable time and memory limits.

On the frontend, **UniTest** delivers a responsive and intuitive user experience using **HTML5**, **CSS3**, and vanilla **JavaScript**, with **Bootstrap 5.3.0** providing a mobile-first, responsive design framework. The application features **Font Awesome 6.0.0** for iconography and **CodeMirror 5.65.2** as a feature-rich code editor for coding questions, complete with syntax highlighting, line numbers, and multi-language support. PDF generation for quiz exports is handled by **ReportLab 4.0.4**, enabling users to download quizzes in PDF format for offline study.

The platform is deployed on **Vercel** as a serverless application, leveraging Vercel's edge network for global performance and automatic SSL certificate provisioning. The application uses a custom domain (`unitest.in`) configured through **GoDaddy DNS**, with environment variables managed securely through Vercel's configuration system. The codebase is version-controlled on **GitHub**, enabling CI/CD workflows and automated deployments. Additional deployment options include **Railway**, and the application architecture supports horizontal scaling through serverless functions and connection pooling for database operations.

---

## Detailed Technology Breakdown

### Backend Framework
- **Python 3.11+** - Core programming language
- **Flask 3.0.0** - Lightweight web framework
- **Flask-SQLAlchemy 3.1.1** - Database ORM
- **Flask-Login 0.6.3** - User session management
- **Flask-WTF 1.2.1** - Form handling and CSRF protection
- **Werkzeug 3.0.1** - WSGI utilities and security

### Database
- **PostgreSQL** - Production database (via NeonDB)
- **SQLite** - Local development database
- **psycopg2-binary 2.9.9** - PostgreSQL adapter
- **SQLAlchemy** - Database abstraction layer

### AI & Machine Learning
- **Google Gemini 2.0 Flash** - AI model for:
  - Question generation
  - Answer evaluation
  - Content analysis
  - Adaptive difficulty adjustment
- **google-generativeai 0.8.3** - Python SDK

### Natural Language Processing
- **NLTK 3.8.1** - Natural language processing:
  - Text tokenization
  - Stopword removal
  - Text analysis
- **PyPDF2 3.0.1** - PDF document processing

### Code Execution
- **Piston API** (emkc.org) - Code execution service:
  - Multi-language support (Python, Java, C, C++)
  - Time and memory limits
  - Test case evaluation
  - Real-time code execution

### Frontend Technologies
- **HTML5** - Markup language
- **CSS3** - Styling with custom variables
- **JavaScript (ES6+)** - Client-side interactivity
- **Bootstrap 5.3.0** - Responsive UI framework
- **Font Awesome 6.0.0** - Icon library
- **CodeMirror 5.65.2** - Code editor component

### PDF Generation
- **ReportLab 4.0.4** - PDF generation library:
  - Quiz export functionality
  - Custom styling and formatting
  - Multi-page document support

### HTTP & Networking
- **Requests 2.31.0** - HTTP library for API calls
- **python-dotenv 1.0.1** - Environment variable management

### Deployment & Infrastructure
- **Vercel** - Serverless deployment platform
- **NeonDB** - PostgreSQL database hosting
- **Railway** - Alternative deployment platform
- **GitHub** - Version control and CI/CD
- **GoDaddy** - Domain registration and DNS
- **Custom Domain** - unitest.in with SSL

### Security Features
- **Werkzeug** - Password hashing (bcrypt)
- **Flask-Login** - Session management
- **CSRF Protection** - Flask-WTF
- **SSL/TLS** - Automatic certificate provisioning
- **Environment Variables** - Secure credential management

### Additional Features
- **Admin Dashboard** - User statistics and login tracking
- **Fullscreen Mode** - Secure quiz-taking experience
- **Real-time Code Execution** - Live code testing
- **PDF Export** - Quiz download functionality
- **Dark/Light Mode** - Theme switching
- **Responsive Design** - Mobile-friendly interface

---

## Architecture Highlights

- **Serverless Architecture** - Deployed on Vercel for scalability
- **RESTful API Design** - Clean API endpoints for code execution
- **Database Migrations** - Automatic schema updates
- **Connection Pooling** - Optimized database connections
- **Edge Computing** - Global CDN for fast load times
- **Auto-scaling** - Handles traffic spikes automatically

---

**Last Updated**: December 2024
**Platform URL**: https://unitest.in

