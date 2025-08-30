from fastapi import APIRouter, HTTPException, Query
from google.cloud import firestore
from typing import List
from....core.config import settings
from....models.schemas import VerificationResponse, Intermediary

router = APIRouter()

# Initialize Firestore client
# In a production app, this would be managed more robustly (e.g., dependency injection)
try:
    db = firestore.Client(project=settings.GCP_PROJECT_ID)
except Exception as e:
    print(f"Could not initialize Firestore client: {e}")
    db = None


@router.get("/intermediary", response_model=VerificationResponse)
async def verify_intermediary(
    query: str = Query(..., min_length=3, description="Name or Registration Number of the intermediary")
):
    """
    Verifies an intermediary against the scraped SEBI database in Firestore.
    Performs a case-insensitive search on name and registration number.
    """
    if not db:
        raise HTTPException(status_code=503, detail="Firestore service is not available.")

    results =[]
    collection_ref = db.collection("sebi_intermediaries")

    # Firestore does not support case-insensitive queries directly or partial text search.
    # A common workaround for small-to-medium datasets is to fetch and filter in memory,
    # or use a third-party search service like Algolia or Elasticsearch for larger scale.
    # For this zero-cost implementation, we will fetch all and filter.
    # This is NOT scalable but works for an MVP.

    try:
        query_lower = query.lower()
        all_docs = collection_ref.stream()

        for doc in all_docs:
            data = doc.to_dict()
            name = data.get("name", "").lower()
            reg_no = data.get("registration_no", "").lower()

            if query_lower in name or query_lower in reg_no:
                results.append(Intermediary(**data))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while querying Firestore: {e}")

    if not results:
        return VerificationResponse(status="Not Found", count=0, results=[])

    return VerificationResponse(status="Verified", count=len(results), results=results)