from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from models import VideoIngestResponse
from services.twelvelabs_service import TwelveLabsService
import tempfile
import os

router = APIRouter()
tl_service = TwelveLabsService()

@router.post("/ingest", response_model=VideoIngestResponse)
async def ingest_video(
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if not url and not file:
        raise HTTPException(status_code=400, detail="Provide either a video URL or file upload.")

    try:
        # Ensure index exists (create if not)
        index_id = tl_service.ensure_index()

        if url:
            video_id, status = tl_service.upload_video_by_url(index_id, url)
        else:
            # Save uploaded file to temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            try:
                video_id, status = tl_service.upload_video_by_file(index_id, tmp_path)
            finally:
                os.unlink(tmp_path)

        return VideoIngestResponse(
            index_id=index_id,
            video_id=video_id,
            status=status,
            message=f"Video indexed successfully. video_id={video_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {str(e)}")
