# AI Code Reviewer

An AI-powered code review tool built with Python, Streamlit, and Claude API.

## Features
- Bug detection with line numbers
- Code quality, security, performance, and best practices analysis
- AI-generated improved version of your code
- Chat with your code — ask follow-up questions
- Review history saved locally with SQLite
- Supports Python, JavaScript, Java, C++, Go, SQL, and more

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get your Gemini API key
Sign up at https://aistudio.google.com/api-keys?project=lively-iris-475417-t4.

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Use the app
- Open http://localhost:8501 in your browser
- Enter your API key in the sidebar
- Paste your code or upload a file
- Click "Review Code"

## Project structure
```
ai_code_reviewer/
├── app.py           # Main Streamlit UI
├── reviewer.py      # Claude API integration
├── utils.py         # Language detection, helpers
├── history.py       # SQLite review history
├── prompts.py       # AI prompt templates
├── requirements.txt
└── README.md
```

## How it works
1. You paste code → language is auto-detected
2. Code is sent to Claude API with a structured review prompt
3. Claude returns JSON with scores, issues, fixes, and improved code
4. Results are displayed with scores, issue cards, and diff view
5. You can chat about the review for deeper explanations
6. All reviews are saved to a local SQLite database
