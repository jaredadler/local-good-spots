import json
from bs4 import BeautifulSoup
import re,os


def parse_tabelog_html(filepath):
    """
    Extract restaurant metadata from Tabelog HTML file.
    
    Args:
        filepath (str): Path to the HTML file containing Tabelog restaurant data
        
    Returns:
        dict: JSON object with restaurant metadata in format:
              {"restaurantName": "", "reviewScore": "", "reviewCount": "", 
               "restaurantGenre": ["", ""], "closestTrainStation": "", 
               "address": "", "telephone": "", "priceDinnerMin": "", 
               "priceDinnerMax": "", "priceLunchMin": "", "priceLunchMax": ""}
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize result dictionary
    result = {
        "restaurantName": "",
        "reviewScore": "",
        "reviewCount": "",
        "restaurantGenre": [],
        "closestTrainStation": "",
        "address": "",
        "telephone": "",
        "priceDinnerMin": "",
        "priceDinnerMax": "",
        "priceLunchMin": "",
        "priceLunchMax": ""
    }
    
    # Extract restaurant name from JSON-LD structured data
    script_tags = soup.find_all('script', type='application/ld+json')
    for script in script_tags:
        try:
            json_data = json.loads(script.string)
            if json_data.get('@type') == 'Restaurant':
                result["restaurantName"] = json_data.get('name', '')
                
                # Extract review score and count
                aggregate_rating = json_data.get('aggregateRating', {})
                result["reviewScore"] = str(aggregate_rating.get('ratingValue', ''))
                result["reviewCount"] = str(aggregate_rating.get('ratingCount', ''))
                
                # Extract genres from servesCuisine
                serves_cuisine = json_data.get('servesCuisine', '')
                if serves_cuisine:
                    result["restaurantGenre"] = [genre.strip() for genre in serves_cuisine.split('、')]
                
                # Extract telephone number
                result["telephone"] = json_data.get('telephone', '')
                
                break
        except (json.JSONDecodeError, AttributeError):
            continue
    
    # Extract closest train station - look for "最寄り駅" section
    # Search for the text "最寄り駅" and extract the station name that follows
    page_text = soup.get_text()
    
    # Look for "最寄り駅:" pattern
    station_pattern = r'最寄り駅:\s*([^\s\n]+)駅?'
    station_match = re.search(station_pattern, page_text)
    if station_match:
        result["closestTrainStation"] = station_match.group(1)
    
    # Find all table rows and extract address and price information
    table_rows = soup.find_all('tr')
    for row in table_rows:
        cells = row.find_all(['td', 'th'])
        for i, cell in enumerate(cells):
            cell_text = cell.get_text().strip()
            
            # Look for address
            if '住所' in cell_text:
                if i + 1 < len(cells):
                    address_text = cells[i + 1].get_text().strip()
                    # Take only the first line of the address
                    result["address"] = address_text.split('\n')[0].strip()
    
    # Extract price ranges from rdheader-budget div
    budget_div = soup.find('div', class_='rdheader-budget')
    if budget_div:
        # Find dinner prices (c-rating-v3__time--dinner)
        dinner_section = budget_div.find('i', class_='c-rating-v3__time--dinner')
        if dinner_section:
            dinner_parent = dinner_section.find_parent('p')
            if dinner_parent:
                dinner_price_link = dinner_parent.find('a', class_='rdheader-budget__price-target')
                if dinner_price_link:
                    dinner_price_text = dinner_price_link.get_text().strip()
                    # Parse dinner price range (e.g., "￥5,000～￥5,999")
                    dinner_match = re.search(r'￥([0-9,]+)～￥([0-9,]+)', dinner_price_text)
                    if dinner_match:
                        result["priceDinnerMin"] = dinner_match.group(1).replace(',', '')
                        result["priceDinnerMax"] = dinner_match.group(2).replace(',', '')
        
        # Find lunch prices (c-rating-v3__time--lunch)
        lunch_section = budget_div.find('i', class_='c-rating-v3__time--lunch')
        if lunch_section:
            lunch_parent = lunch_section.find_parent('p')
            if lunch_parent:
                lunch_price_link = lunch_parent.find('a', class_='rdheader-budget__price-target')
                if lunch_price_link:
                    lunch_price_text = lunch_price_link.get_text().strip()
                    # Parse lunch price range (e.g., "～￥999" or "￥1,000～￥1,999")
                    if lunch_price_text.startswith('～￥'):
                        # Format like "～￥999" (only max price)
                        lunch_max_match = re.search(r'～￥([0-9,]+)', lunch_price_text)
                        if lunch_max_match:
                            result["priceLunchMin"] = "0"
                            result["priceLunchMax"] = lunch_max_match.group(1).replace(',', '')
                    else:
                        # Format like "￥1,000～￥1,999" (min and max)
                        lunch_match = re.search(r'￥([0-9,]+)～￥([0-9,]+)', lunch_price_text)
                        if lunch_match:
                            result["priceLunchMin"] = lunch_match.group(1).replace(',', '')
                            result["priceLunchMax"] = lunch_match.group(2).replace(',', '')

    print(result)
    return result


if __name__ == "__main__":
    # Example usage
    tabelog_html_file = f"{os.getenv('LOCAL_GOOD_SPOTS_OUTPUT_DIR', '/restaurants/')}restaurants/tokyo-A1317-A131706.html"

    parse_tabelog_html(tabelog_html_file)