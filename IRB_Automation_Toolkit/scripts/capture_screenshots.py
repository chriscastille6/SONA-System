#!/usr/bin/env python3
"""
IRB Screenshot Automation Tool
Captures screenshots of web applications for IRB documentation

Usage:
    python3 capture_screenshots.py --config config.json
    python3 capture_screenshots.py --url http://localhost:8080 --output screenshots/
"""

import argparse
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def setup_driver(headless=True, window_size="1400,900"):
    """Setup Chrome driver for screenshots"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--window-size={window_size}")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def capture_screenshot(driver, config_item, output_dir):
    """Capture a single screenshot based on config"""
    try:
        name = config_item.get('name', 'screenshot')
        url = config_item['url']
        viewport = config_item.get('viewport', {'width': 1400, 'height': 900})
        scroll = config_item.get('scroll', 0)
        wait = config_item.get('wait_seconds', 2)
        js_before = config_item.get('javascript_before')
        
        print(f"Capturing: {name}...")
        
        # Load URL
        driver.get(url)
        time.sleep(wait)
        
        # Execute JavaScript if provided
        if js_before:
            try:
                driver.execute_script(js_before)
                time.sleep(1)
            except Exception as e:
                print(f"  Warning: JavaScript execution failed: {e}")
        
        # Scroll if needed
        if scroll > 0:
            driver.execute_script(f"window.scrollTo(0, {scroll});")
            time.sleep(1)
        
        # Capture screenshot
        output_path = os.path.join(output_dir, f"{name}.png")
        driver.save_screenshot(output_path)
        
        # Get file size
        size_kb = os.path.getsize(output_path) / 1024
        print(f"  ✓ Saved: {output_path} ({size_kb:.1f} KB)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def load_config(config_file):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description='Capture screenshots for IRB documentation')
    parser.add_argument('--config', help='Path to config JSON file')
    parser.add_argument('--url', help='Base URL (if not using config file)')
    parser.add_argument('--output', default='screenshots', help='Output directory')
    parser.add_argument('--headless', action='store_true', default=True, help='Run in headless mode')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    if args.config:
        # Load from config file
        config = load_config(args.config)
        server_url = config['server']['url']
        screenshots = config['screenshots']
        output_dir = config.get('output', {}).get('screenshot_dir', args.output)
        
        # Build full URLs
        for item in screenshots:
            if 'path' in item:
                item['url'] = server_url + item['path']
        
    else:
        # Simple mode: just capture URL
        if not args.url:
            print("Error: Must provide either --config or --url")
            return 1
        
        screenshots = [{
            'name': '01_screenshot',
            'url': args.url,
            'viewport': {'width': 1400, 'height': 900},
            'scroll': 0,
            'wait_seconds': 3
        }]
        output_dir = args.output
    
    # Setup driver
    print("Starting screenshot capture...")
    driver = setup_driver(headless=args.headless)
    
    try:
        success_count = 0
        for item in screenshots:
            if capture_screenshot(driver, item, output_dir):
                success_count += 1
        
        print(f"\n✓ Successfully captured {success_count}/{len(screenshots)} screenshots")
        print(f"  Output directory: {output_dir}")
        
    finally:
        driver.quit()
    
    return 0

if __name__ == "__main__":
    exit(main())

