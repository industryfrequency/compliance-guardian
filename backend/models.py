from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import uuid
from datetime import datetime

class Severity(str, Enum):
    critical = "critical"
    warning = "warning"
    info = "info"

class VideoIngestRequest(BaseModel):
    url: Optional[str] = None
    # file upload handled via UploadFile in the route

class VideoIngestResponse(BaseModel):
    index_id: str
    video_id: str
    status: str
    duration: Optional[float] = None
    message: str

class ComplianceRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str
    category: str = "general"
    enabled: bool = True

class RuleSetRequest(BaseModel):
    rules: list[ComplianceRule]

class RuleSetResponse(BaseModel):
    rules: list[ComplianceRule]
    count: int

class Violation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp_start: float
    timestamp_end: float
    confidence: float = Field(ge=0.0, le=1.0)
    severity: Severity = Severity.warning
    rule_id: str
    rule_text: str
    reasoning: str
    source: str  # "search" | "analyze" | "merged"
    thumbnail_url: Optional[str] = None

class ScanRequest(BaseModel):
    video_id: str
    index_id: str
    rules: list[ComplianceRule]

class ScanResult(BaseModel):
    scan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    video_id: str
    index_id: str
    violations: list[Violation]
    total_violations: int
    rules_checked: int
    processing_time_seconds: float
    scanned_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    twelvelabs_connected: bool
