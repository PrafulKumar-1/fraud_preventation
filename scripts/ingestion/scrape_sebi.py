# import os
# import json
# import requests
# from bs4 import BeautifulSoup
# from google.cloud import storage, firestore
# import functions_framework

# # --- Configuration ---
# SEBI_URLS = {
#     "investment_advisers": "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13",
#     "research_analysts": "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=14"
# }

# # --- GCP Configuration ---
# GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
# GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

# # --- Initialize GCP Clients ---
# # This check is important for local execution vs. cloud deployment.
# if GCP_PROJECT_ID:
#     db = firestore.Client(project=GCP_PROJECT_ID)
#     storage_client = storage.Client(project=GCP_PROJECT_ID)
# else:
#     print("Warning: GCP_PROJECT_ID not set. GCP clients not initialized.")
#     db = None
#     storage_client = None

# def upload_to_gcs(data, destination_blob_name):
#     """Uploads a dictionary as a JSON file to the GCS bucket."""
#     if not storage_client or not GCS_BUCKET_NAME:
#         print("GCS client not initialized or bucket name not set. Skipping upload.")
#         return
#     bucket = storage_client.bucket(GCS_BUCKET_NAME)
#     blob = bucket.blob(destination_blob_name)
#     blob.upload_from_string(json.dumps(data, indent=2), content_type='application/json')
#     print(f"Data successfully uploaded to gs://{GCS_BUCKET_NAME}/{destination_blob_name}")

# def update_firestore(data, collection_name):
#     """
#     Updates a Firestore collection with the scraped data.
#     It uses the registration number as the document ID for idempotency.
#     """
#     if not db:
#         print("Firestore client not initialized. Skipping update.")
#         return
        
#     collection_ref = db.collection(collection_name)
#     batch = db.batch()
#     count = 0

#     for record in data:
#         reg_no = record.get("registration_no")
#         if reg_no:
#             doc_ref = collection_ref.document(reg_no.replace("/", "_"))
#             batch.set(doc_ref, record)
#             count += 1
#             if count % 499 == 0:
#                 batch.commit()
#                 batch = db.batch()
#                 print(f"Committed batch of {count} records to Firestore.")

#     if count > 0 and count % 499 != 0:
#         batch.commit()
#     print(f"Finished updating Firestore. Total records processed: {len(data)}")

# def scrape_sebi_page(url):
#     """Scrapes a single SEBI intermediary page, handling pagination."""
#     all_records = []
#     page_num = 1
    
#     while True:
#         try:
#             paginated_url = f"{url}&pageNo={page_num}"
#             print(f"Scraping page: {paginated_url}")
            
#             headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
#             response = requests.get(paginated_url, headers=headers, timeout=30)
#             response.raise_for_status()

#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             # Find the main table containing the data. This selector may need adjustment.
#             table = soup.find('table', {'class': 'table table-striped'})
#             if not table:
#                 print(f"No data table found on page {page_num}. Ending scrape for this URL.")
#                 break

#             rows = table.find_all('tr')
#             if len(rows) <= 1:
#                 print(f"No data rows found on page {page_num}. Ending scrape for this URL.")
#                 break

#             headers_raw = [th.text.strip().lower().replace(' ', '_') for th in rows[0].find_all('th')]
            
#             page_records = []
#             for row in rows[1:]:
#                 cols = row.find_all('td')
#                 if len(cols) == len(headers_raw):
#                     record = {headers_raw[i]: cols[i].text.strip() for i in range(len(cols))}
#                     page_records.append(record)
            
#             if not page_records:
#                 print(f"No records extracted on page {page_num}. Ending scrape.")
#                 break

#             all_records.extend(page_records)
#             print(f"Found {len(page_records)} records on page {page_num}.")
#             page_num += 1

#         except requests.exceptions.RequestException as e:
#             print(f"Error fetching page {page_num}: {e}")
#             break
#         except Exception as e:
#             print(f"An unexpected error occurred on page {page_num}: {e}")
#             break
            
#     return all_records

# # This is the entry point for Google Cloud Functions
# @functions_framework.http
# def main_scraper(request):
#     """
#     Main function triggered by HTTP request or Cloud Scheduler.
#     """
#     run_scraper_logic()
#     return "Scraping process completed.", 200

# # This function contains the core logic, separated for local testing
# def run_scraper_logic():
#     """
#     Scrapes all configured SEBI URLs and stores the data in GCS and Firestore.
#     """
#     print("Starting Project Suraksha SEBI Scraper.")
    
#     for entity_type, url in SEBI_URLS.items():
#         print(f"--- Processing {entity_type} ---")
#         scraped_data = scrape_sebi_page(url)
        
#         if scraped_data:
#             gcs_filename = f"sebi_data/{entity_type}_latest.json"
#             upload_to_gcs(scraped_data, gcs_filename)
            
#             for record in scraped_data:
#                 record['entity_type'] = entity_type
#             update_firestore(scraped_data, "sebi_intermediaries")
#         else:
#             print(f"No data scraped for {entity_type}. Skipping storage.")
            
#     print("SEBI Scraper finished successfully.")

# # This block allows you to run the script directly from your terminal for testing
# if __name__ == "__main__":
#     # Check for environment variables needed for local run
#     if not GCP_PROJECT_ID or not GCS_BUCKET_NAME:
#         print("Error: Make sure GCP_PROJECT_ID and GCS_BUCKET_NAME environment variables are set.")
#     else:
#         run_scraper_logic()


import os
import json
import requests
from bs4 import BeautifulSoup
from google.cloud import storage, firestore
import functions_framework
import re

# --- Configuration ---
SEBI_URLS = {
    "investment_advisers": "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13",
    "research_analysts": "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=14"
}

# --- GCP Configuration ---
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

# --- Initialize GCP Clients ---
if GCP_PROJECT_ID:
    db = firestore.Client(project=GCP_PROJECT_ID)
    storage_client = storage.Client(project=GCP_PROJECT_ID)
else:
    print("Warning: GCP_PROJECT_ID not set. GCP clients not initialized.")
    db = None
    storage_client = None

def upload_to_gcs(data, destination_blob_name):
    """Uploads a dictionary as a JSON file to the GCS bucket."""
    if not storage_client or not GCS_BUCKET_NAME:
        print("GCS client not initialized or bucket name not set. Skipping upload.")
        return
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(json.dumps(data, indent=2), content_type='application/json')
    print(f"Data successfully uploaded to gs://{GCS_BUCKET_NAME}/{destination_blob_name}")

def update_firestore(data, collection_name):
    """Updates a Firestore collection with the scraped data."""
    if not db:
        print("Firestore client not initialized. Skipping update.")
        return
        
    collection_ref = db.collection(collection_name)
    batch = db.batch()
    count = 0

    for record in data:
        reg_no = record.get("registration_no")
        if reg_no:
            doc_id = reg_no.replace("/", "_").replace(" ", "")
            doc_ref = collection_ref.document(doc_id)
            batch.set(doc_ref, record)
            count += 1
            if count % 499 == 0:
                batch.commit()
                batch = db.batch()
                print(f"Committed batch of {count} records to Firestore.")

    if count > 0 and count % 499 != 0:
        batch.commit()
    print(f"Finished updating Firestore. Total records processed: {len(data)}")

def scrape_sebi_page_final(url):
    """
    Scrapes a single SEBI intermediary page with logic to prevent infinite loops.
    """
    all_records = []
    page_num = 1
    # **NEW LOGIC**: Keep track of the last page's content to detect loops.
    last_page_content_ids = set()
    
    while True:
        try:
            paginated_url = f"{url}&pageNo={page_num}"
            print(f"Scraping page: {paginated_url}")
            
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'}
            response = requests.get(paginated_url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            
            record_containers = soup.find_all('div', {'class': 'fixed-table-body card-table'})
            
            if not record_containers:
                print(f"No record containers found on page {page_num}. Ending scrape for this URL.")
                break

            page_records = []
            # **NEW LOGIC**: Store the IDs of records found on the current page.
            current_page_content_ids = set()

            for container in record_containers:
                record = {}
                card_views = container.find_all('div', class_='card-view')
                for view in card_views:
                    title_tag = view.find('div', class_='title')
                    value_tag = view.find('div', class_='value')
                    
                    if title_tag and value_tag:
                        key = title_tag.text.strip().lower().replace(' ', '_').replace('.', '').replace('/', '_')
                        value = value_tag.text.strip()
                        record[key] = value
                
                if 'registration_no' in record and record['registration_no']:
                    page_records.append(record)
                    current_page_content_ids.add(record['registration_no'])

            # **INFINITE LOOP CHECK**: If we see the same content as the last page, stop.
            if page_num > 1 and not current_page_content_ids.difference(last_page_content_ids):
                print("Duplicate content detected. Ending pagination to prevent infinite loop.")
                break
            
            last_page_content_ids = current_page_content_ids

            all_records.extend(page_records)
            print(f"Found {len(page_records)} records on page {page_num}.")
            
            # Keep the original pagination check as a fallback.
            next_link = soup.find('a', title='Next')
            if not next_link:
                 print("No 'Next' button found. This is the last page.")
                 break
                 
            page_num += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            break
        except Exception as e:
            print(f"An unexpected error occurred on page {page_num}: {e}")
            break
            
    return all_records

@functions_framework.http
def main_scraper(request):
    """Main function triggered by HTTP request or Cloud Scheduler."""
    run_scraper_logic()
    return "Scraping process completed.", 200

def run_scraper_logic():
    """Scrapes all configured SEBI URLs and stores the data."""
    print("Starting Project Suraksha SEBI Scraper.")
    
    for entity_type, url in SEBI_URLS.items():
        print(f"--- Processing {entity_type} ---")
        scraped_data = scrape_sebi_page_final(url)
        
        if scraped_data:
            gcs_filename = f"sebi_data/{entity_type}_latest.json"
            upload_to_gcs(scraped_data, gcs_filename)
            
            for record in scraped_data:
                record['entity_type'] = entity_type
            update_firestore(scraped_data, "sebi_intermediaries")
        else:
            print(f"No data scraped for {entity_type}. Skipping storage.")
            
    print("SEBI Scraper finished successfully.")

# This block allows you to run the script directly from your terminal for testing
if __name__ == "__main__":
    if not GCP_PROJECT_ID or not GCS_BUCKET_NAME:
        print("Error: Make sure GCP_PROJECT_ID and GCS_BUCKET_NAME environment variables are set.")
    else:
        run_scraper_logic()