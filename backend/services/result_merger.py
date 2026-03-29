from models import Violation

def timestamps_overlap(a: Violation, b: Violation, tolerance: float = 2.0) -> bool:
    """Check if two violations overlap within a tolerance window (seconds)."""
    return (a.timestamp_start - tolerance) <= b.timestamp_end and (b.timestamp_start - tolerance) <= a.timestamp_end

def merge_and_deduplicate(
    search_violations: list[Violation],
    analyze_violations: list[Violation]
) -> list[Violation]:
    """
    Merge search (Marengo) and analyze (Pegasus) results.
    Corroborated violations (flagged by both) get upgraded confidence and reasoning.
    """
    merged: list[Violation] = []
    used_analyze: set[int] = set()

    for sv in search_violations:
        matched = False
        for i, av in enumerate(analyze_violations):
            if i in used_analyze:
                continue
            if sv.rule_id == av.rule_id and timestamps_overlap(sv, av):
                merged_violation = Violation(
                    timestamp_start=min(sv.timestamp_start, av.timestamp_start),
                    timestamp_end=max(sv.timestamp_end, av.timestamp_end),
                    confidence=max(sv.confidence, av.confidence),
                    severity=av.severity if av.severity == "critical" else sv.severity,
                    rule_id=sv.rule_id,
                    rule_text=sv.rule_text,
                    reasoning=f"[CORROBORATED] Search: {sv.reasoning} | Analysis: {av.reasoning}",
                    source="merged",
                    thumbnail_url=sv.thumbnail_url or av.thumbnail_url
                )
                merged.append(merged_violation)
                used_analyze.add(i)
                matched = True
                break
        if not matched:
            merged.append(sv)

    for i, av in enumerate(analyze_violations):
        if i not in used_analyze:
            merged.append(av)

    return merged
