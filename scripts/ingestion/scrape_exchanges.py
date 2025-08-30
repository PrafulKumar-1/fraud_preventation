import os
import requests
from bs4 import BeautifulSoup
from google.cloud import storage, firestore
import functions_framework
from datetime import datetime
import hashlib

# --- Configuration ---
# This URL is an example. You will need to find the correct
# URL for BSE/NSE corporate announcements.
EXCHANGE_URL = "https://www.bseindia.com/corporates/ann.html" # Example URL

GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

# Initialize GCP Clients
db = firestore.Client(project=GCP_PROJECT_ID)
storage_client = storage.Client(project=GCP_PROJECT_ID)

def get_announcement_details(announcement_row):
    """
    Extracts details from a single announcement row.
    NOTE: This function is highly dependent on the website's HTML structure
    and will need to be adapted based on inspection of the target site.
    """
    try:
        # Example selectors - these MUST be changed
        link_tag = announcement_row.find('a', {'class': 'announcement-link'})
        title = link_tag.text.strip()
        detail_url = link_tag['href']
        
        date_tag = announcement_row.find('span', {'class': 'date'})
        date_str = date_tag.text.strip()
        
        ticker_tag = announcement_row.find('span', {'class': 'ticker'})
        ticker = ticker_tag.text.strip()

        # Fetch the full text from the detail page
        response = requests.get(detail_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        response.raise_for_status()
        detail_soup = BeautifulSoup(response.content, 'html.parser')
        
        # Example selector for the main content
        content_div = detail_soup.find('div', {'id': 'announcement-body'})
        full_text = content_div.get_text(separator='\n', strip=True)

        return {
            "ticker": ticker,
            "title": title,
            "announcement_date": date_str,
            "source_url": detail_url,
            "full_text": full_text
        }
    except Exception as e:
        print(f"Could not process an announcement row: {e}")
        return None

@functions_framework.http
def main_exchange_scraper(request):
    """
    Scrapes the latest corporate announcements, stores text in GCS,
    and metadata in Firestore.
    """
    print("Starting corporate announcement scraper.")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(EXCHANGE_URL, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example selector for the list of announcements
        announcements = soup.find_all('div', {'class': 'announcement-item'})
        
        if not announcements:
            print("No announcements found. Check CSS selectors.")
            return "No announcements found.", 200

        for item in announcements:
            details = get_announcement_details(item)
            if not details:
                continue

            # Create a unique ID for the announcement to prevent duplicates
            announcement_hash = hashlib.md5(details['source_url'].encode()).hexdigest()
            doc_ref = db.collection("corporate_announcements").document(announcement_hash)
            
            if doc_ref.get().exists:
                print(f"Announcement {details['title']} already exists. Skipping.")
                continue

            # 1. Store full text in GCS
            gcs_path = f"announcements/{details['ticker']}/{announcement_hash}.txt"
            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            blob = bucket.blob(gcs_path)
            blob.upload_from_string(details['full_text'], content_type='text/plain')
            print(f"Stored text for '{details['title']}' in GCS at {gcs_path}")

            # 2. Store metadata in Firestore
            metadata = {
                "ticker": details['ticker'],
                "title": details['title'],
                "announcement_date": details['announcement_date'], # Should be parsed to datetime in a real app
                "source_url": details['source_url'],
                "gcs_text_uri": f"gs://{GCS_BUCKET_NAME}/{gcs_path}",
                "scraped_at": firestore.SERVER_TIMESTAMP
            }
            doc_ref.set(metadata)
            print(f"Stored metadata for '{details['title']}' in Firestore.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch announcements page: {e}")
        return f"Error fetching page: {e}", 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}", 500

    print("Corporate announcement scraper finished.")
    return "Scraping process completed.", 200