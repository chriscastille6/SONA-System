#!/usr/bin/env python3
"""
Dedicated script to capture a choice task showing Options A and B
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

def setup_driver():
    """Setup Chrome driver for screenshots"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,1000")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def capture_choice_task():
    """Navigate to and capture a choice task"""
    driver = setup_driver()
    
    try:
        os.makedirs("screenshots", exist_ok=True)
        
        print("Loading student survey...")
        driver.get("http://localhost:8080/student_survey.html")
        time.sleep(3)
        
        # Use JavaScript to navigate directly to a choice task
        print("Navigating to choice task using JavaScript...")
        
        # Hide welcome page, show scenario page
        driver.execute_script("""
            document.getElementById('welcomePage').classList.remove('active');
            document.getElementById('scenarioPage').classList.add('active');
        """)
        time.sleep(1)
        
        # Hide scenario page, show choice page
        driver.execute_script("""
            document.getElementById('scenarioPage').classList.remove('active');
            document.getElementById('choicePage').classList.add('active');
            // Update task counter
            document.getElementById('currentTask').textContent = '1';
            document.getElementById('totalTasks').textContent = '8';
        """)
        time.sleep(2)
        
        # Scroll to top to ensure full view
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        print("Capturing choice task screenshot...")
        driver.save_screenshot("screenshots/03_choice_task_options_A_and_B.png")
        print("✓ Saved 03_choice_task_options_A_and_B.png")
        
        # Also try to capture with a bit of scroll to show more context
        driver.execute_script("window.scrollTo(0, 100);")
        time.sleep(1)
        driver.save_screenshot("screenshots/03b_choice_task_scrolled.png")
        print("✓ Saved 03b_choice_task_scrolled.png (alternative view)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    capture_choice_task()

