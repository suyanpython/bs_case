# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 08:45:19 2024

@author: Suyan
"""



import requests
from bs4 import BeautifulSoup
import json
import re, sys , os

# Base URL and query parameters
base_url = "https://www.hellowork.com"
params_list = [
    {"lang": "full stack", "city": "aix-en-provence","type":"CDI","page":"1"},
    {"lang": "fullstack", "city": "aix-en-provence","type":"CDI","page":"1"},
    {"lang": "python", "city": "aix-en-provence","type":"CDI","page":"1"},
    {"lang": "developpeur web", "city": "marseille","type":"CDI","page":"1"},
]

# Generate URLs
# urls = [f"{base_url}/fr-fr/emploi/recherche.html?k={params['lang']}&l={params['city']}&c={params['type']}&p=1" for params in params_list]


def find_total_pages(url):
    try:
        session = requests.Session()
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")
        # Locate all <button> elements with type="submit" and name="p"
        pagination_buttons = soup.find_all("button", attrs={"type": "submit", "name": "p"})
        
        # Extract the values or text from each button to get page numbers
        page_numbers = [int(button["value"]) for button in pagination_buttons if button.has_attr("value")]
        
        # Get the maximum page number (total pages)
        return max(page_numbers) if page_numbers else 1
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return 1  # Default to 1 page if an error occurs or no pagination is found

# Dynamically generate URLs based on pagination
all_urls = []
for params in params_list:
    # Generate the URL for the first page
    first_page_url = f"{base_url}/fr-fr/emploi/recherche.html?k={params['lang']}&l={params['city']}&c={params['type']}&p=1"
    total_pages = find_total_pages(first_page_url)
    
    # Generate URLs for all pages
    for page in range(1, total_pages + 1):
        url = f"{base_url}/fr-fr/emploi/recherche.html?k={params['lang']}&l={params['city']}&c={params['type']}&p={page}"
        all_urls.append(url)



scraped_data = []  # To store the scraped results

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36"
}




def trim_word(text):
    # text = re.sub(r'(?<=\w)(?=[A-Z])(?!(?:[A-Z]){2,}|PHP|SQL|USA)', ' ', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'(H/F)(?=\S)', r'\1 ', text)
    return text

# Function to scrape a URL and extract its content
def scrape_inner_page(url,keyword="php"):
    try:
        session = requests.Session()
        response = session.get(url,headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find all <section> tags
        sections = soup.find_all("section")
       
        reversed_sections = []
        
        # Iterate over each section and process its text content
        for i, section in enumerate(sections, start=1):
            section_text = section.get_text(strip=True)  # Extract all text from the section
            section_text = trim_word(section_text)  # Apply any necessary word trimming
            # Check if section_text is not empty before appending
            if section_text:
                reversed_sections.append(section_text)
            
        return reversed_sections
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def is_url_in_file(file_path, url):
    """
    Check if a file exists and whether a specific URL is present in its content.
    
    Args:
        file_path (str): Path to the JSON file.
        url (str): The URL to check.

    Returns:
        bool: True if the file exists and the URL is found, False otherwise.
    """
    if not os.path.exists(file_path):
        # File does not exist
        return False
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Check if the data is a list of dictionaries and contains the URL
            if isinstance(data, list):
                return any(item.get("url") == url for item in data)
    except json.JSONDecodeError:
        # File exists but has invalid JSON
        return False
    
    return False

# File name
output_file = "scraped_data.json"

# Loop through each URL
for url in all_urls:
    try:
        session = requests.Session()
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            print(url)
            # Find all elements with class 'tw-grid'
            sections = soup.find_all("section")
            tw_grid_elements = []
            for section in sections:
                tw_grid_elements.extend(section.find_all(class_="tw-grid"))
            
            # Extract href values from <a> tags within those elements
            hrefs = []
            for element in tw_grid_elements:
                            
                a_tags = element.find_all("a", href=True)  # Find all <a> with an href attribute
                for a in a_tags:
                    
                    title = a.get('title')
                    aria_label = a.get('aria-label')
                    short_des = aria_label.split("à", 1)[1].strip()
                    hrefs.append(a["href"])
                    href_a = base_url + a["href"]
                    
                    if not is_url_in_file(output_file, href_a):
                        print(href_a)
                        inner_page_data = scrape_inner_page(href_a)
                        scraped_data.append({
                            "title": title, 
                            "short_description":short_des,
                            "url": href_a, 
                            "content": inner_page_data
                        })      
        else:
            print(f"Failed to fetch {url}: {response.status_code}")
    except Exception as e:
        print(f"Error occurred for {url}: {e}")

# Remove duplicates
unique_scraped_data = list(
    {json.dumps(item, sort_keys=True) for item in scraped_data}
)

# Deserialize back to dictionaries
scraped_data = [json.loads(item) for item in unique_scraped_data]


# Check if the file exists
if os.path.exists(output_file):
    # Read existing data and append to it
    with open(output_file, "r", encoding="utf-8") as f:
        try:
            existing_data = json.load(f)
        except json.JSONDecodeError:
            # If the file is empty or invalid, initialize as empty list
            existing_data = []
    
    # Ensure existing_data is a list and append the new data
    if isinstance(existing_data, list):
        existing_data.extend(scraped_data)
    else:
        # Handle case where existing data isn't a list
        existing_data = scraped_data

    # Write the updated data back to the file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)
else:
    # Create a new file and write the data
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)
        
# # Deserialize back to dictionaries
# scraped_data = [json.loads(item) for item in unique_scraped_data]

# # Save results to a JSON file
# output_file = "scraped_data.json"
# with open(output_file, "w", encoding="utf-8") as f:
#     json.dump(scraped_data, f, indent=4, ensure_ascii=False)
    
print(f"Scraping complete! Data saved to {output_file}")
