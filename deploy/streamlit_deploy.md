# Deploy to Streamlit Cloud — Step by Step

## Step 1 — Push to GitHub
```bash
cd india-job-market-pulse
git init
git add .
git commit -m "India Job Market Pulse — initial release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/india-job-market-pulse.git
git push -u origin main
```

## Step 2 — Streamlit Cloud
1. Go to **share.streamlit.io** → Sign in with GitHub
2. Click **New app**
3. Repository: `YOUR_USERNAME/india-job-market-pulse`
4. Branch: `main`
5. Main file path: `dashboard/app.py`
6. Click **Deploy**

## Step 3 — Fix SQLite for Cloud
Streamlit Cloud reads from your repo. The `data/job_market.db` file must be committed.
```bash
git add data/job_market.db
git commit -m "Add seeded database"
git push
```
Every time you run a new scrape locally → commit the updated db → push → cloud auto-refreshes.

## Step 4 — Your public URL
`https://YOUR_USERNAME-india-job-market-pulse-dashboard-app-XXXXX.streamlit.app`

Shorten with: bit.ly or tinyurl → put this on your resume

## Step 5 — Add to Resume
```
India Job Market Pulse | Python · Selenium · SQLite · Streamlit · Plotly
Live dashboard tracking DA/BA/DE demand across 8 Indian cities — updated weekly
→ https://your-short-link.streamlit.app
→ https://github.com/yourusername/india-job-market-pulse
```