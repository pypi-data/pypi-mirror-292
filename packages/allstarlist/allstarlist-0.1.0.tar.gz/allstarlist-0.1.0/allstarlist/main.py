import os
import time
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import argparse
import signal
import logging
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Optional, Tuple

# Constants
DEFAULT_URL = "http://stats.allstarlink.org/stats/keyed"
DEFAULT_SLEEP_INTERVAL = 60  # seconds
CONFIG_FILE = os.path.expanduser("~/.allstar.json")
HEADER = "Node|Callsign|Frequency|CTCSS|Location"
MAGIC_NUMBER_TO_REMOVE_COLS = [1, 6]
console = Console()

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Session for requests
session = requests.Session()

def clear_terminal() -> None:
    """Clears the terminal screen."""
    os.system('clear')

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_data(url: str) -> Optional[str]:
    """Fetches data from the provided URL with retry logic.
    
    Args:
        url: The URL to fetch data from.
    
    Returns:
        The raw HTML content as a string, or None if the request fails.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; script/1.0)'}
    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            logging.info("Successfully fetched data from %s", url)
            return response.text
        else:
            logging.error("Failed to fetch data. Status code: %d", response.status_code)
            return None
    except requests.RequestException as e:
        logging.error("Error fetching data from %s: %s", url, e)
        return None

def parse_data(html_content: str) -> Optional[List[List[str]]]:
    """Parses the fetched HTML content and extracts relevant data.
    
    Args:
        html_content: The HTML content to parse.
    
    Returns:
        A list of rows, where each row is a list of column data, or None if parsing fails.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all(['th', 'td'])
            cols = [col.text.strip() for col in cols]
            # Remove specific columns (2 and 7)
            modified_cols = [cols[i] for i in range(len(cols)) if i not in MAGIC_NUMBER_TO_REMOVE_COLS]
            data.append(modified_cols)
        # Sort data numerically by node number
        data.sort(key=lambda x: int(x[0]))
        return data
    except (AttributeError, IndexError) as e:
        logging.error("Error parsing data: %s", e)
        return None

def print_table(data: List[List[str]]) -> None:
    """Prints the fetched data in a table format using rich library.
    
    Args:
        data: A list of rows, where each row is a list of column data.
    """
    if data:
        table = Table(show_header=True, header_style="bold cyan")
        headers = HEADER.split("|")
        colors = ["bold cyan", "bold green", "bold yellow", "bold orange_red1", "bold red"]

        # Add columns with styled headers
        for i, header in enumerate(headers):
            table.add_column(header, style=colors[i % len(colors)])

        # Add rows to the table
        for row in data:
            table.add_row(*row)

        console.print(table)
    else:
        logging.error("No data to display")

def handle_exit(signum, frame) -> None:
    """Handles exit signals to gracefully terminate the program."""
    logging.info("73 from W5ALC...")
    exit(0)

def load_config() -> Tuple[str, int]:
    """Loads configuration from a file or returns defaults if not available.
    
    Returns:
        A tuple containing the URL and the refresh interval.
    """
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
            url = config.get('url', DEFAULT_URL)
            interval = config.get('interval', DEFAULT_SLEEP_INTERVAL)
            logging.info("Configuration loaded successfully.")
            return url, interval
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning("Configuration file not found or invalid. Using default settings.")
        return DEFAULT_URL, DEFAULT_SLEEP_INTERVAL

def parse_args() -> Tuple[str, int]:
    """Parses command-line arguments.
    
    Returns:
        A tuple containing the URL and the refresh interval.
    """
    parser = argparse.ArgumentParser(description="Fetch and display AllStarLink stats.")
    parser.add_argument('--url', type=str, default=None, help="URL to fetch data from")
    parser.add_argument('--interval', type=int, default=None, help="Refresh interval in seconds")
    args = parser.parse_args()

    # Load configuration file settings
    config_url, config_interval = load_config()

    # Override configuration file settings with command-line arguments if provided
    url = args.url if args.url else config_url
    interval = args.interval if args.interval else config_interval

    return url, interval

def run_allstar_fetch(url: str, interval: int) -> None:
    """Main loop for fetching and displaying AllStarLink data.
    
    Args:
        url: The URL to fetch data from.
        interval: The interval in seconds between fetches.
    """
    while True:
        clear_terminal()
        html_content = fetch_data(url)
        if html_content:
            parsed_data = parse_data(html_content)
            if parsed_data:
                print_table(parsed_data)
        time.sleep(interval)

def main() -> None:
    """Entry point for the script."""
    url, interval = parse_args()

    # Setup signal handling
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        run_allstar_fetch(url, interval)
    except Exception as e:
        logging.error("Unhandled exception: %s", e)

if __name__ == "__main__":
    main()

