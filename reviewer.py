import json
import os
from google import genai
from dotenv import load_dotenv
from prompts import CODE_REVIEW_PROMPT, CHAT_PROMPT

load_dotenv()

def get_api_key(user_key: str = "") -> str:
    return user_key.strip() if user_key.strip() else os.getenv("GEMINI_API_KEY", "")

def review_code(code: str, language: str, api_key: str = "") -> dict:
    key = get_api_key(api_key)
    client = genai.Client(api_key=key)
    prompt = CODE_REVIEW_PROMPT.format(language=language, code=code)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()
    return json.loads(raw)

def chat_about_code(code: str, language: str, review: dict, question: str, api_key: str = "") -> str:
    key = get_api_key(api_key)
    client = genai.Client(api_key=key)
    summary = f"Overall score: {review.get('overall_score')}/100. Summary: {review.get('summary')}"
    prompt = CHAT_PROMPT.format(
        language=language,
        review_summary=summary,
        code=code,
        question=question
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()
