import requests, time, random
from bs4 import BeautifulSoup
from config import MAX_JOBS_PER_SEARCH, MIN_DELAY, MAX_DELAY

HEADERS = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36","Accept-Language":"en-US,en;q=0.9"}

def build_url(role, page=1):
    return f"https://internshala.com/jobs/keywords-{role.lower().replace(' ','%20')}/page-{page}/"

def scrape_role(role):
    jobs, page = [], 1
    print(f"  [Internshala] {role}")
    while len(jobs) < MAX_JOBS_PER_SEARCH:
        try:
            r = requests.get(build_url(role, page), headers=HEADERS, timeout=15)
            if r.status_code != 200: break
            soup = BeautifulSoup(r.text, "html.parser")
            cards = soup.select(".individual_internship")
            if not cards: break
            for card in cards:
                if len(jobs) >= MAX_JOBS_PER_SEARCH: break
                try:
                    title    = card.select_one(".job-internship-name") or card.select_one(".profile")
                    company  = card.select_one(".company-name")
                    location = card.select_one(".locations span") or card.select_one(".location_link")
                    salary   = card.select_one(".stipend") or card.select_one(".salary")
                    url_tag  = card.select_one("a.job-title-href") or card.select_one("a[href*='/jobs/']")
                    if not title: continue
                    jobs.append({
                        "Title"        : title.get_text(strip=True),
                        "Company"      : company.get_text(strip=True) if company else "N/A",
                        "Platform"     : "Internshala",
                        "Location"     : location.get_text(strip=True) if location else "N/A",
                        "Skills"       : "N/A",
                        "Salary"       : salary.get_text(strip=True) if salary else "N/A",
                        "Experience"   : "N/A",
                        "URL"          : "https://internshala.com" + url_tag["href"] if url_tag and url_tag.get("href") else "N/A",
                        "Role Searched": role,
                    })
                except: continue
            print(f"    Page {page}: {len(cards)} cards | Total: {len(jobs)}")
            page += 1
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