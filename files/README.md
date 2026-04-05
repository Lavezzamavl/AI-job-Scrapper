# Kazi Kenya — Job Agent

A full-stack job hunting app for Kenya. React frontend + Flask API backend.
Finds entry-level, internship, and junior tech roles across Kenyan cities.

## Project structure

```
kazi_app/
  api.py           ← Flask backend (run this first)
  config.py        ← Your credentials (copy from old project)
  requirements.txt ← Python dependencies
  jobs.db          ← SQLite database (auto-created)
  frontend/
    src/
      App.jsx      ← Main React app
      JobList.jsx  ← Job cards
      JobDetail.jsx← Detail + cover letter panel
      Filters.jsx  ← Sidebar filters
      StatsBar.jsx ← Stats strip
      App.css      ← All styles
    package.json
    vite.config.js
    index.html
```

## Setup

### 1. Copy your config.py from the old project
The same config.py works — make sure GEMINI_API_KEY is set.

### 2. Install Python dependencies
```cmd
cd kazi_app
py -m pip install -r requirements.txt
```

### 3. Install Node.js (if you don't have it)
Download from: https://nodejs.org — get the LTS version.

### 4. Install React dependencies
```cmd
cd frontend
npm install
```

## Running

You need TWO terminal windows open at the same time.

**Terminal 1 — Flask API (from kazi_app folder):**
```cmd
python api.py
```
→ Runs on http://localhost:5000

**Terminal 2 — React frontend (from kazi_app/frontend folder):**
```cmd
npm run dev
```
→ Opens on http://localhost:3000

Then open http://localhost:3000 in your browser.

## Usage

1. Click **"Find New Jobs"** to scrape fresh listings
2. Use the sidebar to filter by **city, role type, or source**
3. Click any job card to open the detail panel
4. Click **"Generate Cover Letter"** — AI writes a tailored letter + email
5. Edit your profile in the "Edit my profile" section for better results
6. Copy the cover letter → paste into the application form
7. Click **"Apply now ↗"** → opens the real job listing
8. Click **"Mark Applied ✓"** to track it

## Sources

- **MyJobMag Kenya** — Nairobi and major cities, ICT + internship pages
- **BrighterMonday Kenya** — Local jobs across Kenya
- **Remotive** — Remote roles open to Kenya
- **Jobicy** — Remote tech jobs by tag
- **Arbeitnow** — International remote roles

## Cities covered

Nairobi, Mombasa, Kisumu, Nakuru, Eldoret, Thika, Malindi, Kitale + Remote
