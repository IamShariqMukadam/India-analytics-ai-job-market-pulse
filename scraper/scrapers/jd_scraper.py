"""jd_scraper.py — scrapes full job descriptions from each platform URL"""
import requests, time, random, re
from bs4 import BeautifulSoup
from config import JD_MIN_DELAY, JD_MAX_DELAY

HEADERS = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language":"en-US,en;q=0.9",
}

def _linkedin(url):
    m = re.search(r'(\d{10,})', url)
    if not m: return ""
    api = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{m.group(1)}"
    try:
        r = requests.get(api, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text,"html.parser")
            desc = soup.find("div", class_="show-more-less-html__markup")
            return desc.get_text(separator=" ",strip=True) if desc else ""
    except Exception as e: print(f"      [LinkedIn JD] {e}")
    return ""

def _internshala(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=(5, 10))
        if r.status_code == 200:
            soup = BeautifulSoup(r.text,"html.parser")
            desc = (soup.select_one(".internship_details") or
                    soup.select_one(".job_details_section") or
                    soup.select_one("#about_internship"))
            return desc.get_text(separator=" ",strip=True) if desc else ""
    except Exception as e: print(f"      [Internshala JD] {e}")
    return ""

def _naukri(url, driver=None):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    own = False
    if driver is None:
        from utils.driver import get_driver
        driver = get_driver(headless=True); own=True
    try:
        driver.get(url)
        WebDriverWait(driver,15).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source,"html.parser")
        desc = (soup.select_one(".job-desc") or soup.select_one(".dang-inner-html") or
                soup.select_one(".jd-desc") or soup.select_one("[class*='description']") or
                soup.select_one("article"))
        skills = soup.select_one(".key-skill") or soup.select_one("[class*='skill']")
        exp = soup.select_one(".exp-wrap") or soup.select_one("[class*='experience']")
        text = (desc.get_text(separator=" ",strip=True) if desc else "")
        if skills: text += " " + skills.get_text(separator=" ",strip=True)
        if exp:    text += " Experience: " + exp.get_text(strip=True)
        return text[:3000]
    except Exception as e: print(f"      [Naukri JD] {e}"); return ""
    finally:
        if own: driver.quit()

def scrape_jd(url, platform, naukri_driver=None):
    if not url or url in ("N/A","nan",""): return ""
    time.sleep(random.uniform(JD_MIN_DELAY, JD_MAX_DELAY))
    p = platform.lower()
    if p == "linkedin":    return _linkedin(url)
    if p == "internshala": return _internshala(url)
    if p == "naukri":      return _naukri(url, naukri_driver)
    return ""