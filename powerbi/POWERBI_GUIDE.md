# Power BI Report — India Analytics and AI Job Market Pulse
## Built by Shariq Mukadam | 6,433 Jobs | 14 Weeks | LinkedIn · Naukri · Internshala

---

## Overview

This report was built entirely on **Power BI Service (web)** — no desktop app required.
Works on Linux, Mac, or any OS with a browser.

**Live report:** 4 pages + 1 executive dashboard
**Data:** 6,433 job listings scraped from LinkedIn, Naukri, and Internshala over 14 weeks
**Theme:** Dark navy (`#0D1B2A`) with blue accents (`#47B4FF`, `#2196F3`)

---

## Screenshot — Executive Dashboard

![Dashboard](powerbi/screenshots/PowerBiDashboard.png)

---

## Step 1 — Export data from SQLite

Run the export script to generate the Excel file:

```bash
pip install pandas openpyxl
python powerbi/export_for_powerbi.py
```

Output: `powerbi/india_job_market_powerbi.xlsx` — 6 sheets:

| Sheet | Contents |
|---|---|
| `Jobs` | All job listings (6,433 rows, 23 columns) |
| `WeeklySkills` | Skill mention counts per week |
| `CityDemand` | Job volume + salary by city |
| `RoleDemand` | Job count by role category |
| `TopCompanies` | Top 30 hiring companies |
| `SkillsFlat` | One row per job per skill (for bar charts) |

---

## Step 2 — Upload to Power BI Service

1. Go to [app.powerbi.com](https://app.powerbi.com) → sign in with Microsoft account
2. Click **"+ New item"** → **"Report"**
3. In Power Query → Connection settings → **"Upload file"** → select `india_job_market_powerbi.xlsx`
4. Click **Next** → all 6 tables load automatically
5. Click **"Create a report"** → name the semantic model → click **Create**

---

## Step 3 — Calculated columns (in semantic model)

Go to **Open semantic model** → select the relevant table → **New column**:

```dax
-- In WeeklySkills table: short week label for X-axis
WeekShort = RIGHT(WeeklySkills[week], 3)

-- In WeeklySkills table: numeric week for sort order
WeekNum = VALUE(MID(WeeklySkills[week], 7, 2))

-- In Jobs table: fresher vs experienced label
Exp Label = IF(Jobs[is_fresher_role] = 1, "Fresher", "Experienced")
```

Then click `WeekShort` column → **Sort by Column** → select `WeekNum`
This ensures weeks sort as W10 → W11 → W12 → W23 instead of alphabetically.

---

## Step 4 — Color theme

Apply these colors consistently across all pages:

| Role | Hex | Used for |
|---|---|---|
| Page background | `#0D1B2A` | Canvas background |
| Card/visual background | `#162D42` | All chart backgrounds |
| Primary blue | `#47B4FF` | Titles, borders, highlights |
| Chart blue | `#2196F3` | Bar/column chart fills |
| Accent cyan | `#00B4D8` | Secondary chart elements |
| Muted text | `#8BA5BE` | Axis labels, subtitles |
| White | `#FFFFFF` | KPI card numbers |

To apply page background:
- Click blank canvas → Format page (paintbrush) → **Canvas background** → enter hex

To apply visual background:
- Click visual → Format visual → **General** → **Effects** → **Visual border** → color `#47B4FF`, radius `8`

---

## Step 5 — KPI Cards (top row, all pages)

For each card:
1. Click blank canvas → select **Card** visual
2. Drag field into **Value** box → set correct aggregation
3. Format visual → **Visual** tab → **Category label** → toggle **Off**
4. Right-click field in Value box → **"Rename for this visual"** → type clean label
5. Format visual → **General** → **Effects** → **Visual border** → On → color `#47B4FF` → radius `8`

| Card | Field | Aggregation | Label |
|---|---|---|---|
| 1 | `Jobs[id]` | Count | Total Job Tracked |
| 2 | `Jobs[salary_min_lpa]` | Average | Avg Salary LPA |
| 3 | `Jobs[is_fresher_role]` | Average → format as % | Fresher Eligibility |
| 4 | `SkillsFlat[skill]` | Count | Skills Mentioned |
| 5 | `WeeklySkills[mention_count]` | Max | Peak Demand |

---

## Step 6 — Dashboard page (Executive Summary)

**Page name:** `Dashboard`

This is the hero page — all key insights in one view.

### Layout grid

```
┌─────────────────────────────────────────────────────┐
│           Title + subtitle (text box)               │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ Total    │ Avg      │ Fresher  │ Skills   │  Peak   │
│ Jobs     │ Salary   │  %       │ Mentions │ Demand  │
├──────────┴──────────┴──────────┴──────────┴─────────┤
│                                  │  Jobs by Role    │
│  Top 20 Skills (horiz bar)       │  Category        │
│                                  │  (donut)         │
│  Top 20 Companies (horiz bar)    ├──────────────────┤
│                                  │  Fresher vs Exp  │
│                                  │  (pie)           │
├────────────────┬─────────────────┼──────────────────┤
│ Skill Demand   │  Job Volume     │  City            │
│ Trend (line)   │  by City (col)  │  Intelligence    │
│                │                 │  (matrix table)  │
└────────────────┴─────────────────┴──────────────────┘
```

### Title text box

- Insert → Text box → type:
  ```
  India Analytics and AI Job Market Pulse
  ```
- Font size: `24`, color: `#47B4FF`, bold
- Subtitle below: `Built by Shariq Mukadam | 6,433 Jobs | 14 Weeks | LinkedIn | Naukri | Internshala`
- Font size: `11`, color: `#8BA5BE`

### Visuals

**Top 20 Skills — horizontal bar chart**
- Y-axis: `SkillsFlat[skill]`
- X-axis: `SkillsFlat[skill]` → Count
- Filter: Top N = 20 by Count of skill
- Sort: descending
- Title: `Top 20 Skills Demanded in Data Analytics and AI`

**Top 20 Companies — horizontal bar chart**
- Y-axis: `TopCompanies[company]`
- X-axis: `TopCompanies[total_openings]` → Sum
- Filter: Top N = 20 by total_openings
- Sort: descending
- Title: `Top 20 Hiring Companies — Analytics Roles India`

**Skill Demand Trend — line chart**
- X-axis: `WeeklySkills[WeekShort]`
- Y-axis: `WeeklySkills[mention_count]` → Sum
- Legend: `WeeklySkills[skill]`
- Filter: Top 8 skills by Sum of mention_count
- Title: `Skill Demand Trend — Weekly`

**Jobs by Role Category — donut chart**
- Legend: `RoleDemand[role_category]`
- Values: `RoleDemand[job_count]`
- Title: `Jobs by Role Category`

**Fresher vs Experienced — pie chart**
- Legend: `Jobs[Exp Label]`
- Values: `Jobs[id]` → Count
- Title: `Fresher vs Experienced`

**Job Volume by City — column chart**
- X-axis: `CityDemand[city]`
- Y-axis: `CityDemand[job_count]` → Sum
- Sort: descending
- Title: `Job Volume by City`

**City Intelligence — matrix table**
- Rows: `CityDemand[city]`
- Values: `job_count` (Sum), `avg_salary_min` (Average)
- Title: `City Intelligence`

---

## Step 7 — Export + Screenshots on Linux

**Export to PDF:**
- File → Export → Export to PDF → downloads all page

**Convert PDF to PNG (high resolution):**

```bash
# Fix ImageMagick PDF policy if needed
sudo sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml

# Convert to PNG at 200 DPI
convert -density 200 "filepath.pdf" page_%d.png

# Move to project folder
mkdir -p powerbi/screenshots
mv ~/page_*.png powerbi/screenshots/
```

**Rename files:**
```bash
mv powerbi/screenshots/page_0.png powerbi/screenshots/PowerBiDashboard.png
```

---

## Step 8 — Add to README

```markdown
## Power BI Dashboard — India Job Market Pulse

> Built on Power BI Service (web) | Dark navy theme | 4 pages

![Dashboard](powerbi/screenshots/PowerBiDashboard.png)

### Key Findings
- SQL, Python and Power BI are the top 3 demanded skills
- Bangalore leads in job volume (1,616 listings); Banglore leads in avg salary (8.61 LPA)
- Only 9.56% of roles are truly fresher-eligible
- Data Engineer dominates at 53% of all analytics roles
- Power BI demand is rising sharply vs Tableau over 14 weeks

### Pages
| Page | Focus |
|---|---|
| Dashboard | Executive summary — all insights in one view |
| Market Overview | KPIs + skills + trend + role breakdown |
| Geographic Intelligence | City-level jobs, salary, fresher % |
| Recruiter Intelligence | Companies, BI tools, experience split |
```

---

## Key insights from the data

- **SQL** is the #1 demanded skill across all cities and role types
- **Power BI** demand is growing 3x faster than Tableau over the 14-week period
- **Bangalore** has the most jobs (1,616) but **Gurgaon** has the highest avg salary (8.61 LPA)
- **Accenture, Infosys and EXL** are the top 3 hiring companies for analytics roles
- **53% of all roles** are Data Engineer — far outpacing Data Analyst (17%) and BI Developer (10%)
- Only **9.56% of listings** are genuinely accessible to freshers

---

## Tools used

| Tool | Purpose |
|---|---|
| Python (pandas, sqlite3, openpyxl) | Data extraction and Excel export |
| Power BI Service (web) | Report building and visualisation |
| DAX | Calculated columns (WeekShort, WeekNum, Exp Label) |
| ImageMagick | PDF to PNG conversion on Linux |

---

*Built in one session — approx 6 hours from raw data to polished dashboard*