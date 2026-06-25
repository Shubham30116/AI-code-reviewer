CODE_REVIEW_PROMPT = """You are a senior software engineer conducting a thorough code review. Analyze the following {language} code and return a JSON response only — no markdown, no explanation outside the JSON.

Code to review:
```{language}
{code}
```

Return this exact JSON structure:
{{
  "overall_score": <integer 0-100>,
  "summary": "<2-3 sentence overall assessment>",
  "categories": {{
    "bugs": {{
      "score": <integer 0-100>,
      "issues": [
        {{"line": <int or null>, "severity": "high|medium|low", "title": "<short title>", "description": "<what's wrong>", "fix": "<how to fix it>"}}
      ]
    }},
    "code_quality": {{
      "score": <integer 0-100>,
      "issues": [
        {{"line": <int or null>, "severity": "high|medium|low", "title": "<short title>", "description": "<what's wrong>", "fix": "<how to fix it>"}}
      ]
    }},
    "security": {{
      "score": <integer 0-100>,
      "issues": [
        {{"line": <int or null>, "severity": "high|medium|low", "title": "<short title>", "description": "<what's wrong>", "fix": "<how to fix it>"}}
      ]
    }},
    "performance": {{
      "score": <integer 0-100>,
      "issues": [
        {{"line": <int or null>, "severity": "high|medium|low", "title": "<short title>", "description": "<what's wrong>", "fix": "<how to fix it>"}}
      ]
    }},
    "best_practices": {{
      "score": <integer 0-100>,
      "issues": [
        {{"line": <int or null>, "severity": "high|medium|low", "title": "<short title>", "description": "<what's wrong>", "fix": "<how to fix it>"}}
      ]
    }}
  }},
  "improved_code": "<the full improved version of the code with all fixes applied>",
  "key_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "top_priorities": ["<most important fix 1>", "<most important fix 2>", "<most important fix 3>"]
}}

Be specific, actionable, and reference actual line numbers where possible. If no issues found in a category, return an empty issues array and score of 100.
"""

CHAT_PROMPT = """You are a helpful senior software engineer. The user has just reviewed the following {language} code and received this review summary:

{review_summary}

The original code was:
```{language}
{code}
```

Now answer the user's follow-up question clearly and helpfully. Be concise and practical.

User question: {question}
"""
