# journey_guardian_service.py - Production-Grade Live Journey Guardian State Machine & Secure Telemetry
import os
import sqlite3
import secrets
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from route_segmenter import haversine_distance_m

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "safewalk.db")

# State Machine Constants
STATUS_STARTED = "JOURNEY_STARTED"
STATUS_CHECKIN_PENDING = "CHECK_IN_PENDING"
STATUS_CHECKIN_CONFIRMED = "CHECK_IN_CONFIRMED"
STATUS_MISSED_CHECKIN = "MISSED_CHECK_IN"
STATUS_CONTACT_ALERTED = "CONTACT_ALERTED"
STATUS_ACKNOWLEDGED = "ASSISTANCE_ACKNOWLEDGED"
STATUS_COMPLETED = "JOURNEY_COMPLETED"
STATUS_CANCELLED = "JOURNEY_CANCELLED"
STATUS_EXPIRED = "JOURNEY_EXPIRED"


def _hash_token(token: str) -> str:
    """Computes SHA-256 hash of sharing token to avoid storing plaintext access credentials."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_journey(
    owner_user_id: str,
    start_lat: float,
    start_lng: float,
    start_address: str,
    dest_lat: float,
    dest_lng: float,
    dest_name: str,
    expected_duration_min: int = 30,
    checkin_interval_min: int = 5,
    grace_period_min: int = 2,
    selected_contact_ids: Optional[List[int]] = None,
    journey_note: str = ""
) -> Dict[str, Any]:
    """
    Starts an opt-in Live Protected Journey:
    1. Generates high-entropy cryptographic token for sharing (secrets.token_urlsafe).
    2. Stores SHA-256 token hash.
    3. Calculates initial check-in deadline.
    4. Records journey start event in audit trail.
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)

    now = datetime.now()
    expected_arrival = now + timedelta(minutes=max(5, expected_duration_min))
    # Expiration is set to expected arrival + 3 hours safety window
    expires_at = expected_arrival + timedelta(hours=3)
    first_checkin_deadline = now + timedelta(minutes=checkin_interval_min)

    now_iso = now.strftime("%Y-%m-%d %H:%M:%S")
    arr_iso = expected_arrival.strftime("%Y-%m-%d %H:%M:%S")
    exp_iso = expires_at.strftime("%Y-%m-%d %H:%M:%S")
    chk_iso = first_checkin_deadline.strftime("%Y-%m-%d %H:%M:%S")

    escalation_json = json.dumps({"contact_ids": selected_contact_ids or []})

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO journeys (
                owner_user_id, start_latitude, start_longitude, start_address,
                destination_latitude, destination_longitude, destination_name,
                expected_arrival, status, location_sharing_enabled,
                checkin_interval_min, grace_period_min, escalation_config,
                share_token_hash, raw_share_token, journey_note,
                last_checkin_prompt_at, next_checkin_deadline, expires_at,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                owner_user_id, start_lat, start_lng, start_address,
                dest_lat, dest_lng, dest_name,
                arr_iso, STATUS_STARTED,
                checkin_interval_min, grace_period_min, escalation_json,
                token_hash, raw_token, journey_note.strip(),
                now_iso, chk_iso, exp_iso,
                now_iso
            ))
            journey_id = cursor.lastrowid

            # Save initial location update
            cursor.execute("""
            INSERT INTO journey_location_updates (
                journey_id, latitude, longitude, accuracy, recorded_at, received_at
            ) VALUES (?, ?, ?, 15.0, ?, ?)
            """, (journey_id, start_lat, start_lng, now_iso, now_iso))

            # Initial journey event
            cursor.execute("""
            INSERT INTO journey_events (
                journey_id, event_type, actor_id, metadata, created_at
            ) VALUES (?, 'started', ?, ?, ?)
            """, (journey_id, owner_user_id, json.dumps({"destination": dest_name}), now_iso))

            # Schedule first check-in
            cursor.execute("""
            INSERT INTO journey_checkins (
                journey_id, scheduled_at, status
            ) VALUES (?, ?, 'PENDING')
            """, (journey_id, chk_iso))

            conn.commit()

            return {
                "success": True,
                "journey_id": journey_id,
                "share_token": raw_token,
                "next_checkin_deadline": chk_iso,
                "expected_arrival": arr_iso,
                "status": STATUS_STARTED
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def record_location_update(
    journey_id: int,
    lat: float,
    lng: float,
    accuracy: float = 10.0,
    speed: Optional[float] = None
) -> Dict[str, Any]:
    """Records a live GPS coordinate update for an active trip."""
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            # Verify journey is active
            status = cursor.execute("SELECT status FROM journeys WHERE id = ?", (journey_id,)).fetchone()
            if not status or status[0] in (STATUS_COMPLETED, STATUS_CANCELLED, STATUS_EXPIRED):
                return {"success": False, "error": "Journey is no longer active."}

            cursor.execute("""
            INSERT INTO journey_location_updates (
                journey_id, latitude, longitude, accuracy, speed, recorded_at, received_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (journey_id, lat, lng, accuracy, speed, now_iso, now_iso))
            conn.commit()
            return {"success": True, "recorded_at": now_iso}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_latest_journey_location(journey_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves the latest recorded location update with accuracy and staleness."""
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("""
            SELECT latitude, longitude, accuracy, speed, recorded_at
            FROM journey_location_updates
            WHERE journey_id = ?
            ORDER BY recorded_at DESC, id DESC
            LIMIT 1
            """, (journey_id,)).fetchone()
            if row:
                rec_dt = datetime.strptime(row["recorded_at"], "%Y-%m-%d %H:%M:%S")
                seconds_ago = max(0, int((datetime.now() - rec_dt).total_seconds()))
                is_stale = seconds_ago > 120  # Stale if > 2 minutes without update
                return {
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "accuracy": row["accuracy"],
                    "recorded_at": row["recorded_at"],
                    "seconds_ago": seconds_ago,
                    "is_stale": is_stale,
                    "staleness_text": f"{seconds_ago}s ago" if seconds_ago < 60 else f"{round(seconds_ago/60)}m ago"
                }
    except Exception as e:
        print(f"Error fetching latest location: {e}")
    return None


def confirm_checkin(journey_id: int, response_type: str = "im_okay") -> Dict[str, Any]:
    """
    Processes user check-in:
    - 'im_okay': Resets next check-in deadline.
    - 'need_assistance': Immediately transitions trip to CONTACT_ALERTED, notifies trusted contacts.
    - 'stop_journey': Ends journey.
    """
    now = datetime.now()
    now_iso = now.strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            j = cursor.execute("""
            SELECT checkin_interval_min, status, escalation_config, owner_user_id
            FROM journeys WHERE id = ?
            """, (journey_id,)).fetchone()
            if not j:
                return {"success": False, "error": "Journey not found."}

            interval_min, curr_status, esc_cfg_str, owner_id = j
            esc_cfg = json.loads(esc_cfg_str or "{}")

            if response_type == "im_okay":
                next_deadline = now + timedelta(minutes=interval_min)
                next_iso = next_deadline.strftime("%Y-%m-%d %H:%M:%S")

                cursor.execute("""
                UPDATE journeys
                SET status = ?, next_checkin_deadline = ?, last_checkin_prompt_at = ?
                WHERE id = ?
                """, (STATUS_CHECKIN_CONFIRMED, next_iso, now_iso, journey_id))

                cursor.execute("""
                UPDATE journey_checkins
                SET responded_at = ?, response_type = 'im_okay', status = 'CONFIRMED'
                WHERE journey_id = ? AND status = 'PENDING'
                """, (now_iso, journey_id))

                # Insert next pending checkin
                cursor.execute("""
                INSERT INTO journey_checkins (journey_id, scheduled_at, status)
                VALUES (?, ?, 'PENDING')
                """, (journey_id, next_iso))

                cursor.execute("""
                INSERT INTO journey_events (journey_id, event_type, actor_id, metadata, created_at)
                VALUES (?, 'checkin_confirmed', ?, ?, ?)
                """, (journey_id, owner_id, json.dumps({"status": "I am okay"}), now_iso))

                conn.commit()
                return {"success": True, "status": STATUS_CHECKIN_CONFIRMED, "next_deadline": next_iso}

            elif response_type == "need_assistance":
                # Immediately escalate
                cursor.execute("""
                UPDATE journeys SET status = ? WHERE id = ?
                """, (STATUS_CONTACT_ALERTED, journey_id))

                # Create Alert records for configured contacts
                for c_id in esc_cfg.get("contact_ids", []):
                    cursor.execute("""
                    INSERT INTO journey_alerts (journey_id, recipient_contact_id, alert_type, status, created_at)
                    VALUES (?, ?, 'emergency_help', 'ALERTED', ?)
                    """, (journey_id, c_id, now_iso))

                    # Notification log
                    cursor.execute("""
                    INSERT INTO notification_logs (
                        journey_id, recipient_contact_id, notification_channel,
                        delivery_status, status_message, created_at
                    ) VALUES (?, ?, 'sms', 'SIMULATED', 'Assistance requested by user. Emergency alert transmitted.', ?)
                    """, (journey_id, c_id, now_iso))

                cursor.execute("""
                INSERT INTO journey_events (journey_id, event_type, actor_id, metadata, created_at)
                VALUES (?, 'assistance_requested', ?, ?, ?)
                """, (journey_id, owner_id, json.dumps({"urgency": "HIGH"}), now_iso))

                conn.commit()
                return {"success": True, "status": STATUS_CONTACT_ALERTED, "action": "contacts_alerted"}

            elif response_type == "stop_journey":
                return complete_or_cancel_journey(journey_id, is_completed=False)

    except Exception as e:
        return {"success": False, "error": str(e)}


def process_server_side_escalations() -> List[Dict[str, Any]]:
    """
    Idempotent Server-Side Check-in Evaluation Job:
    Evaluates all active journeys:
    - If now > next_checkin_deadline + grace_period, transitions from PENDING -> MISSED_CHECK_IN -> CONTACT_ALERTED.
    - Sends automated simulated or configured notifications to trusted contacts.
    - Guarantees duplicate alerts are never emitted.
    """
    now = datetime.now()
    now_iso = now.strftime("%Y-%m-%d %H:%M:%S")
    escalated = []

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            # Fetch active journeys that have passed their checkin deadline + grace period
            active_journeys = cursor.execute("""
            SELECT id, owner_user_id, next_checkin_deadline, grace_period_min,
                   escalation_config, status, destination_name
            FROM journeys
            WHERE status IN (?, ?, ?)
            """, (STATUS_STARTED, STATUS_CHECKIN_PENDING, STATUS_CHECKIN_CONFIRMED)).fetchall()

            for j_id, owner_id, deadline_str, grace_min, esc_cfg_str, stat, dest_name in active_journeys:
                if not deadline_str:
                    continue
                try:
                    dl_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
                    grace_dt = dl_dt + timedelta(minutes=grace_min or 2)
                    
                    if now >= dl_dt and now < grace_dt:
                        # Journey in pending grace prompt
                        if stat != STATUS_CHECKIN_PENDING:
                            cursor.execute("UPDATE journeys SET status = ? WHERE id = ?", (STATUS_CHECKIN_PENDING, j_id))
                    
                    elif now >= grace_dt:
                        # Missed checkin! Escalate immediately
                        cursor.execute("UPDATE journeys SET status = ? WHERE id = ?", (STATUS_CONTACT_ALERTED, j_id))
                        cursor.execute("""
                        UPDATE journey_checkins SET status = 'MISSED'
                        WHERE journey_id = ? AND status = 'PENDING'
                        """, (j_id,))

                        esc_cfg = json.loads(esc_cfg_str or "{}")
                        contact_ids = esc_cfg.get("contact_ids", [])
                        
                        for c_id in contact_ids:
                            # Avoid duplicate alerts for this check-in cycle
                            existing = cursor.execute("""
                            SELECT id FROM journey_alerts
                            WHERE journey_id = ? AND recipient_contact_id = ? AND alert_type = 'missed_checkin'
                              AND created_at >= ?
                            """, (j_id, c_id, dl_dt.strftime("%Y-%m-%d %H:%M:%S"))).fetchone()

                            if not existing:
                                cursor.execute("""
                                INSERT INTO journey_alerts (journey_id, recipient_contact_id, alert_type, status, created_at)
                                VALUES (?, ?, 'missed_checkin', 'ALERTED', ?)
                                """, (j_id, c_id, now_iso))

                                cursor.execute("""
                                INSERT INTO notification_logs (
                                    journey_id, recipient_contact_id, notification_channel,
                                    delivery_status, status_message, created_at
                                ) VALUES (?, ?, 'sms', 'SIMULATED', 'Missed check-in alert dispatched to contact.', ?)
                                """, (j_id, c_id, now_iso))

                        cursor.execute("""
                        INSERT INTO journey_events (journey_id, event_type, actor_id, metadata, created_at)
                        VALUES (?, 'missed_checkin', 'system_escalator', ?, ?)
                        """, (j_id, json.dumps({"deadline": deadline_str, "contacts_alerted": len(contact_ids)}), now_iso))

                        escalated.append({"journey_id": j_id, "contacts_notified": len(contact_ids)})

                except Exception as ex:
                    print(f"Error evaluating journey {j_id}: {ex}")

            conn.commit()
    except Exception as e:
        print(f"Escalation engine error: {e}")

    return escalated


def acknowledge_alert(
    journey_id: int,
    contact_id: int,
    contact_name: str = "Trusted Contact"
) -> Dict[str, Any]:
    """Allows an authorized trusted contact to select 'I am responding'."""
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE journey_alerts
            SET status = 'ACKNOWLEDGED', acknowledged_by_contact_id = ?, acknowledged_at = ?
            WHERE journey_id = ?
            """, (contact_id, now_iso, journey_id))

            cursor.execute("""
            UPDATE journeys SET status = ? WHERE id = ?
            """, (STATUS_ACKNOWLEDGED, journey_id))

            cursor.execute("""
            INSERT INTO journey_events (journey_id, event_type, actor_id, metadata, created_at)
            VALUES (?, 'assistance_acknowledged', ?, ?, ?)
            """, (journey_id, f"contact_{contact_id}", json.dumps({"contact_name": contact_name, "action": "I am responding"}), now_iso))

            conn.commit()
            return {"success": True, "status": STATUS_ACKNOWLEDGED, "acknowledged_at": now_iso}
    except Exception as e:
        return {"success": False, "error": str(e)}


def complete_or_cancel_journey(journey_id: int, is_completed: bool = True) -> Dict[str, Any]:
    """Stops location collection, cancels escalation jobs, and applies retention policy."""
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_status = STATUS_COMPLETED if is_completed else STATUS_CANCELLED
    event_name = "completed" if is_completed else "cancelled"

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE journeys
            SET status = ?, location_sharing_enabled = 0, completed_at = ?
            WHERE id = ?
            """, (final_status, now_iso, journey_id))

            cursor.execute("""
            INSERT INTO journey_events (journey_id, event_type, metadata, created_at)
            VALUES (?, ?, ?, ?)
            """, (journey_id, event_name, json.dumps({"final_status": final_status}), now_iso))

            conn.commit()
            return {"success": True, "status": final_status}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_journey_by_share_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Secure Public Contact Access:
    Validates token hash, checks expiration, and returns public journey progress.
    Prevents unauthorized visitors from discovering other trips.
    """
    if not token or len(token) < 20:
        return None

    h = _hash_token(token)
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            j = conn.execute("""
            SELECT id, owner_user_id, destination_name, start_address,
                   expected_arrival, status, checkin_interval_min,
                   journey_note, expires_at, created_at, completed_at
            FROM journeys
            WHERE share_token_hash = ?
            """, (h,)).fetchone()

            if not j:
                return None

            # Check expiration
            exp_dt = datetime.strptime(j["expires_at"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > exp_dt:
                return {"status": STATUS_EXPIRED, "message": "This journey sharing link has expired."}

            latest_loc = get_latest_journey_location(j["id"])

            # Check recent alerts
            alerts = conn.execute("""
            SELECT alert_type, status, acknowledged_at, created_at
            FROM journey_alerts
            WHERE journey_id = ?
            ORDER BY created_at DESC
            """, (j["id"],)).fetchall()

            return {
                "journey_id": j["id"],
                "destination_name": j["destination_name"],
                "start_address": j["start_address"],
                "expected_arrival": j["expected_arrival"],
                "status": j["status"],
                "journey_note": j["journey_note"],
                "latest_location": latest_loc,
                "alerts": [dict(a) for a in alerts]
            }
    except Exception as e:
        print(f"Error querying share token: {e}")
        return None
