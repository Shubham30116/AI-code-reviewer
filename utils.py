import re

EXTENSION_MAP = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".java": "Java", ".cpp": "C++", ".c": "C", ".cs": "C#",
    ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".swift": "Swift", ".kt": "Kotlin", ".html": "HTML",
    ".css": "CSS", ".sql": "SQL", ".sh": "Bash", ".r": "R",
}

KEYWORD_MAP = {
    "Python":     ["def ", "import ", "print(", "elif ", "self.", "lambda ", "class "],
    "JavaScript": ["const ", "let ", "var ", "function ", "=>", "console.log", "require("],
    "TypeScript": ["interface ", "type ", ": string", ": number", ": boolean", "as ", "enum "],
    "Java":       ["public class", "System.out", "void ", "import java", "extends ", "@Override"],
    "C++":        ["#include", "cout <<", "std::", "int main(", "cin >>", "namespace "],
    "C":          ["#include", "printf(", "scanf(", "int main(", "malloc(", "NULL"],
    "C#":         ["using System", "Console.Write", "namespace ", "public class", "static void"],
    "Go":         ["package main", "import (", "func ", ":= ", "fmt.Print"],
    "Rust":       ["fn main()", "let mut", "println!", "use std", "impl "],
    "SQL":        ["SELECT ", "FROM ", "WHERE ", "INSERT ", "UPDATE ", "CREATE TABLE"],
}

def detect_language(code: str, filename: str = "") -> str:
    if filename:
        for ext, lang in EXTENSION_MAP.items():
            if filename.lower().endswith(ext):
                return lang
    scores = {}
    for lang, keywords in KEYWORD_MAP.items():
        scores[lang] = sum(1 for kw in keywords if kw.lower() in code.lower())
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Unknown"

def read_uploaded_file(uploaded_file) -> tuple[str, str]:
    filename = uploaded_file.name
    try:
        content = uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception:
        content = ""
    lang = detect_language(content, filename)
    return content, lang

def add_line_numbers(code: str) -> str:
    lines = code.split("\n")
    width = len(str(len(lines)))
    return "\n".join(f"{str(i+1).rjust(width)}  {line}" for i, line in enumerate(lines))

def score_color(score: int) -> str:
    if score >= 80:
        return "#1D9E75"
    elif score >= 60:
        return "#EF9F27"
    else:
        return "#E24B4A"

def score_label(score: int) -> str:
    if score >= 80:
        return "Good"
    elif score >= 60:
        return "Needs work"
    else:
        return "Critical"

def severity_color(severity: str) -> str:
    return {"high": "#E24B4A", "medium": "#EF9F27", "low": "#378ADD"}.get(severity, "#888")

def severity_bg(severity: str) -> str:
    return {"high": "#FCEBEB", "medium": "#FAEEDA", "low": "#E6F1FB"}.get(severity, "#F1EFE8")

def count_issues(review: dict) -> dict:
    counts = {"high": 0, "medium": 0, "low": 0}
    for cat in review.get("categories", {}).values():
        for issue in cat.get("issues", []):
            sev = issue.get("severity", "low")
            counts[sev] = counts.get(sev, 0) + 1
    return counts
