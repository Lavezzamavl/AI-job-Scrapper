"""
Kazi Kenya — Job Agent API
Flask backend that serves jobs to the React frontend and triggers AI generation.

Run: python api.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3, hashlib, time, requests, logging, threading
from datetime import datetime
from bs4 import BeautifulSoup
from config import CONFIG

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

KENYA_CITIES = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika", "Malindi", "Kitale"]

ENTRY_KEYWORDS = [
    "intern", "internship", "junior", "entry level", "entry-level",
    "graduate", "trainee", "attachment", "fresh graduate"
]

TECH_KEYWORDS = [
    "software", "developer", "engineer", "backend", "frontend",
    "fullstack", "full stack", "python", "php", "laravel", "django",
    "javascript", "react", "node", "web developer", "IT", "data"
]


# ── DATABASE ──────────────────────────────────

def get_db():
    conn = sqlite3.connect("jobs.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id           TEXT PRIMARY KEY,
            title        TEXT,
            company      TEXT,
            location     TEXT,
            city         TEXT,
            source       TEXT,
            url          TEXT,
            description  TEXT,
            salary       TEXT,
            job_type     TEXT,
            found_at     TEXT,
            applied      INTEGER DEFAULT 0,
            bookmarked   INTEGER DEFAULT 0,
            cover_letter TEXT,
            email_draft  TEXT
        )
    """)
    conn.commit()
    conn.close()

def job_id(url, title, company):
    key = f"{url}{title}{company}".lower().strip()
    return hashlib.md5(key.encode()).hexdigest()[:16]

def detect_city(text):
    text_lower = text.lower()
    for city in KENYA_CITIES:
        if city.lower() in text_lower:
            return city
    return "Kenya"

def detect_job_type(title, desc=""):
    combined = f"{title} {desc}".lower()
    if any(k in combined for k in ["intern", "internship", "attachment"]):
        return "internship"
    if any(k in combined for k in ["junior", "entry", "graduate", "trainee", "fresh"]):
        return "junior"
    return "other"

def is_entry_level(title, desc=""):
    combined = f"{title} {desc}".lower()
    return any(k in combined for k in ENTRY_KEYWORDS + ["junior", "associate"])

def is_tech_role(title, desc=""):
    combined = f"{title} {desc}".lower()
    return any(k in combined for k in TECH_KEYWORDS)


# ── JOB SCRAPERS ──────────────────────────────

def scrape_myjobmag():
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    pages = [
        "https://www.myjobmag.co.ke/jobs-by-field/ict-software",
        "https://www.myjobmag.co.ke/jobs/internship-kenya",
        "https://www.myjobmag.co.ke/jobs/entry-level-kenya",
    ]
    for page_url in pages:
        try:
            r = requests.get(page_url, headers=headers, timeout=12)
            soup = BeautifulSoup(r.text, "html.parser")
            for card in soup.select(".job-list-li")[:20]:
                title_el   = card.select_one("h2 a")
                company_el = card.select_one(".company-name")
                location_el = card.select_one(".location")
                if not title_el:
                    continue
                href = title_el.get("href", "")
                if not href.startswith("http"):
                    href = "https://www.myjobmag.co.ke" + href
                title   = title_el.get_text(strip=True)
                loc_txt = location_el.get_text(strip=True) if location_el else "Kenya"
                jobs.append({
                    "title":    title,
                    "company":  company_el.get_text(strip=True) if company_el else "",
                    "location": loc_txt,
                    "city":     detect_city(loc_txt),
                    "url":      href,
                    "description": "",
                    "salary":   "",
                    "source":   "MyJobMag",
                    "job_type": detect_job_type(title),
                })
            time.sleep(1)
        except Exception as e:
            log.error(f"MyJobMag error {page_url}: {e}")
    return jobs


def scrape_brightermonday():
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    searches = [
        "https://www.brightermonday.co.ke/listings?q=software+developer&l=nairobi",
        "https://www.brightermonday.co.ke/listings?q=IT+intern&l=kenya",
        "https://www.brightermonday.co.ke/listings?q=junior+developer&l=kenya",
        "https://www.brightermonday.co.ke/listings?q=software+intern&l=kenya",
    ]
    for url in searches:
        try:
            r = requests.get(url, headers=headers, timeout=12)
            soup = BeautifulSoup(r.text, "html.parser")
            for card in soup.select("article.listingCard, div.listing-item, [data-testid='listing-card']")[:10]:
                title_el   = card.select_one("h3, h2, .listing-title, [data-testid='job-title']")
                company_el = card.select_one(".company, .listing-company, [data-testid='company-name']")
                link_el    = card.select_one("a[href]")
                location_el = card.select_one(".location, .listing-location")
                if not title_el:
                    continue
                href = link_el.get("href","") if link_el else ""
                if href and not href.startswith("http"):
                    href = "https://www.brightermonday.co.ke" + href
                title   = title_el.get_text(strip=True)
                loc_txt = location_el.get_text(strip=True) if location_el else "Kenya"
                jobs.append({
                    "title":    title,
                    "company":  company_el.get_text(strip=True) if company_el else "",
                    "location": loc_txt,
                    "city":     detect_city(loc_txt),
                    "url":      href,
                    "description": "",
                    "salary":   "",
                    "source":   "BrighterMonday",
                    "job_type": detect_job_type(title),
                })
            time.sleep(1.5)
        except Exception as e:
            log.error(f"BrighterMonday error: {e}")
    return jobs


def search_remotive():
    jobs, seen = [], set()
    for term in ["software developer", "backend developer", "python developer", "php developer"]:
        try:
            r = requests.get(f"https://remotive.com/api/remote-jobs?search={term}&limit=20", timeout=10)
            r.raise_for_status()
            for item in r.json().get("jobs", []):
                u = item.get("url","")
                if u in seen: continue
                seen.add(u)
                title = item.get("title","")
                desc  = BeautifulSoup(item.get("description",""), "html.parser").get_text()[:600]
                jobs.append({
                    "title":    title,
                    "company":  item.get("company_name",""),
                    "location": "Remote (Kenya eligible)",
                    "city":     "Remote",
                    "url":      u,
                    "description": desc,
                    "salary":   item.get("salary",""),
                    "source":   "Remotive",
                    "job_type": detect_job_type(title, desc),
                })
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Remotive error: {e}")
    return jobs


def search_jobicy():
    jobs, seen = [], set()
    for tag in ["php", "python", "javascript", "backend", "software-engineer"]:
        try:
            r = requests.get(f"https://jobicy.com/api/v2/remote-jobs?tag={tag}&count=10", timeout=10)
            r.raise_for_status()
            for item in r.json().get("jobs", []):
                u = item.get("url","")
                if u in seen: continue
                seen.add(u)
                title = item.get("jobTitle","")
                desc  = BeautifulSoup(item.get("jobDescription",""), "html.parser").get_text()[:600]
                jobs.append({
                    "title":    title,
                    "company":  item.get("companyName",""),
                    "location": "Remote",
                    "city":     "Remote",
                    "url":      u,
                    "description": desc,
                    "salary":   str(item.get("annualSalaryMin","")),
                    "source":   "Jobicy",
                    "job_type": detect_job_type(title, desc),
                })
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Jobicy error: {e}")
    return jobs


def search_arbeitnow():
    jobs, seen = [], set()
    for term in ["software-engineer", "backend-developer", "python", "php", "junior-developer"]:
        try:
            r = requests.get(f"https://www.arbeitnow.com/api/job-board-api?search={term}", timeout=10)
            r.raise_for_status()
            for item in r.json().get("data", [])[:8]:
                u = item.get("url","")
                if u in seen: continue
                seen.add(u)
                title = item.get("title","")
                desc  = item.get("description","")[:600]
                jobs.append({
                    "title":    title,
                    "company":  item.get("company_name",""),
                    "location": item.get("location","Remote"),
                    "city":     "Remote",
                    "url":      u,
                    "description": desc,
                    "salary":   "",
                    "source":   "Arbeitnow",
                    "job_type": detect_job_type(title, desc),
                })
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Arbeitnow error: {e}")
    return jobs


def run_scrape():
    log.info("Starting scrape run...")
    all_raw = []
    for fn in [scrape_myjobmag, scrape_brightermonday, search_remotive, search_jobicy, search_arbeitnow]:
        try:
            all_raw += fn()
        except Exception as e:
            log.error(f"Scraper error: {e}")

    conn = get_db()
    new_count = 0
    for job in all_raw:
        if not job.get("title") or not job.get("url"): continue
        # Filter: entry-level or tech roles only
        if not (is_entry_level(job["title"], job.get("description","")) or
                is_tech_role(job["title"], job.get("description",""))):
            continue
        jid = job_id(job["url"], job["title"], job["company"])
        exists = conn.execute("SELECT id FROM jobs WHERE id=?", (jid,)).fetchone()
        if exists: continue
        conn.execute("""
            INSERT OR IGNORE INTO jobs
            (id,title,company,location,city,source,url,description,salary,job_type,found_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (jid, job["title"], job["company"], job["location"], job["city"],
              job["source"], job["url"], job.get("description",""),
              job.get("salary",""), job.get("job_type","other"),
              datetime.now().isoformat()))
        new_count += 1
    conn.commit()
    conn.close()
    log.info(f"Scrape complete. {new_count} new jobs saved.")
    return new_count


# ── AI COVER LETTER ───────────────────────────

def generate_cover_letter(job, profile):
    api_key = CONFIG.get("GEMINI_API_KEY","")
    if not api_key or "YOUR" in api_key:
        return "Add your Gemini API key to config.py to generate cover letters.", ""

    prompt = f"""You are helping a job applicant in Kenya apply for jobs.

APPLICANT PROFILE:
{profile}

JOB DETAILS:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Description: {job.get('description','Not provided')}
Salary: {job.get('salary','Not specified')}

Generate TWO things separated by ---EMAIL---:

1. COVER LETTER (200 words max): Professional, enthusiastic, references the company by name. Highlights relevant skills from the profile. Strong call to action. No placeholders.

---EMAIL---

2. APPLICATION EMAIL: First line is "Subject: ..." then blank line then 130-word email body. Sign off with applicant's name. Ready to send as-is."""

    try:
        url  = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash:generateContent?key={api_key}")
        body = {"contents": [{"parts": [{"text": prompt}]}]}
        r    = requests.post(url, json=body, timeout=20)
        r.raise_for_status()
        text  = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        parts = text.split("---EMAIL---")
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""
    except Exception as e:
        log.error(f"Gemini error: {e}")
        return f"AI generation failed: {e}", ""


# ── API ROUTES ────────────────────────────────

@app.route("/api/jobs")
def get_jobs():
    city     = request.args.get("city","")
    job_type = request.args.get("type","")
    source   = request.args.get("source","")
    search   = request.args.get("search","").lower()
    page     = int(request.args.get("page", 1))
    per_page = 20

    conn  = get_db()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if city and city != "All":
        query += " AND city=?"; params.append(city)
    if job_type and job_type != "All":
        query += " AND job_type=?"; params.append(job_type)
    if source and source != "All":
        query += " AND source=?"; params.append(source)
    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(company) LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]

    total  = conn.execute(f"SELECT COUNT(*) FROM ({query})", params).fetchone()[0]
    query += f" ORDER BY found_at DESC LIMIT {per_page} OFFSET {(page-1)*per_page}"
    rows   = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify({
        "jobs":  [dict(r) for r in rows],
        "total": total,
        "page":  page,
        "pages": (total + per_page - 1) // per_page,
    })


@app.route("/api/jobs/<job_id>")
def get_job(job_id):
    conn = get_db()
    row  = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    conn.close()
    if not row: return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))


@app.route("/api/jobs/<job_id>/generate", methods=["POST"])
def generate(job_id):
    data    = request.json or {}
    profile = data.get("profile", CONFIG.get("MY_PROFILE",""))
    conn    = get_db()
    row     = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Job not found"}), 404
    job = dict(row)
    cover, email_draft = generate_cover_letter(job, profile)
    conn.execute("UPDATE jobs SET cover_letter=?, email_draft=? WHERE id=?",
                 (cover, email_draft, job_id))
    conn.commit()
    conn.close()
    return jsonify({"cover_letter": cover, "email_draft": email_draft})


@app.route("/api/jobs/<job_id>/apply", methods=["POST"])
def mark_applied(job_id):
    conn = get_db()
    conn.execute("UPDATE jobs SET applied=1 WHERE id=?", (job_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/jobs/<job_id>/bookmark", methods=["POST"])
def toggle_bookmark(job_id):
    conn = get_db()
    row  = conn.execute("SELECT bookmarked FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Not found"}), 404
    new_val = 0 if row["bookmarked"] else 1
    conn.execute("UPDATE jobs SET bookmarked=? WHERE id=?", (new_val, job_id))
    conn.commit()
    conn.close()
    return jsonify({"bookmarked": bool(new_val)})


@app.route("/api/scrape", methods=["POST"])
def trigger_scrape():
    def bg():
        run_scrape()
    threading.Thread(target=bg, daemon=True).start()
    return jsonify({"message": "Scrape started in background"})


@app.route("/api/stats")
def stats():
    conn    = get_db()
    total   = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    applied = conn.execute("SELECT COUNT(*) FROM jobs WHERE applied=1").fetchone()[0]
    saved   = conn.execute("SELECT COUNT(*) FROM jobs WHERE bookmarked=1").fetchone()[0]
    by_city = conn.execute("SELECT city, COUNT(*) as c FROM jobs GROUP BY city ORDER BY c DESC").fetchall()
    by_type = conn.execute("SELECT job_type, COUNT(*) as c FROM jobs GROUP BY job_type").fetchall()
    conn.close()
    return jsonify({
        "total": total, "applied": applied, "saved": saved,
        "by_city": [dict(r) for r in by_city],
        "by_type": [dict(r) for r in by_type],
    })


@app.route("/api/profile")
def get_profile():
    return jsonify({"profile": CONFIG.get("MY_PROFILE","")})


if __name__ == "__main__":
    init_db()
    log.info("Kazi Kenya API starting on http://localhost:5000")
    app.run(debug=True, port=5000)
