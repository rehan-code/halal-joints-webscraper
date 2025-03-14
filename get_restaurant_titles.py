"""
Restaurant Information Scraper

This script extracts restaurant information from the Halal Joints website for Central London.
It uses Playwright to handle JavaScript rendering and extract restaurant names, images, and addresses.
The extraction follows the structure: 
1. Find all <a> elements with href starting with '/restaurant/'
2. For each link, extract the title and image from its children using CSS selectors
3. Visit the restaurant page to extract the address

Usage:
    python get_restaurant_titles.py
"""

import asyncio
from playwright.async_api import async_playwright
import json
import os
import csv

async def scrape_restaurant_address(context, href, title):
    """
    Scrapes the address from a restaurant's page.
    
    Args:
        context: The browser context to use
        href: The href link to the restaurant page
        title: The restaurant title (for logging purposes)
        
    Returns:
        str: The restaurant address or empty string if not found
    """
    address = ""
    try:
        print(f"Visiting restaurant page: {href}")
        restaurant_url = f"https://www.halaljoints.com{href}"
        restaurant_page = await context.new_page()
        await restaurant_page.goto(restaurant_url, timeout=30000)
        
        # Wait for the address element to be visible
        try:
            await restaurant_page.wait_for_selector('#__next > div.relative.w-full.bg-white.flex.flex-col.lg\\:px-4 > article > div:nth-child(3) > div.w-full.lg\\:w-7\\/12.flex.flex-col.space-y-5.px-4 > div.w-full.flex.flex-col.space-y-1.items-start > a', timeout=10000)
            
            # Extract the address
            address_element = await restaurant_page.query_selector('#__next > div.relative.w-full.bg-white.flex.flex-col.lg\\:px-4 > article > div:nth-child(3) > div.w-full.lg\\:w-7\\/12.flex.flex-col.space-y-5.px-4 > div.w-full.flex.flex-col.space-y-1.items-start > a')
            
            if address_element:
                address = await address_element.text_content()
                address = address.strip()
                print(f"Found address: {address}")
            else:
                print(f"No address element found for {title}")
        except Exception as e:
            print(f"Error waiting for address element: {e}")
        
        # Close the restaurant page
        await restaurant_page.close()
        
    except Exception as e:
        print(f"Error visiting restaurant page: {e}")
    
    return address

async def scrape_restaurant_info():
    """
    Scrapes restaurant information (titles, images, and addresses) from the Halal Joints website for Central London.
    
    Returns:
        list: A list of dictionaries containing restaurant information (title, image, and address)
    """
    url = "https://www.halaljoints.com/neighbourhood/central-london-united-kingdom"
    restaurant_info = []
    
    async with async_playwright() as p:
        print(f"Launching browser...")
        # Launch browser with a larger viewport to ensure more content is loaded
        browser = await p.chromium.launch(headless=True)  # Use headless=True for production
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            print(f"Navigating to {url}...")
            # Use a shorter timeout and don't wait for network idle
            await page.goto(url, timeout=30000)
            
            # Wait for content to load
            print("Waiting for content to load...")
            try:
                # Wait for some key elements to be visible
                await page.wait_for_selector('a[href^="/restaurant/"]', timeout=10000)
                print("Found restaurant links, page seems loaded")
            except Exception as e:
                print(f"Timeout waiting for restaurant links: {e}")
                # Continue anyway
            
            # Take a screenshot for debugging
            await page.screenshot(path="webpage_full.png", full_page=True)
            print("Saved full page screenshot as webpage_full.png")
            
            # Get all restaurant links
            print("Finding all restaurant links...")
            restaurant_links = await page.query_selector_all('a[href^="/restaurant/"]')
            print(f"Found {len(restaurant_links)} restaurant links")
            
            # Process each link to extract restaurant information using CSS selectors
            for i, link in enumerate(restaurant_links):
                try:
                    # Get the href attribute (restaurant link)
                    href = await link.get_attribute('href')
                    print(f"Processing link {i+1}/{len(restaurant_links)}: {href}")
                    
                    # Extract restaurant title using CSS selectors
                    # Try different selectors to find the title
                    title_element = None
                    
                    # Try to find the title in article > div:nth-child(2) > p
                    title_element = await link.query_selector('article > div:nth-child(2) > p')
                    
                    if not title_element:
                        # Try to find the title in any p element within the article
                        title_element = await link.query_selector('article p')
                    
                    if title_element:
                        title_text = await title_element.text_content()
                        title = title_text.strip()
                        
                        # Extract restaurant image using CSS selectors
                        img_element = await link.query_selector('article > div:nth-child(1) > img')
                        
                        if not img_element:
                            # Try to find any img element within the article
                            img_element = await link.query_selector('article img')
                        
                        if img_element:
                            img_src = await img_element.get_attribute('src')
                            
                            # Create restaurant info dictionary
                            info = {
                                "title": title,
                                "image": img_src,
                                "link": href,
                                "address": ""  # Will be populated when visiting the restaurant page
                            }
                            
                            # Visit the restaurant page to get the address
                            info["address"] = await scrape_restaurant_address(context, href, title)
                            
                            restaurant_info.append(info)
                            print(f"Added restaurant: {title} | Image: {img_src} | Address: {info['address']}")
                        else:
                            print(f"No image found for link {i+1}")
                    else:
                        print(f"No title found for link {i+1}")
                        
                        # Debug: Print the HTML structure of the link
                        link_html = await page.evaluate('(element) => element.outerHTML', link)
                        print(f"Link HTML structure: {link_html[:200]}...")  # Print first 200 chars
                        
                except Exception as e:
                    print(f"Error processing link {i+1}: {e}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            # Close the browser
            await browser.close()
    
    # Sort by title
    restaurant_info = sorted(restaurant_info, key=lambda x: x["title"])
    print(f"Found {len(restaurant_info)} restaurants")
    
    return restaurant_info

async def main():
    """
    Main function to scrape restaurant information and save it to a CSV file.
    """
    restaurant_info = await scrape_restaurant_info()
    
    if restaurant_info:
        print(f"\nFound {len(restaurant_info)} restaurants:")
        for i, info in enumerate(restaurant_info, 1):
            print(f"{i}. {info['title']} | Address: {info['address']} | Image: {info['image']}")
        
        # Save to CSV file
        output_file = 'restaurant_info.csv'
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['title', 'address', 'image', 'link']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for restaurant in restaurant_info:
                writer.writerow(restaurant)
        
        print(f"\nRestaurant information saved to {output_file}")
        print(f"Full path: {os.path.abspath(output_file)}")
    else:
        print("\nNo restaurant information found.")
        print("The website might have a unique structure or be protected against scraping.")

if __name__ == "__main__":
    asyncio.run(main())
