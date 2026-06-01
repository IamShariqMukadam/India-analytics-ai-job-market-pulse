"""extractor.py — Groq LLM extracts skills/exp/salary from JD text"""
import json, time, itertools, requests
from config import GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3, GROQ_MODEL

_KEYS = [k for k in [GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3] if k]
if not _KEYS: raise ValueError("No GROQ_API_KEY in .env — get free key at console.groq.com")
_cycle = itertools.cycle(_KEYS)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM   = "You are a job description parser. Respond ONLY with valid JSON, no markdown, no backticks."
PROMPT   = """Extract from this job description:
1. required_skills: list of must-have technical skills
2. nice_to_have: list of optional skills  
3. experience_required: years as string (e.g. "2-4 years", "fresher"), null if not found
4. salary: CTC mentioned as string (e.g. "15-25 LPA"), null if not found

Respond ONLY with this JSON:
{"required_skills":[],"nice_to_have":[],"experience_required":null,"salary":null}

Job Description:
"""
EMPTY = {"required_skills":[],"nice_to_have":[],"experience_required":None,"salary":None}

def extract(jd_text, retries=3):
    if not jd_text or len(jd_text.strip()) < 50: return EMPTY
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role":"system","content":SYSTEM},
            {"role":"user","content":PROMPT + jd_text[:3000]}
        ],
        "max_tokens": 400, "temperature": 0
    }
    time.sleep(1.5)
    for attempt in range(retries):
        key = next(_cycle)
        try:
            r = requests.post(GROQ_URL,
                headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"},
                json=payload, timeout=30)
            if r.status_code == 429:
                retry_after = r.headers.get("Retry-After")
                wait = int(retry_after) if retry_after else (2**attempt) * 15
                wait = max(wait, 20)  # minimum 20s wait
                print(f"      [Groq] 429 — wait {wait}s"); time.sleep(wait); continue
            if r.status_code != 200: return EMPTY
            content = r.json()["choices"][0]["message"]["content"].strip().strip("```json").strip("```").strip()
            parsed = json.loads(content)
            return {
                "required_skills": parsed.get("required_skills",[]),
                "nice_to_have":    parsed.get("nice_to_have",[]),
                "experience_required": parsed.get("experience_required"),
                "salary":          parsed.get("salary"),
            }
        except json.JSONDecodeError: time.sleep(2)
        except Exception as e: print(f"      [Groq] {e}"); time.sleep(2)
    return EMPTY