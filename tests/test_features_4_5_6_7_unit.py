import sys
import os
import uuid

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
for d in [BASE_DIR, BACKEND_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from multilingual_voice_reporting import detect_language, extract_incident_draft, detect_duplicate_candidates
from community_verification_moderation import cast_community_vote, apply_moderator_action, get_moderation_queue
from offline_sync_service import queue_offline_report, process_offline_sync_queue, get_queued_offline_reports
from safety_intelligence_service import get_safety_intelligence_summary, get_geographic_clusters


def test_multilingual_and_hinglish_detection():
    # 1. Hindi test
    res_hi = detect_language("बस स्टैंड के पास लाइट नहीं जल रही है")
    assert res_hi["language"] == "hindi"
    assert res_hi["script"] == "devanagari"

    # 2. Hinglish test
    res_hinglish = detect_language("Bus stand ke paas light nahi jal rahi hai aur bahut andhera hai")
    assert res_hinglish["language"] == "hinglish"
    assert res_hinglish["is_hinglish"] is True

    # 3. English test
    res_en = detect_language("Streetlight is broken near the university gate.")
    assert res_en["language"] == "english"


def test_structured_incident_extraction_draft():
    draft = extract_incident_draft("Chakrata road pe do log bike se picha kar rahe the", city="Dehradun")
    assert draft["suggested_category"] == "following"
    assert draft["is_hinglish"] is True
    assert draft["user_confirmed"] is False
    assert "suggested_severity" in draft
    assert "normalized_description" in draft


def test_community_verification_and_moderation():
    # Use dynamic user id to ensure test idempotency across repeated test runs
    test_user = f"user_test_{uuid.uuid4().hex[:8]}"
    vote_res = cast_community_vote(incident_id=1, user_id=test_user, vote_type="up")
    assert vote_res["success"] is True
    assert "evidence_status" in vote_res

    # Test moderator action
    mod_res = apply_moderator_action(
        incident_id=1,
        moderator_id="admin_unit_test",
        action_type="attach_source",
        reason="Verified against police station log #402",
        source_metadata={"organization": "Dehradun City Police", "url": "https://police.uk.gov.in"}
    )
    assert mod_res["success"] is True
    assert mod_res["evidence_status"] == "OFFICIALLY_SOURCED"


def test_offline_queue_and_idempotent_sync():
    sub_id = f"test_sub_key_{uuid.uuid4().hex[:8]}"
    # 1. Queue offline
    q_res = queue_offline_report(
        user_id="user_offline_tester",
        category="poor_lighting",
        lat=30.3243,
        lng=78.0419,
        description="Offline queued test incident",
        client_submission_id=sub_id
    )
    assert q_res["success"] is True
    assert q_res["status"] == "QUEUED_OFFLINE"

    # 2. Process Sync
    sync_res = process_offline_sync_queue()
    assert sync_res["success"] is True
    assert sub_id in sync_res["synced_ids"]

    # 3. Idempotent Retry: processing again should not duplicate
    sync_retry = process_offline_sync_queue()
    assert sync_retry["success"] is True
    assert sync_retry["synced_count"] == 0


def test_safety_intelligence_aggregation():
    summary = get_safety_intelligence_summary(days=30)
    assert summary["total_reports"] >= 0
    assert "safestops_summary" in summary
    assert "infrastructure_alerts" in summary
    assert "category_counts" in summary
