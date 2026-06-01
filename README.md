# ⚡ India Analytics & AI Job Market Pulse

> **Real-time, enterprise-grade data analytics dashboard tracking Data Science, Analytics, and AI job demand across India's top tech hubs.**

🔗 **[Live Dashboard →](https://your-short-link.streamlit.app)** &nbsp;|&nbsp; Built by **Shariq Mukadam** &nbsp;|&nbsp; Data: Naukri, LinkedIn, Internshala

---

## 📸 Dashboard Screenshots

### 1. Interactive Streamlit Dashboard (Dark Glassmorphism UI)
> _Screenshot: (Replace with image of your main KPI and Skills Intel view)_

### 2. Multivariate Market Analysis
> _Screenshot: (Replace with image of your Heatmap and Box Plot)_

### 3. Power BI Report — Market Overview
![Power BI Page 1](powerbi/screenshots/page1_overview.png)

*(Additional Power BI pages: [Geographic Intelligence](powerbi/screenshots/page2_geography.png) | [Recruiter Intelligence](powerbi/screenshots/page3_recruiter.png))*

---

## 🎯 What This Tracks
| Metric | Details |
|--------|---------|
| **Skills vs. Roles (Heatmap)** | Cross-tabulated dependency matrix mapping which specific skills are required for DA vs. BA vs. DE roles. |
| **Realistic Salary Spreads** | Box plots showing the true statistical distribution of salaries (LPA) by role, filtering out extreme outliers. |
| **Geographic Matrix** | City-wise total jobs, average floor salaries, and entry-level (fresher) ingress ratios. |
| **BI Tool Battle** | Week-over-week market share velocity between Power BI, Tableau, and Looker. |
| **Platform Breakdown** | Sourcing volume metrics segmented by Naukri, LinkedIn, and Internshala. |

---

## 🔑 Key Findings (Updated Weekly)
- **SQL** appears in ~90% of all DA job postings — it remains the non-negotiable core skill.
- **Power BI** demand consistently outpaces **Tableau** by nearly 2x in the Indian market.
- Only **~18%** of posted roles are genuinely fresher-eligible (0 years experience).
- **Bangalore** leads total job volume; **Mumbai** commands the highest average starting salary.
- **AI/LLM** skills are rapidly transitioning from "nice-to-have" to baseline requirements in standard analyst roles.

---

## 🏗 Architecture Pipeline

```text
Job Portals (LinkedIn, Naukri, Internshala)
      ↓
naukri_scraper.py   [Selenium + anti-bot: UA rotation, random delays]
      ↓
cleaner.py          [Pandas — normalize cities, extract 50+ skills, parse salary]
      ↓
db_loader.py        [SQLite — jobs table + 4 weekly aggregation tables]
      ↓
      ┌──────────────────────┬──────────────────────┐
      ↓                      ↓                      ↓
  app.py                   eda.py               export_for_powerbi.py
[Streamlit Cloud]      [9 EDA charts]          [Excel → Power BI]
[Glassmorphism UI]     [analysis/charts/]      [3-page .pbix report]

Project Structure:
india-job-market-pulse/
├── .streamlit/
│   └── config.toml              # Streamlit native theme overrides (Cyan/Slate)
├── scraper/
│   ├── naukri_scraper.py        # Selenium scraper
│   ├── cleaner.py               # Data cleaning + skill extraction
│   ├── db_loader.py             # SQLite loader + aggregations
│   ├── seed_data.py             # 12-week historical seed data
│   ├── scheduler.py             # Weekly automation
│   └── run_pipeline.py          # One-click pipeline runner
├── data/
│   ├── raw/                     # Timestamped raw CSVs
│   ├── processed/               # Cleaned CSVs
│   └── job_market.db            # SQLite database
├── analysis/
│   ├── eda.py                   # 9 EDA charts + business insights
│   └── charts/                  # Saved PNG charts
├── dashboard/
│   └── app.py                   # Streamlit dashboard (Enterprise UI + Plotly)
├── powerbi/
│   ├── export_for_powerbi.py    # Exports Excel for Power BI
│   ├── india_job_market_powerbi.xlsx  # Generated Excel (6 sheets)
│   ├── POWERBI_GUIDE.md         # Step-by-step Power BI build guide
│   └── screenshots/             # Power BI report screenshots
├── deploy/
│   └── streamlit_deploy.md      # Streamlit Cloud deploy guide
└── requirements.txt

🚀 Quick Start:
git clone [https://github.com/YOUR_USERNAME/india-job-market-pulse.git](https://github.com/YOUR_USERNAME/india-job-market-pulse.git)
cd india-job-market-pulse
pip install -r requirements.txt

# 1. Seed historical data
python scraper/seed_data.py

# 2. Run live scrape (30-60 mins)
python scraper/run_pipeline.py
# (To skip scrape and use seed only: python scraper/run_pipeline.py --skip-scrape)

# 3. Launch the Interactive Dashboard
streamlit run dashboard/app.py

# 4. Generate local EDA charts
python analysis/eda.py

# 5. Export for Power BI
python powerbi/export_for_powerbi.py

💡 Technical Highlights:
Premium UI/UX Architecture: Extensive custom CSS overrides bypassing default Streamlit styling to create a modern, dark-glassmorphism aesthetic typically reserved for enterprise SaaS platforms (React/Vue).

Multivariate Analytics: Moving beyond simple aggregations to plot cross-tabulated heatmaps and outlier-resistant statistical distributions (Box Plots).

Advanced Skill Extraction: Custom Regex engine matching 50+ data-stack patterns, prioritizing complex multi-word phrases to prevent false-positive matching.

Incremental Data Design: Database safely dedupes on (job_url, scrape_date), allowing the pipeline to be re-run indefinitely without data corruption.

Built to solve my own problem: instead of guessing what skills to learn, I built a pipeline to measure the actual market.

