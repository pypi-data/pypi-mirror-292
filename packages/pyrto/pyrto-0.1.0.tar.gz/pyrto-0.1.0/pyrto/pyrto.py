import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fetch_vehicle_details(license_plate):
    url = f"https://www.carinfo.app/rc-details/{license_plate}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers, allow_redirects=True)
    
    if response.status_code != 200:
        logger.error(f"Failed to retrieve data for {license_plate}. HTTP Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text(separator='\n').strip()
    
    patterns = {
        'Owner Name': r'Owner Name\s*([\w\s*]+)',
        'Maker': r'Maker\s*([\s\S]*?)(?=\n[A-Za-z])',
        'RTO Number': r'Number\s*([\w-]+)',
        'Registered RTO Address': r'Registered RTO\s*([\s\S]*?)(?=\n[A-Za-z])',
        'City': r'City\s*([\w\s]+)',
        'State': r'State\s*([\w\s]+)',
        'RTO Phone Number': r'RTO Phone number\s*([\+\d-]+)',
        'Email': r'Email\s*([\w@.]+)',
    }
    
    results = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, page_text)
        if matches:
            combined = ' '.join(set(match.strip() for match in matches))
            results[key] = combined
        else:
            results[key] = 'Not found'
            logger.warning(f"No data found for {key}")
    
    if results['Maker']:
        maker_parts = re.split(r'\s*\n\s*', results['Maker'])
        maker_combined = ' '.join(part.strip() for part in maker_parts if part.strip())
        results['Maker'] = maker_combined
    
    if results['Owner Name']:
        owner_parts = re.split(r'\s*\n\s*', results['Owner Name'])
        owner_combined = ' '.join(part.strip() for part in owner_parts if part.strip())
        results['Owner Name'] = owner_combined
    
    logger.info("Vehicle Details:")
    for key, value in results.items():
        logger.info(f"{key}: {value}")
    
    return results

def fetch_vehicle_image(license_plate):
    url = f"https://www.carinfo.app/rc-details/{license_plate}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers, allow_redirects=True)
    
    if response.status_code != 200:
        logger.error(f"Failed to retrieve data for {license_plate}. HTTP Status code: {response.status_code}")
        return None
    
    img_pattern = r'https://imgd\.aeplcdn\.com[\S]+'
    img_urls = re.findall(img_pattern, response.text)
    
    if img_urls:
        img_url = img_urls[0]
        img_response = requests.get(img_url, headers=headers, allow_redirects=True)
        
        if img_response.status_code == 200:
            logger.info(f"Image successfully retrieved for {license_plate}")
            return Image.open(BytesIO(img_response.content))
        else:
            logger.error(f"Failed to retrieve image from {img_url}. HTTP Status code: {img_response.status_code}")
    else:
        logger.warning("No image found with the specified URL pattern.")
    
    return None