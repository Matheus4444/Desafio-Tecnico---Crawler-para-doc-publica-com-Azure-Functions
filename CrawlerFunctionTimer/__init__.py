import logging
import os
from urllib.parse import urlparse, urljoin
import azure.functions as func
import re
import requests
from bs4 import BeautifulSoup

def save_html(url, base_directory, link_text=None):
    try:
        # Perform the web request
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse the URL to create directory structure
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        directory = os.path.join(base_directory, parsed_url.netloc, os.path.dirname(path))

        # Create a directory to store HTML files if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Determine the file name
        if link_text:
            # Sanitize link_text to create a valid file name
            sanitized_link_text = re.sub(r'[\/\\]', '_', link_text)
            file_name = os.path.join(directory, f"{sanitized_link_text}.html")
        else:
            file_name = os.path.join(directory, os.path.basename(path) or 'index.html')

        # Save the HTML content to a file
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

def crawl(url, base_directory, visited, link_text=None):
    if url in visited:
        return
    visited.add(url)

    soup, directory = save_html(url, base_directory, link_text)
    if soup is None:
        return

    # Find all links on the page
    for link in soup.find_all('a', href=True):
        href = link['href']
        next_url = urljoin(url, href)
        if urlparse(next_url).netloc == urlparse(url).netloc:
            crawl(next_url, base_directory, visited, link.get_text(strip=True) or None)

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Timer trigger function executed at %s', mytimer.schedule_status['Last'])

    # URL of the documentation to crawl
    url = "https://sapiensia.atlassian.net/wiki/spaces/SIA/overview?homepageId=578912377"

    visited = set()
    base_directory = 'collected_docs'
    crawl(url, base_directory, visited)

    logging.info('Documentation successfully crawled and saved.')