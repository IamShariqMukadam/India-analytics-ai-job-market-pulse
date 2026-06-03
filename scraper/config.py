import os
from dotenv import load_dotenv
load_dotenv()

DATA_DIR   = os.path.join(os.path.dirname(__file__),"..","data")
DB_PATH    = os.path.join(DATA_DIR,"job_market.db")
CSV_OUTPUT = os.path.join(DATA_DIR,"jobs_raw.csv")
XLSX_OUTPUT= os.path.join(DATA_DIR,"india-job-market-pulse.xlsx")

# ROLES = [
#     "Data Analyst","Junior Data Analyst","Business Analyst",
#     "Business Intelligence Analyst","MIS Analyst","SQL Analyst",
#     "Power BI Developer","Tableau Developer","Analytics Engineer",
#     "Quality Assurance", "Operations Analyst",
# ]
ROLES = [
    "Data Analyst","Junior Data Analyst",
    "Business Analyst","Business Intelligence Analyst",
    "MIS Analyst","Reporting Analyst","Operations Analyst",
    "Data Engineer","Analytics Engineer","Quality Assurance",
    "Data Scientist","Machine Learning Engineer","AI Engineer",
    "ML Engineer","AI ML Engineer","NLP Engineer","MLOps Engineer",
    "Power BI Developer","Tableau Developer","BI Developer",
    "Product Analyst","Growth Analyst","Marketing Analyst",
]

PLATFORMS = ["internshala","naukri","linkedin"]
TARGET_LOCATIONS = [
    "Pune","Pimpri","Mumbai","Bangalore","Bengaluru",
    "Hyderabad","Delhi","Gurgaon","Noida","Chennai",
    "Remote","Work from home","Hybrid"
]
# TARGET_LOCATIONS = ["Pune", "Pimpri", "Remote", "Work from home"]
MAX_JOBS_PER_SEARCH = 50
MIN_DELAY, MAX_DELAY = 4, 8
JD_MIN_DELAY, JD_MAX_DELAY = 3, 6
CHECKPOINT_EVERY = 25
BRAVE_PATH = "/snap/bin/brave"
NAUKRI_API  = "https://www.naukri.com/jobapi/v3/search"
NAUKRI_BASE = "https://www.naukri.com"

# Groq — get free key at console.groq.com
GROQ_API_KEY  = os.getenv("GROQ_API_KEY","")
GROQ_API_KEY_2= os.getenv("GROQ_API_KEY_2","")
GROQ_API_KEY_3 = os.getenv("GROQ_API_KEY_3","")
GROQ_MODEL    = "llama-3.1-8b-instant"