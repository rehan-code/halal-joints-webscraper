"""
Restaurant Title Scraper

This script extracts restaurant titles from the Halal Joints website for Central London.
It uses Playwright to handle JavaScript rendering and extract the restaurant names.
The titles follow the structure: <a> -> <article> -> the second <div> -> <p> (title)

Usage:
    python get_restaurant_titles.py
"""

import asyncio
from playwright.async_api import async_playwright
import json
import os
import re

def clean_restaurant_name(name):
    """
    Cleans the restaurant name by removing verification information and other non-name text.
    
    Args:
        name (str): The raw restaurant name text
        
    Returns:
        str: The cleaned restaurant name
    """
    # Remove verification information (e.g., "verified a month ago")
    name = re.sub(r'verified.*', '', name)
    
    # Remove status information (e.g., "No longer Halal")
    name = re.sub(r'No longer Halal.*', '', name)
    
    # Remove any other common patterns that aren't part of the name
    name = re.sub(r'\(.*\)', '', name)  # Remove text in parentheses
    
    # Trim whitespace
    name = name.strip()
    
    return name

async def scrape_restaurant_titles():
    """
    Scrapes restaurant titles from the Halal Joints website for Central London.
    
    Returns:
        list: A list of restaurant titles
    """
    url = "https://www.halaljoints.com/neighbourhood/central-london-united-kingdom"
    restaurant_titles = []
    
    async with async_playwright() as p:
        print(f"Launching browser...")
        # Launch browser with a larger viewport to ensure more content is loaded
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            print(f"Navigating to {url}...")
            # Use a longer timeout and wait for network idle
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Wait for content to load
            print("Waiting for content to load...")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(5)  # Longer wait to ensure JS rendering completes
            
            print("Extracting restaurant titles...")
            
            # Take a screenshot for debugging
            await page.screenshot(path="webpage_full.png", full_page=True)
            print("Saved full page screenshot as webpage_full.png")
            
            # Method: Use CSS selector approach for the exact structure
            print("Using CSS selector approach to extract restaurant titles...")
            
            # CSS selector for the structure: a > article > div:nth-child(2) > p:nth-child(1)
            elements = await page.query_selector_all('a > article > div:nth-child(2) > p:nth-child(1)')
            
            if elements and len(elements) > 0:
                print(f"Found {len(elements)} elements with CSS selector")
                for element in elements:
                    text = await element.text_content()
                    text = text.strip()
                    
                    # Clean the restaurant name
                    cleaned_name = clean_restaurant_name(text)
                    
                    if cleaned_name:
                        restaurant_titles.append(cleaned_name)
                        print(f"Found restaurant: {cleaned_name}")
            else:
                print("No restaurant titles found with CSS selector.")
                print("The website might have changed its structure.")
            
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            # Close the browser
            await browser.close()
    
    # Sort
    restaurant_titles = sorted(restaurant_titles)
    print(f"Found {len(restaurant_titles)} unique restaurant titles")
    
    return restaurant_titles

async def main():
    """
    Main function to scrape restaurant titles and save them to a JSON file.
    """
    restaurant_titles = await scrape_restaurant_titles()
    
    if restaurant_titles:
        print(f"\nFound {len(restaurant_titles)} restaurant titles:")
        for i, title in enumerate(restaurant_titles, 1):
            print(f"{i}. {title}")
        
        # Save to JSON file
        output_file = 'restaurant_titles.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"restaurants": restaurant_titles}, f, indent=4)
        
        print(f"\nRestaurant titles saved to {output_file}")
        print(f"Full path: {os.path.abspath(output_file)}")
    else:
        print("\nNo restaurant titles found.")
        print("The website might have a unique structure or be protected against scraping.")

if __name__ == "__main__":
    asyncio.run(main())
