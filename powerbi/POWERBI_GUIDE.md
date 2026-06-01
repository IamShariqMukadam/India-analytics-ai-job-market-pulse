# Power BI Report — India Job Market Pulse
## Step-by-step guide to build the 3-page report for portfolio screenshots

---

## Step 1 — Load Data
1. Open Power BI Desktop (free download: powerbi.microsoft.com)
2. **Home → Get Data → Excel Workbook**
3. Select `powerbi/india_job_market_powerbi.xlsx`
4. Check all 6 sheets → **Load**

---

## Step 2 — Data Model (Relationships)
Go to **Model view** and create these relationships:
```
Jobs[id]          → SkillsFlat[job_id]       (1:Many)
Jobs[scrape_week] → WeeklySkills[week]        (Many:Many, both directions)
Jobs[city_normalized] → CityDemand[city]     (Many:Many)
```

---

## Step 3 — DAX Measures
In **Table view → Jobs table**, create these measures (Home → New Measure):

```dax
Total Jobs = COUNTROWS(Jobs)

Avg Salary Min LPA = AVERAGE(Jobs[salary_min_lpa])

Fresher Role % = 
DIVIDE(
    COUNTROWS(FILTER(Jobs, Jobs[is_fresher_role] = 1)),
    COUNTROWS(Jobs)
) * 100

Top Skill = 
TOPN(1, VALUES(SkillsFlat[skill]), 
    CALCULATE(COUNTROWS(SkillsFlat)), DESC)

Power BI vs Tableau Ratio = 
DIVIDE(
    CALCULATE(COUNTROWS(SkillsFlat), SkillsFlat[skill] = "power bi"),
    CALCULATE(COUNTROWS(SkillsFlat), SkillsFlat[skill] = "tableau")
)
```

---

## Step 4 — PAGE 1: Market Overview Dashboard

**Page name:** `Market Overview`
**Background color:** #F0F4FF (light blue-white)

### Visuals to add:

**A. KPI Cards (top row — 5 cards)**
- Visual: **Card**
- Card 1: Field = `[Total Jobs]` | Label = "Total Jobs Tracked"
- Card 2: Field = `[Avg Salary Min LPA]` | Label = "Avg Min Salary (LPA)"
- Card 3: Field = `[Fresher Role %]` | Label = "Fresher Eligible %"
- Card 4: Field = `[Power BI vs Tableau Ratio]` | Label = "Power BI : Tableau Ratio"
- Card 5: From WeeklySkills → Max(mention_count) | Label = "Peak Skill Demand"
- Format all cards: Bold value, #1565C0 font color, white background, subtle border

**B. Top 20 Skills Bar Chart**
- Visual: **Clustered Bar Chart** (horizontal)
- Axis (Y): `SkillsFlat[skill]`
- Values (X): `Count of SkillsFlat[skill]`
- Sort: Descending by count
- Color: Single color #2196F3
- Title: "Top 20 Skills Demanded Across India"

**C. Skill Trend Line Chart**
- Visual: **Line Chart**
- X-axis: `WeeklySkills[week]`
- Y-axis: `WeeklySkills[mention_count]`
- Legend: `WeeklySkills[skill]`
- Filter: Top 8 skills by total mention_count
- Title: "Skill Demand Trend — Weekly"

**D. Role Category Donut**
- Visual: **Donut Chart**
- Legend: `RoleDemand[role_category]`
- Values: `RoleDemand[job_count]`
- Colors: Blues palette
- Title: "Jobs by Role Category"

---

## Step 5 — PAGE 2: Geographic & Salary Analysis

**Page name:** `Geographic Intelligence`

**A. Jobs by City Bar Chart**
- Visual: **Clustered Column Chart**
- X: `CityDemand[city]`
- Y: `CityDemand[job_count]` (Sum)
- Color: Gradient blue (Format → Data colors → diverging)
- Title: "Job Volume by City"

**B. Salary by City Bar Chart**
- Visual: **Clustered Column Chart**
- X: `CityDemand[city]`
- Y: `CityDemand[avg_salary_min]` (Average)
- Color: Green gradient
- Title: "Avg Min Salary by City (LPA)"

**C. Fresher % by City**
- Visual: **Clustered Bar Chart**
- Y: `CityDemand[city]`
- X: `CityDemand[fresher_pct]` (Average)
- Add data labels
- Title: "Fresher-Eligible Roles % by City"

**D. City Intelligence Matrix Table**
- Visual: **Matrix**
- Rows: `CityDemand[city]`
- Values: Sum(job_count), Average(avg_salary_min), Average(fresher_pct)
- Format: Conditional formatting on job_count (color scale blue)
- Title: "City Intelligence Summary"

**E. Salary Distribution Histogram**
- Visual: **Column Chart** with salary buckets
- Create a calculated column in Jobs:
  ```dax
  Salary Bucket = 
  SWITCH(TRUE(),
    Jobs[salary_min_lpa] <= 3,  "0-3 LPA",
    Jobs[salary_min_lpa] <= 5,  "3-5 LPA",
    Jobs[salary_min_lpa] <= 8,  "5-8 LPA",
    Jobs[salary_min_lpa] <= 12, "8-12 LPA",
    Jobs[salary_min_lpa] <= 20, "12-20 LPA",
    "20+ LPA"
  )
  ```
- X: Salary Bucket, Y: Count of Jobs
- Title: "Salary Range Distribution"

---

## Step 6 — PAGE 3: Recruiter Intelligence

**Page name:** `Recruiter Intelligence`

**A. Top 20 Companies Hiring**
- Visual: **Clustered Bar Chart** (horizontal)
- Y: `TopCompanies[company]`
- X: `TopCompanies[total_openings]`
- Sort descending
- Color: #2196F3
- Title: "Top 20 Hiring Companies — Analytics Roles India"

**B. BI Tool Battle Chart**
- Visual: **Line Chart**
- X: `WeeklySkills[week]`
- Y: `WeeklySkills[mention_count]`
- Legend: `WeeklySkills[skill]`
- Filter visual: skill IN (power bi, tableau, looker, qlik)
- Colors: Power BI=#2196F3, Tableau=#E87722, Looker=#34A853
- Title: "Power BI vs Tableau vs Looker — Weekly Demand"

**C. Experience Distribution**
- Visual: **Clustered Column Chart**
- X: `Jobs[exp_min]` (bins 0-10)
- Y: Count of Jobs
- Title: "Jobs by Min Experience Required"

**D. Fresher vs Experienced Pie**
- Visual: **Pie Chart**
- Create calculated column:
  ```dax
  Exp Category = 
  IF(Jobs[exp_min] = 0, "Fresher (0yr)",
  IF(Jobs[exp_min] <= 2, "Junior (1-2yr)", "Mid/Senior (3+yr)"))
  ```
- Legend: Exp Category, Values: Count
- Title: "Fresher vs Experienced Split"

**E. Insight Text Boxes** (Insert → Text Box)
Add 3 text boxes with findings like:
```
💡 Power BI is 2x more demanded than Tableau in India
💡 Bangalore leads job volume; Mumbai leads salary
💡 Only 18% of roles are truly fresher-eligible
```
Format: Blue border, light background, bold insight text

---

## Step 7 — Global Formatting (Apply to all pages)

1. **View → Themes → Browse** → Create custom theme:
   - Primary: #2196F3
   - Background: #FFFFFF
   - Secondary bg: #F0F4FF
   - Text: #1A1A2E

2. **All page titles:**
   - Font: Segoe UI Semibold, 14pt, #1565C0

3. **Add logo/header text box on each page:**
   ```
   📊 India Job Market Pulse | Built by Shariq | Updated Weekly
   ```

4. **Add page navigation buttons** (Insert → Buttons → Page Navigator)

---

## Step 8 — Screenshot for README/Resume

1. Set canvas size: **View → Page View → Fit to Page**
2. Each page: **File → Export → Export to PDF** (then screenshot)
   OR use Windows Snipping Tool / Mac Screenshot
3. Save 3 screenshots:
   - `powerbi/screenshots/page1_overview.png`
   - `powerbi/screenshots/page2_geography.png`
   - `powerbi/screenshots/page3_recruiter.png`
4. Add to README.md:
   ```markdown
   ## Power BI Report
   ![Overview](powerbi/screenshots/page1_overview.png)
   ![Geography](powerbi/screenshots/page2_geography.png)
   ![Recruiter](powerbi/screenshots/page3_recruiter.png)
   ```

---

## Estimated time: 2-3 hours for all 3 pages
## Screenshot tip: Use 1920x1080 resolution for best quality