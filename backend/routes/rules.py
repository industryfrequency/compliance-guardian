from fastapi import APIRouter
from models import ComplianceRule, RuleSetRequest, RuleSetResponse

router = APIRouter()

# In-memory store (sufficient for hackathon demo)
_rules_store: list[ComplianceRule] = [
    ComplianceRule(id="default-1", text="Flag any frame containing visible alcohol branding or consumption", category="substance"),
    ComplianceRule(id="default-2", text="Flag physical violence, aggressive contact, or dangerous crowd behavior", category="violence"),
    ComplianceRule(id="default-3", text="Flag nudity, sexually suggestive content, or inappropriate exposure", category="adult"),
    ComplianceRule(id="default-4", text="Flag visible brand logos appearing within 3 seconds of dangerous or illegal activity", category="brand-safety"),
]

@router.get("/rules", response_model=RuleSetResponse)
async def get_rules():
    return RuleSetResponse(rules=_rules_store, count=len(_rules_store))

@router.post("/rules", response_model=RuleSetResponse)
async def set_rules(request: RuleSetRequest):
    global _rules_store
    _rules_store = request.rules
    return RuleSetResponse(rules=_rules_store, count=len(_rules_store))
