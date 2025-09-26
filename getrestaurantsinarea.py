import requests
from bs4 import BeautifulSoup
import re
import os
from typing import List, Dict
from urllib.parse import urljoin, urlparse


def get_restaurants_in_area(area_url: str) -> None:
    """
    Extract all restaurants from a Tabelog area page by following sub-pages for each sound.
    Writes results to a text file with area name and restaurant URL per line.

    Args:
        area_url: URL of the Tabelog area sitemap page (e.g., https://tabelog.com/sitemap/tokyo/A1316-A131602/)
    """
    restaurants = []

    # Extract city and area from URL for file path
    # URL pattern: https://tabelog.com/sitemap/tokyo/A1316-A131602/
    url_parts = area_url.strip('/').split('/')
    city = url_parts[-2] if len(url_parts) >= 2 else 'unknown'
    area_code = url_parts[-1] if len(url_parts) >= 1 else 'unknown'
    
    # Get the main area page
    response = requests.get(area_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all links to sound sub-pages
    # These follow the pattern: https://tabelog.com/sitemap/tokyo/A1316-A131602/[sound]/
    area_base = area_url.rstrip('/')
    sound_links = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Check for full URLs that match the pattern
        if href.startswith(area_base + '/') and href.endswith('/'):
            # Extract the sound part (last segment before final slash)
            sound = href[len(area_base) + 1:-1]
            if len(sound) <= 2 and sound:  # Single character or 2-char katakana sounds
                sound_links.append(href)
    
    # Process each sound sub-page
    for sound_url in sound_links:
        try:
            sound_response = requests.get(sound_url)
            sound_response.raise_for_status()
            
            sound_soup = BeautifulSoup(sound_response.content, 'html.parser')
            
            # Find restaurant links matching the pattern /tokyo/A1316/A131602/[id]/
            restaurant_pattern = re.compile(r'/tokyo/A\d+/A\d+/\d+/')
            
            for link in sound_soup.find_all('a', href=True):
                href = link['href']
                if restaurant_pattern.match(href):
                    restaurant_name = link.get_text(strip=True)
                    restaurant_url = urljoin('https://tabelog.com', href)
                    
                    if restaurant_name:  # Only add if name is not empty
                        restaurants.append({
                            'name': restaurant_name,
                            'url': restaurant_url
                        })

        except requests.RequestException as e:
            print(f"Error fetching {sound_url}: {e}")
            continue

    # Write results to file
    output_dir = os.getenv('LOCAL_GOOD_SPOTS_OUTPUT_DIR', '/restaurants/')
    file_path = f"{output_dir.rstrip('/')}/{city}/{area_code}.txt"

    # Create directory structure if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write restaurants to file (restaurant name, URL)
    with open(file_path, 'w', encoding='utf-8') as f:
        for restaurant in restaurants:
            f.write(f"{restaurant['name']}\t{restaurant['url']}\n")

    print(f"Wrote {len(restaurants)} restaurants to {file_path}")


if __name__ == "__main__":
    # Test with the example URL
    test_url = "https://tabelog.com/sitemap/tokyo/A1316-A131602/"
    get_restaurants_in_area(test_url)