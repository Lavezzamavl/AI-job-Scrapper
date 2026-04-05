"""
config.py — Edit this file with your credentials and preferences.

GEMINI_API_KEY (free, no card):
  1. Go to https://aistudio.google.com
  2. Click "Get API key" in the top left
  3. Create a new key and paste it below

ADZUNA keys (free):
  Sign up at https://developer.adzuna.com

GMAIL_APP_PASSWORD:
  Gmail → Settings → Security → 2-Step Verification → App Passwords
  Generate one for "Mail" and paste the 16-char code below
"""

CONFIG = {

    # ── AI (free — no card needed) ───────────────────────────
    "GEMINI_API_KEY": "AIzaSyDiAfZRtLzjNZZQ169aBNV50yQseFGM02Q",

    # ── Your profile (AI uses this to write your materials) ──
    "MY_PROFILE": """
Name: Nathanael Karanja
Education: Bachelor of Science in Software Engineering , Murang'a Univeristy of Science and Technology
Experience: Backend development (PHP/Laravel, Python/Django), REST APIs, MySQL/SQLite
Projects:
  - Task Management API (Laravel, deployed on Railway with Vanilla JS frontend)
  - E-commerce store backend (Laravel vs Django comparative study)
Skills: PHP, Laravel, Python, Django, JavaScript, React, SQL, Git, REST APIs
Location: Nairobi, Kenya
Looking for: Software engineering internship or junior developer role
Strengths: Fast learner, strong API design, comparative framework knowledge
    """.strip(),

    # ── Search keywords ───────────────────────────────────────
    "SEARCH_KEYWORDS": [
        "software engineer nairobi",
        "backend developer nairobi",
        "PHP developer kenya",
        "Laravel developer nairobi",
        "Python developer kenya",
        "software engineering intern nairobi",
        "junior developer nairobi",
    ],

    # ── Adzuna (free at developer.adzuna.com) ─────────────────
    "ADZUNA_APP_ID":  "016f932d",
    "ADZUNA_APP_KEY": "1f17117f379c83f79e207dda0b356424",

    # ── Gmail (for sending your daily digest email) ───────────
    "GMAIL_USER":         "nathankarash@gmail.com",
    "GMAIL_APP_PASSWORD": "hqbz zurm icrd llfy",
    "SEND_TO_EMAIL":      "nathankarashh@gmail.com",

    # ── Schedule ──────────────────────────────────────────────
    "SCHEDULE_TIME":       "08:00",
    "MAX_AI_JOBS_PER_RUN": 10,
}
