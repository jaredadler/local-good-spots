import requests
from bs4 import BeautifulSoup
import os
import csv

def get_area_urls(city):
    """
    Scrapes Tabelog sitemap for a city and writes area names, area codes, and URLs to a CSV file.

    Args:
        city (str): City name (e.g., 'tokyo')

    Returns:
        list: Array of tuples containing (area_name, area_code, url) for each area in the city
    """
    sitemap_url = f"https://tabelog.com/sitemap/{city}/"
    
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        area_data = []
        
        # Find all links that represent area pages
        # Area URLs follow pattern: https://tabelog.com/sitemap/{city}/A{code}/
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Check if the URL matches the area pattern
            if f'/sitemap/{city}/A' in href and href.endswith('/'):
                # Ensure it's a full URL
                if href.startswith('https://'):
                    full_url = href
                else:
                    full_url = f"https://tabelog.com{href}"

                # Extract area code from URL
                # URL pattern: https://tabelog.com/sitemap/{city}/A{code}/
                url_parts = full_url.rstrip('/').split('/')
                area_code = url_parts[-1] if url_parts else ''

                # Extract area name from link text
                area_name = link.get_text(strip=True)
                area_data.append((area_name, area_code, full_url))
        
        # Write results to CSV file
        output_dir = f"{os.getenv('LOCAL_GOOD_SPOTS_OUTPUT_DIR', '/restaurants/')}cities"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}/{city}.csv"
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(['area_name', 'area_code', 'url'])  # Header row
            for area_name, area_code, url in area_data:
                writer.writerow([area_name, area_code, url])
        
        print(f"Wrote {len(area_data)} areas to {output_file}")
        return area_data
        
    except requests.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        return []
    except Exception as e:
        print(f"Error parsing page: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    tokyo_areas = get_area_urls("tokyo")
    print(f"Found {len(tokyo_areas)} areas in Tokyo:")
    for area_name, area_code, url in tokyo_areas:
        print(f"{area_name} ({area_code}): {url}")