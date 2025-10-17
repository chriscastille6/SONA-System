#!/usr/bin/env python3
"""
Screenshot script for Conjoint Analysis Classroom Exercise
Takes screenshots of key pages for IRB application appendix
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def setup_driver():
    """Setup Chrome driver for screenshots"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1200,800")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def take_screenshots():
    """Take screenshots of key pages"""
    driver = setup_driver()
    
    try:
        # Create screenshots directory
        os.makedirs("screenshots", exist_ok=True)
        
        # Screenshot 1: Welcome page
        print("Taking screenshot 1: Welcome page...")
        driver.get("http://localhost:8080/student_survey.html")
        time.sleep(3)
        driver.save_screenshot("screenshots/01_welcome_page.png")
        print("✓ Saved 01_welcome_page.png")
        
        # Screenshot 2: Scroll down to see anonymity notice
        print("Taking screenshot 2: Full welcome with anonymity...")
        driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)
        driver.save_screenshot("screenshots/02_anonymity_notice.png")
        print("✓ Saved 02_anonymity_notice.png")
        
        # Screenshot 3: Instructor dashboard
        print("Taking screenshot 3: Instructor dashboard...")
        driver.get("http://localhost:8080/instructor_dashboard.html")
        time.sleep(3)
        driver.save_screenshot("screenshots/03_instructor_dashboard.png")
        print("✓ Saved 03_instructor_dashboard.png")
        
        # Screenshot 4: Instructor dashboard - scroll to charts section
        print("Taking screenshot 4: Instructor dashboard charts...")
        driver.execute_script("window.scrollTo(0, 800);")
        time.sleep(2)
        driver.save_screenshot("screenshots/04_instructor_dashboard_charts.png")
        print("✓ Saved 04_instructor_dashboard_charts.png")
        
        print("\n✓ Successfully captured 4 key screenshots!")
        print("\nScreenshots saved to: screenshots/")
        print("  - 01_welcome_page.png")
        print("  - 02_anonymity_notice.png")
        print("  - 03_instructor_dashboard.png")
        print("  - 04_instructor_dashboard_charts.png")
        
    except Exception as e:
        print(f"Error taking screenshots: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    take_screenshots()






