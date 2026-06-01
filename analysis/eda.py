# %% [markdown]
# # India Analytics & AI Job Market — EDA
# Run Cell 1 first, then any cell individually

# %% [markdown]
# ## Cell 1 — Imports & Setup
# %%
import os, sys, sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# Works in both .py and notebook
_base = os.getcwd()
sys.path.insert(0, os.path.join(_base, "..", "scraper"))
sys.path.insert(0, os.path.join(_base, "scraper"))  # fallback if run from root

from config import DB_PATH

CHARTS = os.path.join(_base, "charts")
os.makedirs(CHARTS, exist_ok=True)
sns.set_theme(style="whitegrid"); plt.rcParams["figure.dpi"] = 150

def conn(): return sqlite3.connect(DB_PATH)
def save(fig, name):
    fig.savefig(os.path.join(CHARTS, f"{name}.png"), bbox_inches="tight")
    plt.close(fig); print(f"  ✓ {name}.png")

print("✅ Setup ready")
print("   DB:", DB_PATH)
print("   DB exists:", os.path.exists(DB_PATH))
print("   Charts →", CHARTS)

# %% [markdown]
# ## Cell 2 — DB Check
# %%
c = conn()
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", c)["name"].tolist()
print("Tables:", tables)
if "jobs" in tables:
    print("Jobs:", pd.read_sql("SELECT COUNT(*) as n FROM jobs", c)["n"][0])
    print("Weeks:", pd.read_sql("SELECT DISTINCT scrape_week FROM jobs ORDER BY scrape_week", c)["scrape_week"].tolist())
else:
    print("❌ No jobs table. Run: cd scraper && python main.py")
c.close()

# %% [markdown]
# ## Cell 3 — Top 25 Skills
# %%
df = pd.read_sql("SELECT skill, SUM(mention_count) as total FROM weekly_skill_trends GROUP BY skill ORDER BY total DESC LIMIT 25", conn())
fig, ax = plt.subplots(figsize=(10,8))
ax.barh(df["skill"][::-1], df["total"][::-1], color=sns.color_palette("Blues_d",25))
ax.set_xlabel("Job Mentions"); ax.set_title("Top 25 Skills — India Analytics & AI Market", fontsize=14, fontweight="bold")
save(fig, "01_top_skills"); plt.show()
print(f"💡 Top 3 skills: {df.head(3)['skill'].tolist()}")

# %% [markdown]
# ## Cell 4 — Skill Demand Trend (Weekly)
# %%
c = conn()
top10 = pd.read_sql("SELECT skill FROM weekly_skill_trends GROUP BY skill ORDER BY SUM(mention_count) DESC LIMIT 10", c)["skill"].tolist()
df = pd.read_sql(f"SELECT week,skill,mention_count FROM weekly_skill_trends WHERE skill IN ({','.join(['?']*len(top10))}) ORDER BY week", c, params=top10)
c.close()
pivot = df.pivot(index="week", columns="skill", values="mention_count").fillna(0)
fig, ax = plt.subplots(figsize=(13,6))
for skill in pivot.columns:
    ax.plot(pivot.index, pivot[skill], marker="o", label=skill, linewidth=2)
ax.set_title("Top 10 Skill Demand — Week over Week", fontsize=14, fontweight="bold")
ax.legend(bbox_to_anchor=(1.01,1), loc="upper left", fontsize=8)
plt.xticks(rotation=45, ha="right"); plt.tight_layout()
save(fig, "02_skill_trends"); plt.show()
print("💡 Rising skills = add to resume now. Falling = less urgent.")

# %% [markdown]
# ## Cell 5 — City Job Count + Avg Salary
# %%
df = pd.read_sql("SELECT city, SUM(job_count) as jobs, AVG(avg_salary_min) as sal FROM weekly_city_demand GROUP BY city ORDER BY jobs DESC", conn())
fig, (ax1,ax2) = plt.subplots(1,2,figsize=(14,5))
ax1.bar(df["city"], df["jobs"], color=sns.color_palette("Blues_d",len(df)))
ax1.set_title("Job Volume by City", fontsize=13, fontweight="bold"); ax1.tick_params(axis="x",rotation=30)
ax2.bar(df["city"], df["sal"].round(1), color=sns.color_palette("Greens_d",len(df)))
ax2.set_title("Avg Min Salary by City (LPA)", fontsize=13, fontweight="bold"); ax2.tick_params(axis="x",rotation=30)
fig.suptitle("City Intelligence", fontsize=15, fontweight="bold"); plt.tight_layout()
save(fig, "03_city_demand"); plt.show()
print(f"💡 {df.iloc[0]['city'].title()} leads volume. {df.sort_values('sal',ascending=False).iloc[0]['city'].title()} leads salary.")

# %% [markdown]
# ## Cell 6 — Salary Distribution by City (Box Plot) — needs Day 2
# %%
df = pd.read_sql("SELECT city_normalized, salary_min_lpa FROM jobs WHERE salary_min_lpa > 0 AND salary_min_lpa < 40", conn())
if df.empty:
    print("⏭ Skipped — run main2.py (Day 2) first to get salary data")
else:
    fig, ax = plt.subplots(figsize=(12,6))
    order = df.groupby("city_normalized")["salary_min_lpa"].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x="city_normalized", y="salary_min_lpa", order=order,
                hue="city_normalized", palette="Blues", legend=False, ax=ax)
    ax.set_title("Salary Distribution by City (Min LPA)", fontsize=14, fontweight="bold")
    ax.set_xlabel("City"); ax.set_ylabel("Min Salary (LPA)"); ax.tick_params(axis="x",rotation=30)
    save(fig, "04_salary_boxplot"); plt.show()

# %% [markdown]
# ## Cell 7 — Experience vs Salary Scatter — needs Day 2
# %%
df = pd.read_sql("SELECT exp_min, salary_min_lpa, role_category FROM jobs WHERE exp_min IS NOT NULL AND salary_min_lpa > 0 AND salary_min_lpa < 40", conn())
if df.empty:
    print("⏭ Skipped — run main2.py (Day 2) first to get salary data")
else:
    fig, ax = plt.subplots(figsize=(10,6))
    for role, color in zip(df["role_category"].unique(), sns.color_palette("tab10", df["role_category"].nunique())):
        sub = df[df["role_category"]==role]
        ax.scatter(sub["exp_min"], sub["salary_min_lpa"], label=role, alpha=0.6, color=color, s=40)
    ax.set_xlabel("Min Experience (yrs)"); ax.set_ylabel("Min Salary (LPA)")
    ax.set_title("Experience vs Salary by Role", fontsize=14, fontweight="bold")
    ax.legend(fontsize=8); plt.tight_layout()
    save(fig, "05_exp_vs_salary"); plt.show()

# %% [markdown]
# ## Cell 8 — Experience Distribution
# %%
df = pd.read_sql("SELECT exp_min FROM jobs WHERE exp_min IS NOT NULL AND exp_min <= 12", conn())
fig, (ax1,ax2) = plt.subplots(1,2,figsize=(14,5))
ec = df["exp_min"].value_counts().sort_index()
ax1.bar(ec.index, ec.values, color=sns.color_palette("Blues_d",len(ec)))
ax1.set_title("Jobs by Min Experience Required", fontsize=13, fontweight="bold")
ax1.set_xlabel("Years"); ax1.set_ylabel("Count")
fp = round(100*(df["exp_min"]==0).sum()/len(df),1)
u3 = round(100*(df["exp_min"]<=2).sum()/len(df),1)
ax2.pie([fp, u3-fp, 100-u3], labels=["Fresher","Junior 1-2yr","Mid/Senior 3+yr"],
        autopct="%1.1f%%", colors=["#2196F3","#64B5F6","#BBDEFB"], startangle=90)
ax2.set_title("Fresher vs Experienced Split", fontsize=13, fontweight="bold")
plt.tight_layout(); save(fig, "06_experience"); plt.show()
print(f"💡 {fp}% roles fresher-eligible. {u3}% need ≤2 years.")

# %% [markdown]
# ## Cell 9 — Role Category Demand
# %%
df = pd.read_sql("SELECT role_category, SUM(job_count) as total FROM weekly_role_demand GROUP BY role_category ORDER BY total DESC", conn())
fig, ax = plt.subplots(figsize=(10,5))
ax.bar(df["role_category"], df["total"], color=sns.color_palette("Blues_d",len(df)))
ax.set_title("Job Openings by Role Category", fontsize=14, fontweight="bold")
ax.set_ylabel("Job Count"); ax.tick_params(axis="x",rotation=20)
for i,(_, row) in enumerate(df.iterrows()):
    ax.text(i, row["total"]+2, str(int(row["total"])), ha="center", fontsize=9)
plt.tight_layout(); save(fig, "07_role_demand"); plt.show()
print(f"💡 Most in-demand: {df.iloc[0]['role_category']}")

# %% [markdown]
# ## Cell 10 — Top 20 Hiring Companies
# %%
df = pd.read_sql("SELECT company, SUM(job_count) as total FROM weekly_company_demand WHERE company!='' GROUP BY company ORDER BY total DESC LIMIT 20", conn())
fig, ax = plt.subplots(figsize=(10,7))
ax.barh(df["company"][::-1], df["total"][::-1], color=sns.color_palette("Blues_d",len(df)))
ax.set_title("Top 20 Hiring Companies — India Analytics & AI", fontsize=14, fontweight="bold")
ax.set_xlabel("Total Openings"); plt.tight_layout()
save(fig, "08_top_companies"); plt.show()
print(f"💡 Top 3 companies: {df.head(3)['company'].tolist()}")

# %% [markdown]
# ## Cell 11 — Platform Breakdown
# %%
df = pd.read_sql("SELECT platform, COUNT(*) as count FROM jobs WHERE platform IS NOT NULL GROUP BY platform", conn())
if df.empty:
    print("No platform data")
else:
    fig, ax = plt.subplots(figsize=(7,5))
    ax.bar(df["platform"], df["count"], color=sns.color_palette("Blues_d",len(df)))
    ax.set_title("Jobs Scraped by Platform", fontsize=14, fontweight="bold")
    ax.set_ylabel("Job Count")
    for i,(_, row) in enumerate(df.iterrows()):
        ax.text(i, row["count"]+2, str(int(row["count"])), ha="center", fontsize=10)
    plt.tight_layout(); save(fig, "09_platform_breakdown"); plt.show()

# %% [markdown]
# ## Cell 12 — Skills Word Cloud
# %%
df = pd.read_sql("SELECT skill, SUM(mention_count) as cnt FROM weekly_skill_trends GROUP BY skill", conn())
wc = WordCloud(width=1200, height=600, background_color="white", colormap="Blues", max_font_size=120)
wc.generate_from_frequencies(dict(zip(df["skill"], df["cnt"])))
fig, ax = plt.subplots(figsize=(14,7))
ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
ax.set_title("Skill Demand Word Cloud — India Analytics & AI Jobs", fontsize=16, fontweight="bold")
save(fig, "10_skills_wordcloud"); plt.show()
print("💡 Screenshot this for LinkedIn + README hero image.")

# %% [markdown]
# ## Cell 13 — BI Tool Battle
# %%
df = pd.read_sql("SELECT week,skill,mention_count FROM weekly_skill_trends WHERE skill IN ('power bi','tableau','looker','qlik') ORDER BY week", conn())
if df.empty:
    print("No BI tool data yet")
else:
    pivot = df.pivot(index="week", columns="skill", values="mention_count").fillna(0)
    fig, ax = plt.subplots(figsize=(10,5))
    colors = {"power bi":"#2196F3","tableau":"#E87722","looker":"#34A853","qlik":"#009845"}
    for skill in pivot.columns:
        ax.plot(pivot.index, pivot[skill], marker="o", label=skill.title(), color=colors.get(skill,"gray"), linewidth=2.5)
    ax.set_title("BI Tool Demand: Power BI vs Tableau vs Others", fontsize=13, fontweight="bold")
    ax.legend(); plt.xticks(rotation=45, ha="right"); plt.tight_layout()
    save(fig, "11_bi_tools_trend"); plt.show()
    if "power bi" in pivot.columns and "tableau" in pivot.columns:
        ratio = round(pivot["power bi"].mean()/max(pivot["tableau"].mean(),1),1)
        print(f"💡 Power BI is {ratio}x more demanded than Tableau in India.")

# %% [markdown]
# ## Cell 14 — Summary (Key Findings)
# %%
c = conn()
total  = pd.read_sql("SELECT COUNT(*) as n FROM jobs", c)["n"][0]
top_sk = pd.read_sql("SELECT skill FROM weekly_skill_trends GROUP BY skill ORDER BY SUM(mention_count) DESC LIMIT 1", c)["skill"][0]
top_c  = pd.read_sql("SELECT city FROM weekly_city_demand GROUP BY city ORDER BY SUM(job_count) DESC LIMIT 1", c)["city"][0]
top_co = pd.read_sql("SELECT company FROM weekly_company_demand WHERE company!='' GROUP BY company ORDER BY SUM(job_count) DESC LIMIT 1", c)["company"][0]
fp     = pd.read_sql("SELECT ROUND(100.0*SUM(is_fresher_role)/COUNT(*),1) as p FROM jobs", c)["p"][0]
weeks  = pd.read_sql("SELECT COUNT(DISTINCT scrape_week) as w FROM jobs", c)["w"][0]
c.close()
print("="*50)
print("  INDIA ANALYTICS & AI JOB MARKET — FINDINGS")
print("="*50)
print(f"  Jobs tracked  : {total:,}")
print(f"  Weeks of data : {weeks}")
print(f"  Top skill     : {top_sk.upper()}")
print(f"  Top city      : {top_c.title()}")
print(f"  Top company   : {top_co}")
print(f"  Fresher roles : {fp}%")
print(f"  Charts saved  : {os.path.abspath(CHARTS)}")
print("="*50)