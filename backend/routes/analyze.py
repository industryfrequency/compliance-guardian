from fastapi import APIRouter, HTTPException
from models import ScanRequest, ScanResult
from services.analysis_engine import AnalysisEngine
import time

router = APIRouter()

# In-memory results store
_results_store: dict[str, ScanResult] = {}

@router.post("/analyze", response_model=ScanResult)
async def run_compliance_scan(request: ScanRequest):
    if not request.rules:
        raise HTTPException(status_code=400, detail="At least one compliance rule is required.")

    engine = AnalysisEngine()
    start = time.time()

    try:
        violations = engine.run_scan(
            video_id=request.video_id,
            index_id=request.index_id,
            rules=request.rules
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    elapsed = round(time.time() - start, 2)
    enabled_rules = [r for r in request.rules if r.enabled]

    result = ScanResult(
        video_id=request.video_id,
        index_id=request.index_id,
        violations=violations,
        total_violations=len(violations),
        rules_checked=len(enabled_rules),
        processing_time_seconds=elapsed
    )

    _results_store[result.scan_id] = result
    return result
