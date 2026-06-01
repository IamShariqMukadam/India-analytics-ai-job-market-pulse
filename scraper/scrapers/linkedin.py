import requests, time, random
from bs4 import BeautifulSoup
from config import MAX_JOBS_PER_SEARCH, MIN_DELAY, MAX_DELAY

HEADERS = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}

def build_url(role, start=0):
    return (f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?keywords={role.replace(' ','%20')}&location=India&f_TPR=r604800&start={start}")

def scrape_role(role):
    jobs, start = [], 0
    print(f"  [LinkedIn] {role}")
    while len(jobs) < MAX_JOBS_PER_SEARCH:
        try:
            r = requests.get(build_url(role, start), headers=HEADERS, timeout=15)
            if r.status_code == 429:
                print("    Rate limited, waiting 30s..."); time.sleep(30); continue
            if r.status_code != 200 or not r.text.strip(): break
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select("li")
            if not cards: break
            for card in cards:
                if len(jobs) >= MAX_JOBS_PER_SEARCH: break
                try:
                    title    = card.select_one("h3.base-search-card__title")
                    company  = card.select_one("h4.base-search-card__subtitle")
                    location = card.select_one("span.job-search-card__location")
                    date_tag = card.select_one("time")
                    url_tag  = card.select_one("a.base-card__full-link")
                    if not title: continue
                    jobs.append({
                        "Title"        : title.get_text(strip=True),
                        "Company"      : company.get_text(strip=True) if company else "N/A",
                        "Platform"     : "LinkedIn",
                        "Location"     : location.get_text(strip=True) if location else "N/A",
                        "Skills"       : "N/A",
                        "Salary"       : "N/A",
                        "Experience"   : "N/A",
                        "URL"          : url_tag["href"].split("?")[0] if url_tag else "N/A",
                        "Role Searched": role,
                    })
                except: continue
            print(f"    Offset {start}: {len(cards)} | Total: {len(jobs)}")
            start += 25
            time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        except Exception as e:
            print(f"    Error: {e}"); break
    return jobs

def scrape(roles):
    all_jobs = []
    for role in roles:
        jobs = scrape_role(role)
        all_jobs.extend(jobs)
        time.sleep(random.uniform(5,10))
    return all_jobs