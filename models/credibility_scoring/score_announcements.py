import os
import spacy
from google.cloud import firestore, storage

# --- Configuration ---
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")

# Load spaCy model
# Run `python -m spacy download en_core_web_sm` locally first
nlp = spacy.load("en_core_web_sm")

# Lexicon of promotional/vague keywords
PROMOTIONAL_WORDS = {"revolutionary", "groundbreaking", "unprecedented", "game-changing", "guaranteed"}
VAGUE_WORDS = {"may", "could", "potentially", "significant", "substantial", "improved"}

# Initialize Clients
db = firestore.Client(project=GCP_PROJECT_ID)
storage_client = storage.Client(project=GCP_PROJECT_ID)


def calculate_credibility_score(text):
    """Calculates a credibility score based on a hybrid NLP pipeline."""
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc]

    score = 100.0
    penalties =[]
    # 1. Qualitative Red Flag Analysis (Rule-Based)
    promo_count = sum(1 for token in tokens if token in PROMOTIONAL_WORDS)
    if promo_count > 0:
        penalty = promo_count * 5.0
        score -= penalty
        penalties.append(f"Found {promo_count} promotional keywords. (-{penalty} pts)")
    # 2. Vagueness and Specificity Detection (Linguistic Analysis)
    vague_count = sum(1 for token in tokens if token in VAGUE_WORDS)
    if vague_count > 2:  # Allow some vague words
        penalty = (vague_count - 2) * 2.0
        score -= penalty
        penalties.append(f"Found {vague_count} vague/non-committal words. (-{penalty} pts)")
    # 3. Quantitative Claim Extraction (NER)
    # A more advanced version would use a fine-tuned NER model.
    # Here, we use spaCy's built-in entities.
    money_entities =[]
    quantity_entities =[]

    if not money_entities and not quantity_entities:
        penalty = 10.0
        score -= penalty
        penalties.append(f"No specific quantitative claims (money, quantity) found. (-{penalty} pts)")
    else:
        # Bonus for having specific claims
        bonus = (len(money_entities) + len(quantity_entities)) * 2.5
        score += bonus
        penalties.append(f"Found {len(money_entities) + len(quantity_entities)} quantitative claims. (+{bonus} pts)")
    # 4. Historical Cross-Verification (Placeholder)
    # This step would fetch historical financial data for the ticker and
    # compare the extracted claims. This is a complex task requiring
    # another data pipeline. We'll just add a note here.
    penalties.append("NOTE: Historical cross-verification not performed in this version.")
    final_score = max(0, min(100, score))  # Clamp score between 0 and 100

    return {
        "score": round(final_score),
        "breakdown": penalties
    }


def process_new_announcements():
    """
    Finds unscored announcements in Firestore, scores them, and updates the record.
    """
    print("Checking for new announcements to score.")
    announcements_ref = db.collection("corporate_announcements")
    query = announcements_ref.where("credibility_score", "==", None).limit(10)

    for doc in query.stream():
        data = doc.to_dict()
        print(f"Processing announcement: {data['title']}")

        try:
            gcs_uri = data['gcs_text_uri']
            # Correctly parse bucket name and blob name from GCS URI
            # GCS URI format: gs://bucket_name/path/to/blob
            uri_parts = gcs_uri.split('/')
            bucket_name = uri_parts
            blob_name = '/'.join(uri_parts[3:])

            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            text = blob.download_as_text()

            score_result = calculate_credibility_score(text)

            # Update the Firestore document with the score
            doc.reference.update({
                "credibility_score": score_result["score"],
                "credibility_breakdown": score_result["breakdown"],
                "scored_at": firestore.SERVER_TIMESTAMP
            })
            print(f"Successfully scored '{data['title']}' with a score of {score_result['score']}.")
        except Exception as e:
            print(f"Failed to process announcement {doc.id}: {e}")
            # Add error information to the document to prevent retries
            doc.reference.update({"credibility_score": -1, "error_message": str(e)})


if __name__ == "__main__":
    process_new_announcements()