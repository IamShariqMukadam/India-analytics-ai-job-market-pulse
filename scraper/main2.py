"""
main2.py — Day 2: scrapes JDs from saved jobs, runs Groq LLM extraction,
updates DB + Excel with enriched skills/experience/salary.
Usage: python main2.py
Prereq: python main.py must have run (jobs_raw.csv + DB must exist)
"""
import os, sqlite3, time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import CSV_OUTPUT, XLSX_OUTPUT, DB_PATH, CHECKPOINT_EVERY, DATA_DIR
from scrapers.jd_scraper import scrape_jd
from utils.extractor import extract
from cleaner import save_xlsx, aggregate

def load_jobs():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT id, job_title, company, platform, job_url, skills_extracted, experience FROM jobs", conn)
    conn.close()
    return df

def already_done(row):
    skills = str(row.get("skills_extracted",""))
    return skills not in ("","N/A","nan") and len(skills.split(",")) > 2

def update_db(updates):
    """Bulk update DB rows with enriched data"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for upd in updates:
        cur.execute("""UPDATE jobs SET
            skills_extracted=?, experience=?
            WHERE id=?""",
            (upd["skills"], upd["exp"], upd["id"]))
    conn.commit()
    # Re-aggregate all weeks
    weeks = cur.execute("SELECT DISTINCT scrape_week FROM jobs").fetchall()
    for (week,) in weeks:
        aggregate(conn, week)
    conn.close()

def process_row(row):
    url = str(row.get("job_url",""))
    platform = str(row.get("platform","")).lower()

    # Internshala already has skills from card — skip JD scrape
    if platform == "internshala":
        jd_text = str(row.get("skills_raw","")) + " " + str(row.get("job_title",""))
    else:
        jd_text = scrape_jd(url, platform)

    if not jd_text or len(jd_text.strip()) < 20:
        return {
            "id": row["id"],
            "skills": str(row.get("skills_extracted","N/A")),
            "nice_to_have": "N/A",
            "exp": str(row.get("experience","N/A")),
            "salary": "N/A",
        }
    ex = extract(jd_text)
    return {
        "id"         : row["id"],
        "skills"     : ", ".join(ex["required_skills"]) or str(row.get("skills_extracted","N/A")),
        "nice_to_have": ", ".join(ex["nice_to_have"]) or "N/A",
        "exp"        : ex["experience_required"] or str(row.get("experience","N/A")),
        "salary"     : ex["salary"] or "N/A",
    }

def rebuild_xlsx():
    """Rebuild Excel from DB after enrichment"""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM jobs", conn)
    conn.close()
    save_xlsx(df)

def run():
    print("="*55)
    print("  Day 2: JD Scraping + Groq LLM Extraction")
    print("="*55)

    df = load_jobs()
    todo = [(i, row) for i, (_, row) in enumerate(df.iterrows()) if not already_done(row)]
    done_count = len(df) - len(todo)
    print(f"\n  Total jobs : {len(df)}")
    print(f"  Already done: {done_count}")
    print(f"  To process  : {len(todo)}\n")

    if not todo:
        print("All jobs already enriched. Rebuilding Excel...")
        rebuild_xlsx(); return

    # Split: Internshala + LinkedIn can run concurrently
    # Naukri needs shared browser (sequential)
    naukri_todo = [(i, r) for i, r in todo if str(r.get("platform","")).lower()=="naukri"]
    other_todo  = [(i, r) for i, r in todo if str(r.get("platform","")).lower()!="naukri"]

    updates = []
    processed = 0

    # ── Internshala + LinkedIn concurrent ─────────────────────
    print(f"  Processing {len(other_todo)} LinkedIn/Internshala jobs (sequential)...")
    for i, row in other_todo:
        print(f"  [{processed+1}/{len(todo)}] {row.get('platform')} | {str(row.get('job_title',''))[:35]}")
        try:
            result = process_row(row)
            if result:
                updates.append(result)
                print(f"    Skills: {result['skills'][:60]}")
            processed += 1
        except Exception as e:
            print(f"    [!] {e}"); processed += 1

        if processed % CHECKPOINT_EVERY == 0 and updates:
            update_db(updates); updates = []
            print(f"\n  [Checkpoint] {processed} done\n")

    # ── Naukri sequential with shared browser ─────────────────
    if naukri_todo:
        print(f"\n  Processing {len(naukri_todo)} Naukri jobs (shared browser)...")
        try:
            from utils.driver import get_driver
            naukri_driver = get_driver(headless=True)
            from scrapers.jd_scraper import _naukri
            for i, row in naukri_todo:
                print(f"  [{processed+1}/{len(todo)}] Naukri | {str(row.get('job_title',''))[:35]}")
                try:
                    jd = _naukri(str(row.get("job_url","")), naukri_driver)
                    if jd:
                        ex_data = extract(jd)
                        updates.append({
                            "id"         : row["id"],
                            "skills"     : ", ".join(ex_data["required_skills"]) or "N/A",
                            "nice_to_have": ", ".join(ex_data["nice_to_have"]) or "N/A",
                            "exp"        : ex_data["experience_required"] or "N/A",
                            "salary"     : ex_data["salary"] or "N/A",
                        })
                except Exception as e: print(f"    [!] {e}")
                processed += 1
                if processed % CHECKPOINT_EVERY == 0 and updates:
                    update_db(updates); updates = []; print(f"\n  [Checkpoint] {processed}\n")
        finally:
            naukri_driver.quit()
    else:
        print("  No Naukri jobs to process (or Naukri skipped).")

    # Final save
    if updates: update_db(updates)
    rebuild_xlsx()

    print("\n"+"="*55)
    print(f"  Day 2 Complete! Processed: {processed}")
    print(f"  Excel → {XLSX_OUTPUT}")
    print("="*55)

if __name__ == "__main__":
    run()