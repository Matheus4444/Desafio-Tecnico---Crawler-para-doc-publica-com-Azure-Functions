import logging
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
import azure.functions as func

def main(mytimer: func.TimerRequest) -> None:
    logging.info('Timer trigger function executed at %s', mytimer.schedule_status.last)

    # URL of the documentation to crawl
    url = "https://example.com/documentation"  # Replace with the actual URL

    try:
        # Perform the web request
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse the URL to create directory structure
        parsed_url = urlparse(url)
        path = parsed_url.path.strip('/')
        directory = os.path.join('collected_docs', parsed_url.netloc, path)

        # Create a directory to store HTML files if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Save the HTML content to a file
        file_name = os.path.join(directory, 'index.html')
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(str(soup))

        logging.info(f'Documentation saved to {file_name}.')

    except requests.exceptions.RequestException as e:
        logging.error(f'Error during requests to {url}: {str(e)}')