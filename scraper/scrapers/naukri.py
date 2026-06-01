import time, random, requests
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.driver import get_driver
from utils.humanize import human_scroll
from config import MAX_JOBS_PER_SEARCH, NAUKRI_BASE

def scrape_role(role):
    jobs, page, driver = [], 1, get_driver(headless=True)
    print(f"  [Naukri] {role}")
    try:
        while len(jobs) < MAX_JOBS_PER_SEARCH:
            url = f"{NAUKRI_BASE}/{role.lower().replace(' ','-')}-jobs-{page}"
            driver.get(url)
            try:
                WebDriverWait(driver,15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,".srp-jobtuple-wrapper")))
            except:
                print(f"    Timeout page {page}"); break
            human_scroll(driver)
            soup = BeautifulSoup(driver.page_source,"html.parser")
            cards = soup.select(".srp-jobtuple-wrapper")
            if not cards: break
            for card in cards:
                if len(jobs) >= MAX_JOBS_PER_SEARCH: break
                try:
                    title   = card.select_one("a.title")
                    company = card.select_one("a.comp-name") or card.select_one(".comp-name")
                    loc     = card.select_one(".locWdth") or card.select_one("li.location")
                    salary  = card.select_one(".sal") or card.select_one("li.salary")
                    exp     = card.select_one(".expwdth") or card.select_one("li.experience")
                    skills  = card.select(".tag-li")
                    if not title: continue
                    jobs.append({
                        "Title"        : title.get_text(strip=True),
                        "Company"      : company.get_text(strip=True) if company else "N/A",
                        "Platform"     : "Naukri",
                        "Location"     : loc.get_text(strip=True) if loc else "N/A",
                        "Skills"       : ", ".join(s.get_text(strip=True) for s in skills) if skills else "N/A",
                        "Salary"       : salary.get_text(strip=True) if salary else "N/A",
                        "Experience"   : exp.get_text(strip=True) if exp else "N/A",
                        "URL"          : title["href"] if title and title.get("href") else "N/A",
                        "Role Searched": role,
                    })
                except: continue
            print(f"    Page {page}: {len(cards)} | Total: {len(jobs)}")
            page += 1
            time.sleep(random.uniform(4,8))
    finally:
        driver.quit()
    return jobs

def scrape(roles):
    all_jobs = []
    for role in roles:
        jobs = scrape_role(role)
        all_jobs.extend(jobs)
    return all_jobs