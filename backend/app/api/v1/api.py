from fastapi import APIRouter
from.endpoints import verify, scan

api_router = APIRouter()
api_router.include_router(verify.router, prefix="/verify", tags=["Verification"])
api_router.include_router(scan.router, prefix="/scan", tags=["Scanning"])
