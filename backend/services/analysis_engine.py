from models import ComplianceRule, Violation
from services.twelvelabs_service import TwelveLabsService
from services.result_merger import merge_and_deduplicate

class AnalysisEngine:
    def __init__(self):
        self.tl = TwelveLabsService()

    def run_scan(self, video_id: str, index_id: str, rules: list[ComplianceRule]) -> list[Violation]:
        all_violations: list[Violation] = []

        for rule in rules:
            if not rule.enabled:
                continue

            # STAGE 1: Marengo Search (semantic clip matching)
            search_clips = self.tl.search_for_violations(index_id, rule.text)

            search_violations = []
            for clip in search_clips:
                confidence = round(1.0 / clip["rank"], 3) if clip.get("rank") else 0.5
                confidence = min(confidence, 1.0)
                search_violations.append(Violation(
                    timestamp_start=clip["start"],
                    timestamp_end=clip["end"],
                    confidence=confidence,
                    severity="warning",
                    rule_id=rule.id,
                    rule_text=rule.text,
                    reasoning=f"Marengo visual/audio match (rank {clip.get('rank', 'N/A')})",
                    source="search",
                    thumbnail_url=clip.get("thumbnail_url")
                ))

            # STAGE 2: Pegasus Analysis (reasoned detection)
            analyze_result = self.tl.analyze_for_violations(video_id, rule.text)

            analyze_violations = []
            if analyze_result.get("violations_found"):
                for v in analyze_result.get("violations", []):
                    severity_raw = v.get("severity", "warning")
                    if severity_raw not in ("critical", "warning", "info"):
                        severity_raw = "warning"
                    analyze_violations.append(Violation(
                        timestamp_start=v.get("timestamp_start", 0),
                        timestamp_end=v.get("timestamp_end", 0),
                        confidence=min(max(v.get("confidence", 0.5), 0.0), 1.0),
                        severity=severity_raw,
                        rule_id=rule.id,
                        rule_text=rule.text,
                        reasoning=v.get("description", "Pegasus flagged a potential violation"),
                        source="analyze"
                    ))

            # STAGE 3: Merge and deduplicate
            merged = merge_and_deduplicate(search_violations, analyze_violations)
            all_violations.extend(merged)

        # Sort by timestamp, then by confidence descending
        all_violations.sort(key=lambda v: (v.timestamp_start, -v.confidence))
        return all_violations
