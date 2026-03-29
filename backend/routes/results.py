from fastapi import APIRouter, HTTPException
from models import ScanResult

router = APIRouter()

# Import the shared store from analyze route
from routes.analyze import _results_store

@router.get("/results/{scan_id}", response_model=ScanResult)
async def get_results(scan_id: str):
    if scan_id not in _results_store:
        raise HTTPException(status_code=404, detail=f"Scan {scan_id} not found.")
    return _results_store[scan_id]
