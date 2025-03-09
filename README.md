# Halal Restaurants Web Scraper

A Python web scraper that extracts restaurant titles from the Halal Joints website for Central London.

## Project Overview

This project contains a script for web scraping restaurant titles from the Halal Joints website. The script `get_restaurant_titles.py` uses Playwright to handle JavaScript rendering and extract restaurant titles.

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
python -m playwright install chromium
```

## Usage

To extract restaurant titles from the Halal Joints website, run:

```bash
python get_restaurant_titles.py
```

This will:
1. Launch a headless browser
2. Navigate to the Halal Joints website for Central London
3. Extract restaurant titles using various methods
4. Save the results to `restaurant_titles.json`

## Files in this Project

- `get_restaurant_titles.py` - The main script for extracting restaurant titles
- `requirements.txt` - List of required Python packages
- `restaurant_titles.json` - Output file containing the extracted restaurant titles
- `README.md` - This documentation file

## Requirements

- Python 3.7+
- Playwright

## Notes

The website may be heavily JavaScript-dependent, which is why Playwright is used for rendering the page before extraction. If the website structure changes, the selectors in the script may need to be updated.
