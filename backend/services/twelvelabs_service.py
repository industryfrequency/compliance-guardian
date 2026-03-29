import os
from twelvelabs import TwelveLabs
from twelvelabs.errors import BadRequestError, NotFoundError
from config import settings
from typing import Optional

class TwelveLabsService:
    def __init__(self):
        self.client = TwelveLabs(api_key=settings.twelvelabs_api_key)
        self._index_id: Optional[str] = None

    def verify_connection(self) -> bool:
        try:
            indexes = self.client.indexes.list(page_limit=1)
            return True
        except Exception:
            return False

    def ensure_index(self) -> str:
        if self._index_id:
            return self._index_id

        try:
            indexes = self.client.indexes.list(page_limit=50)
            for idx in indexes:
                if idx.index_name == settings.twelvelabs_index_name:
                    self._index_id = idx.id
                    return self._index_id
        except Exception:
            pass

        index = self.client.indexes.create(
            index_name=settings.twelvelabs_index_name,
            models=[
                {
                    "model_name": "marengo3.0",
                    "model_options": ["visual", "audio"]
                },
                {
                    "model_name": "pegasus1.2",
                    "model_options": ["visual", "audio"]
                }
            ],
            addons=["thumbnail"]
        )
        self._index_id = index.id
        return self._index_id

    def upload_video_by_url(self, index_id: str, url: str) -> tuple[str, str]:
        task = self.client.tasks.create(index_id=index_id, video_url=url)
        return self._poll_task(task)

    def upload_video_by_file(self, index_id: str, file_path: str) -> tuple[str, str]:
        with open(file_path, "rb") as f:
            task = self.client.tasks.create(index_id=index_id, video_file=f)
        return self._poll_task(task)

    def _poll_task(self, task) -> tuple[str, str]:
        import time
        task_id = task.id
        while True:
            updated = self.client.tasks.retrieve(task_id)
            if updated.status in ("ready", "failed"):
                return updated.video_id, updated.status
            print(f"  Indexing status: {updated.status}...")
            time.sleep(5)

    def search_for_violations(self, index_id: str, query_text: str, page_limit: int = 20) -> list[dict]:
        try:
            results = self.client.search.query(
                index_id=index_id,
                query_text=query_text,
                search_options=["visual", "audio"],
                group_by="clip",
                page_limit=page_limit
            )

            clips = []
            for item in results:
                clips.append({
                    "start": item.start,
                    "end": item.end,
                    "rank": item.rank,
                    "video_id": item.video_id,
                    "thumbnail_url": getattr(item, "thumbnail_url", None),
                    "transcription": getattr(item, "transcription", None),
                })
            return clips
        except Exception as e:
            print(f"Search error for query '{query_text}': {e}")
            return []

    def analyze_for_violations(self, video_id: str, rule_text: str) -> dict:
        prompt = f"""You are a broadcast compliance auditor reviewing video content.

Analyze this video for the following compliance rule violation:
"{rule_text}"

For EACH violation found, provide:
1. timestamp_start: start time in seconds
2. timestamp_end: end time in seconds
3. confidence: your confidence level from 0.0 to 1.0
4. severity: "critical", "warning", or "info"
5. description: detailed explanation of what was detected and why it violates the rule

If NO violations are found, return an empty violations array.
Return ONLY valid JSON in this format:
{{"violations_found": true/false, "violations": [...]}}"""

        try:
            result = self.client.analyze(
                video_id=video_id,
                prompt=prompt,
                temperature=0.1,
                max_tokens=4096
            )

            import json
            return json.loads(result.data)
        except Exception as e:
            print(f"Analyze error for rule '{rule_text}': {e}")
            return {"violations_found": False, "violations": []}
            