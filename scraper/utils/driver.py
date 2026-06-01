import undetected_chromedriver as uc
from config import BRAVE_PATH

def get_driver(headless=False):
    opts = uc.ChromeOptions()
    opts.binary_location = BRAVE_PATH
    for arg in ["--no-sandbox","--disable-dev-shm-usage","--disable-gpu",
                "--remote-debugging-port=0","--window-size=1920,1080",
                "--disable-blink-features=AutomationControlled","--lang=en-US"]:
        opts.add_argument(arg)
    opts.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36")
    if headless: opts.add_argument("--headless=new")
    return uc.Chrome(options=opts, headless=False, use_subprocess=True, version_main=148)