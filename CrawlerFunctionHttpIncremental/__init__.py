import logging
import os
from urllib.parse import urlparse, urljoin
import azure.functions as func
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def save_html(url, base_directory, link_text=None):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        directory = os.path.join(base_directory, parsed_url.netloc, os.path.dirname(path))
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        if link_text:
            sanitized_link_text = sanitize_filename(link_text)
            file_name = os.path.join(directory, f"{sanitized_link_text}.html")
        else:
            file_name = os.path.join(directory, sanitize_filename(os.path.basename(path) or 'index.html'))
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(str(soup))
        logging.info(f'Documentation saved to {file_name}.')
        return soup, directory
    except requests.exceptions.RequestException as e:
        logging.error(f'Error during requests to {url}: {str(e)}')
        return None, None
    except OSError as e:
        logging.error(f'Error creating directory or writing file: {str(e)}')
        return None, None

def crawl(url, base_directory, visited, last_crawl_date, link_text=None):
    if url in visited:
        return
    visited.add(url)
    soup, directory = save_html(url, base_directory, link_text)
    if soup is None:
        return
    for link in soup.find_all('a', href=True):
        href = link['href']
        next_url = urljoin(url, href)
        if next_url.endswith('?'):
            next_url = next_url[:-1]
        if urlparse(next_url).netloc == urlparse(url).netloc:
            mod_date_str = link.get('data-mod-date')
            if mod_date_str:
                mod_date = datetime.strptime(mod_date_str, '%Y-%m-%d')
                if mod_date > last_crawl_date:
                    crawl(next_url, base_directory, visited, last_crawl_date, link.get_text(strip=True) or None)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')
    url = req.params.get('url')
    if not url:
        return func.HttpResponse("Please provide a URL to crawl.", status_code=400)
    last_crawl_date_str = req.params.get('last_crawl_date')
    if not last_crawl_date_str:
        return func.HttpResponse("Please provide the last crawl date in YYYY-MM-DD format.", status_code=400)
    try:
        last_crawl_date = datetime.strptime(last_crawl_date_str, '%Y-%m-%d')
    except ValueError:
        return func.HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status_code=400)
    visited = set()
    base_directory = 'collected_docs'
    crawl(url, base_directory, visited, last_crawl_date)
    return func.HttpResponse(f'Documentation successfully crawled and saved.', status_code=200)