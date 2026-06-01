"""
main.py — Day 1 scraper
Usage:
  python main.py              # scrape all 3 platforms
  python main.py --seed       # skip scrape, seed 12 weeks of fake data (dev mode)
  python main.py --skip-naukri  # skip Naukri (needs Brave), do Internshala + LinkedIn only
"""
import sys, os, random, time, sqlite3
import pandas as pd
from datetime import datetime, timedelta
from config import ROLES, PLATFORMS, CSV_OUTPUT, DATA_DIR, DB_PATH

os.makedirs(DATA_DIR, exist_ok=True)

def run_scraper():
    from scrapers import internshala, linkedin
    all_jobs = []
    args = sys.argv[1:]

    if "internshala" in PLATFORMS:
        print("\n[1/3] Internshala...")
        try:
            jobs = internshala.scrape(ROLES)
            all_jobs.extend(jobs)
            print(f"  ✓ {len(jobs)} jobs")
        except Exception as e: print(f"  ✗ {e}")

    if "naukri" in PLATFORMS and "--skip-naukri" not in args:
        print("\n[2/3] Naukri...")
        try:
            from scrapers import naukri
            jobs = naukri.scrape(ROLES)
            all_jobs.extend(jobs)
            print(f"  ✓ {len(jobs)} jobs")
        except Exception as e: print(f"  ✗ Naukri: {e}")
    else:
        print("\n[2/3] Naukri skipped")

    if "linkedin" in PLATFORMS:
        print("\n[3/3] LinkedIn...")
        try:
            jobs = linkedin.scrape(ROLES)
            all_jobs.extend(jobs)
            print(f"  ✓ {len(jobs)} jobs")
        except Exception as e: print(f"  ✗ {e}")

    if not all_jobs: print("No jobs collected."); return
    df = pd.DataFrame(all_jobs)
    df.to_csv(CSV_OUTPUT, index=False)
    print(f"\n✅ {len(df)} jobs → {CSV_OUTPUT}")

    import cleaner
    cleaner.run()

def seed():
    """Generate 12 weeks of realistic seed data for dev/demo"""
    from cleaner import SCHEMA
    COMPANIES = ["Accenture","TCS","Infosys","Wipro","Cognizant","Deloitte",
                 "Amazon","Flipkart","Swiggy","Razorpay","Mu Sigma","LatentView",
                 "Fractal Analytics","EXL","HDFC Bank","ICICI Bank","Zoho","Meesho"]
    CITIES    = ["bangalore","pune","hyderabad","mumbai","delhi","chennai","gurgaon","noida"]
    ROLE_CATS = ["Data Analyst","Business Analyst","Data Engineer","BI Developer"]
    SKILL_W   = {"sql":95,"excel":88,"power bi":71,"python":65,"tableau":42,
                 "pandas":40,"statistics":48,"data visualization":60,"mysql":45,
                 "postgresql":38,"azure":32,"aws":28,"machine learning":22,
                 "snowflake":15,"dbt":12,"etl":35,"business intelligence":40}

    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA); conn.commit()
    today = datetime.today()
    cur = conn.cursor(); total = 0

    for wk in range(12,0,-1):
        dt      = today - timedelta(weeks=wk)
        week    = dt.strftime("%Y-W%V")
        date    = dt.strftime("%Y-%m-%d")
        n_jobs  = int(200 + wk*5 + random.randint(-20,20))
        sk_cnt  = {}; city_d = {c:{"n":0,"f":0} for c in CITIES}; role_cnt={}; co_cnt={}

        for i in range(n_jobs):
            city = random.choice(CITIES)
            role = random.choices(ROLE_CATS, weights=[40,25,15,12])[0]
            co   = random.choice(COMPANIES)
            exp  = random.choices([0,1,2,3,5,7], weights=[15,20,25,20,12,8])[0]
            sks  = list(dict.fromkeys(random.choices(list(SKILL_W.keys()),
                        weights=list(SKILL_W.values()), k=random.randint(4,8))))
            for s in sks: sk_cnt[s] = sk_cnt.get(s,0)+1
            url  = f"https://naukri.com/seed-{week}-{city}-{i}"
            try:
                cur.execute("""INSERT OR IGNORE INTO jobs
                    (job_title,company,location,city_normalized,role_category,
                     experience,exp_min,exp_max,skills_extracted,is_fresher_role,
                     scrape_date,scrape_week,job_url,search_query,search_city,platform)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (f"{role} at {co}",co,city.title(),city,role,
                     f"{exp}-{exp+2} Yrs",exp,exp+2,", ".join(sks),1 if exp==0 else 0,
                     date,week,url,role.lower(),city,"Seed"))
                total += cur.rowcount
            except: pass
            city_d[city]["n"]+=1; city_d[city]["f"]+=(1 if exp==0 else 0)
            role_cnt[role]=role_cnt.get(role,0)+1
            co_cnt[co]=co_cnt.get(co,0)+1

        cur.executemany("INSERT OR REPLACE INTO weekly_skill_trends VALUES(?,?,?)",
            [(week,s,c) for s,c in sk_cnt.items()])
        cur.executemany("INSERT OR REPLACE INTO weekly_city_demand VALUES(?,?,?,?,?)",
            [(week,c,city_d[c]["n"],5.0,round(100*city_d[c]["f"]/max(city_d[c]["n"],1),1)) for c in CITIES])
        cur.executemany("INSERT OR REPLACE INTO weekly_role_demand VALUES(?,?,?)",
            [(week,r,c) for r,c in role_cnt.items()])
        cur.executemany("INSERT OR REPLACE INTO weekly_company_demand VALUES(?,?,?)",
            [(week,co,c) for co,c in co_cnt.items()])
        conn.commit()
        print(f"  Week {week}: {n_jobs} jobs")

    conn.close()
    print(f"\n✅ Seed done: {total} rows + 12 weeks aggregations")

if __name__ == "__main__":
    if "--seed" in sys.argv:
        seed()
    else:
        run_scraper()