import time, random
from selenium.webdriver.common.action_chains import ActionChains

def random_sleep(lo=4, hi=8): time.sleep(random.uniform(lo, hi))

def human_scroll(driver, scrolls=3):
    for _ in range(scrolls):
        driver.execute_script(f"window.scrollBy(0, {random.randint(300,700)});")
        time.sleep(random.uniform(0.8, 1.8))