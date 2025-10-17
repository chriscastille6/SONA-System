#!/usr/bin/env python3
"""
Capture screenshot of sample choice task (Options A and B)
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

def setup_driver():
    """Setup Chrome driver for screenshots"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,1100")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def capture_choice_task():
    """Capture the sample choice task"""
    driver = setup_driver()
    
    try:
        os.makedirs("screenshots", exist_ok=True)
        
        print("Loading sample choice task...")
        driver.get("http://localhost:8080/choice_task_sample.html")
        time.sleep(3)
        
        print("Capturing screenshot...")
        driver.save_screenshot("screenshots/03_choice_task_options_A_and_B.png")
        print("✓ Saved 03_choice_task_options_A_and_B.png")
        
        print("\n✓ Successfully captured choice task screenshot!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_choice_task()

