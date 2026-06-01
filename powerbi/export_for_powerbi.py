"""
export_for_powerbi.py
Exports SQLite data to Excel sheets — import into Power BI Desktop.
Run: python powerbi/export_for_powerbi.py
Output: powerbi/india_job_market_powerbi.xlsx  (4 sheets)
"""
import os, sqlite3
import pandas as pd

BASE    = os.path.join(os.path.dirname(__file__), "..")
DB_PATH = os.path.join(BASE, "data", "job_market.db")
OUT     = os.path.join(os.path.dirname(__file__), "india_job_market_powerbi.xlsx")

conn = sqlite3.connect(DB_PATH)

jobs        = pd.read_sql("SELECT * FROM jobs", conn)
skills      = pd.read_sql("SELECT * FROM weekly_skill_trends ORDER BY week, mention_count DESC", conn)
city_demand = pd.read_sql("SELECT * FROM weekly_city_demand ORDER BY week", conn)
role_demand = pd.read_sql("SELECT * FROM weekly_role_demand ORDER BY week", conn)
companies   = pd.read_sql("""
    SELECT company, SUM(job_count) as total_openings
    FROM weekly_company_demand
    WHERE company != ''
    GROUP BY company ORDER BY total_openings DESC LIMIT 30
""", conn)
conn.close()

# Flatten skills for Power BI (one row per job per skill)
skill_rows = []
for _, row in jobs.iterrows():
    if pd.notna(row.get("skills_extracted")) and row["skills_extracted"]:
        for sk in row["skills_extracted"].split(","):
            sk = sk.strip()
            if sk:
                skill_rows.append({
                    "job_id"         : row.get("id"),
                    "skill"          : sk,
                    "city"           : row.get("city_normalized"),
                    "role_category"  : row.get("role_category"),
                    "scrape_week"    : row.get("scrape_week"),
                    "salary_min_lpa" : row.get("salary_min_lpa"),
                    "exp_min"        : row.get("exp_min"),
                    "is_fresher_role": row.get("is_fresher_role"),
                })
skills_flat = pd.DataFrame(skill_rows)

with pd.ExcelWriter(OUT, engine="openpyxl") as w:
    jobs.to_excel(w,         sheet_name="Jobs",          index=False)
    skills.to_excel(w,       sheet_name="WeeklySkills",  index=False)
    city_demand.to_excel(w,  sheet_name="CityDemand",    index=False)
    role_demand.to_excel(w,  sheet_name="RoleDemand",    index=False)
    companies.to_excel(w,    sheet_name="TopCompanies",  index=False)
    skills_flat.to_excel(w,  sheet_name="SkillsFlat",   index=False)

print(f"✅ Excel exported → {OUT}")
print(f"   Jobs: {len(jobs)} rows")
print(f"   Skills flat: {len(skills_flat)} rows")
print(f"   Sheets: Jobs, WeeklySkills, CityDemand, RoleDemand, TopCompanies, SkillsFlat")
print()
print("Next steps:")
print("  1. Open Power BI Desktop")
print("  2. Get Data → Excel → select india_job_market_powerbi.xlsx")
print("  3. Load all 6 sheets")
print("  4. Follow powerbi/POWERBI_GUIDE.md to build the 3-page report")