"""scheduler.py — run every Monday 9am. Usage: python scheduler.py"""
import schedule, time, subprocess, os

def run():
    print("Running weekly pipeline...")
    subprocess.run(["python","main.py"], cwd=os.path.dirname(__file__))

schedule.every().monday.at("09:00").do(run)
print("Scheduler active — every Monday 9am. Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)