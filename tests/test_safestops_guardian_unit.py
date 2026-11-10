import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
for d in [BASE_DIR, BACKEND_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

from safestops_service import find_nearby_safestops, add_community_safestop, get_safestop_by_id
from trusted_contacts_service import add_trusted_contact, get_trusted_contacts, delete_trusted_contact
from journey_guardian_service import (
    create_journey,
    record_location_update,
    confirm_checkin,
    process_server_side_escalations,
    acknowledge_alert,
    complete_or_cancel_journey,
    get_journey_by_share_token,
    get_latest_journey_location,
    STATUS_STARTED,
    STATUS_CHECKIN_CONFIRMED,
    STATUS_CONTACT_ALERTED,
    STATUS_COMPLETED
)


def test_safestops_search_and_filtering():
    # Test nearby assistance lookup
    stops = find_nearby_safestops(30.4158, 77.9659, radius_km=5.0)
    assert len(stops) > 0
    first = stops[0]
    assert "name" in first
    assert "category" in first
    assert "distance_m" in first
    assert "verification_status" in first
    assert first["verification_status"] in ["PUBLIC FACILITY", "COMMUNITY-LISTED", "PARTNER-VERIFIED"]

    # Filter by police category
    police_stops = find_nearby_safestops(30.3375, 77.9602, radius_km=10.0, category_filter="police")
    assert all(s["category"] == "police" for s in police_stops)


def test_community_safestop_addition():
    res = add_community_safestop(
        name="Test 24/7 Store",
        category="community_help",
        lat=30.3300,
        lng=78.0300,
        address="Test Road"
    )
    assert res["success"] is True
    assert res["status"] == "COMMUNITY-LISTED"


def test_trusted_contacts_lifecycle():
    user_id = "test_user_unit_99"
    # Add
    c_res = add_trusted_contact(
        owner_user_id=user_id,
        name="Emergency Contact",
        phone="+919876543211",
        relationship="Sister"
    )
    assert c_res["success"] is True
    contact_id = c_res["contact_id"]

    # Retrieve
    contacts = get_trusted_contacts(user_id)
    assert len(contacts) == 1
    assert contacts[0]["contact_name"] == "Emergency Contact"

    # Delete
    del_res = delete_trusted_contact(contact_id, user_id)
    assert del_res["success"] is True
    assert len(get_trusted_contacts(user_id)) == 0


def test_journey_guardian_state_machine():
    user_id = "test_walker_101"
    # 1. Create Journey
    j_res = create_journey(
        owner_user_id=user_id,
        start_lat=30.3243,
        start_lng=78.0419,
        start_address="Start Point",
        dest_lat=30.4158,
        dest_lng=77.9659,
        dest_name="Campus Hostel",
        expected_duration_min=30,
        checkin_interval_min=5
    )
    assert j_res["success"] is True
    j_id = j_res["journey_id"]
    token = j_res["share_token"]

    # 2. Public Token Query
    public_view = get_journey_by_share_token(token)
    assert public_view is not None
    assert public_view["destination_name"] == "Campus Hostel"
    assert public_view["status"] == STATUS_STARTED

    # 3. Location update
    loc_res = record_location_update(j_id, 30.3300, 78.0400, accuracy=5.0)
    assert loc_res["success"] is True
    latest = get_latest_journey_location(j_id)
    assert latest is not None
    assert latest["accuracy"] == 5.0

    # 4. Check-in Confirmation
    chk_res = confirm_checkin(j_id, "im_okay")
    assert chk_res["success"] is True
    assert chk_res["status"] == STATUS_CHECKIN_CONFIRMED

    # 5. Assistance Escalation
    need_res = confirm_checkin(j_id, "need_assistance")
    assert need_res["success"] is True
    assert need_res["status"] == STATUS_CONTACT_ALERTED

    # 6. Acknowledgement by Contact
    ack_res = acknowledge_alert(j_id, contact_id=1, contact_name="Sister")
    assert ack_res["success"] is True

    # 7. Complete Journey
    comp_res = complete_or_cancel_journey(j_id, is_completed=True)
    assert comp_res["success"] is True
    assert comp_res["status"] == STATUS_COMPLETED
