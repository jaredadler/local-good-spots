import requests
import os
import re


def parse_tabelog_url(url_string):
    """
    Parse Tabelog URL to extract top-level area, lower-level area, and restaurant ID
    
    Args:
        url_string (str): Tabelog restaurant URL
        
    Returns:
        tuple: (top_level_area, lower_level_area, restaurant_id) or (None, None, None) if parsing fails
    """
    # Pattern to match Tabelog URL structure: /tokyo/A1317/A131701/13312586/
    pattern = r'/[^/]+/([^/]+)/([^/]+)/([^/]+)/?'
    match = re.search(pattern, url_string)
    
    if match:
        return match.group(1), match.group(2), match.group(3)
    return None, None, None


def scrape_url(target_url, output_directory):
    """
    Scrape content from a URL and save to local directory
    
    Args:
        target_url (str): The URL to scrape
        output_directory (str): Directory to save the scraped content
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Parse the Tabelog URL to get filename components
        top_level, lower_level, restaurant_id = parse_tabelog_url(target_url)
        
        if top_level and lower_level and restaurant_id:
            filename = f"{top_level}-{lower_level}-{restaurant_id}.html"
        else:
            # Fallback to original filename if URL parsing fails
            filename = 'scraped_content.txt'
        
        # Send GET request to the URL
        response = requests.get(target_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Save to file
        output_file = os.path.join(output_directory, filename)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Content successfully scraped and saved to: {output_file}")
        return output_file
        
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None
    except Exception as e:
        print(f"Error processing content: {e}")
        return None


if __name__ == "__main__":
    # Example usage - update the URL as needed
    url = "https://tabelog.com/tokyo/A1317/A131706/13120700/"  # Replace with your actual URL, this is an example
    output_dir = f"{os.getenv('LOCAL_GOOD_SPOTS_OUTPUT_DIR', '/restaurants/')}restaurants/"  # Uses OUTPUT_DIR env var or defaults to "/restaurants/"
    
    scrape_url(url, output_dir)