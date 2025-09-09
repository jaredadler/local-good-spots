import requests
import os
import re
from typing import Callable


def tabelog_restaurant_url_to_filename(url_string) -> str:
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
        return f"{'-'.join([match.group(1), match.group(2), match.group(3)])}.html"
    else:
        raise Exception("Tabelog restaurant URL does not match pattern")


def scrape_url(target_url: str, output_directory: str, construct_filename: Callable[[str | None], str]) -> str | None:
    """
    Scrape a URL and save to specified directory with a filename determined by supplied function construct_filename.
    
    Args:
        :param output_directory: The URL to scrape
        :param target_url: Directory to save the scraped content
        :param construct_filename: A function that returns the filename to write the URL raw contents to
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)
        
        # Send GET request to the URL
        response = requests.get(target_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Save to file
        output_file = os.path.join(output_directory, construct_filename(target_url))
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
    
    scrape_url(url, output_dir, tabelog_restaurant_url_to_filename)