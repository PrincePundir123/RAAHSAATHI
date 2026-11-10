# offline_sync_service.py - Feature 6: Offline & Low-Network Report Queue & Synchronizer
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "safewalk.db")


def init_offline_queue_table():
    """Initializes the offline report synchronization queue."""
    with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS offline_sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_submission_id TEXT UNIQUE NOT NULL,
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            description TEXT NOT NULL,
            severity INTEGER DEFAULT 2,
            original_language TEXT DEFAULT 'english',
            sync_status TEXT DEFAULT 'QUEUED_OFFLINE', 
            /* QUEUED_OFFLINE, SYNCING, SYNCED_SUCCESS, SYNC_FAILED */
            attempt_count INTEGER DEFAULT 0,
            queued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            synced_at DATETIME,
            error_message TEXT
        )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_offline_status ON offline_sync_queue(sync_status)")
        conn.commit()


def queue_offline_report(
    user_id: str,
    category: str,
    lat: float,
    lng: float,
    description: str,
    severity: int = 2,
    original_language: str = "english",
    client_submission_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Saves an incident report in the offline queue when internet is poor or disconnected.
    Uses idempotency keys (client_submission_id) to prevent duplicate server inserts on retry.
    """
    init_offline_queue_table()
    sub_id = client_submission_id or str(uuid.uuid4())
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO offline_sync_queue (
                client_submission_id, user_id, category, latitude, longitude,
                description, severity, original_language, sync_status, queued_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'QUEUED_OFFLINE', ?)
            """, (sub_id, user_id, category, lat, lng, description.strip(), severity, original_language, now_iso))
            conn.commit()
            return {
                "success": True,
                "client_submission_id": sub_id,
                "status": "QUEUED_OFFLINE",
                "message": "Report saved on device. Will synchronize automatically when connection is verified."
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def process_offline_sync_queue() -> Dict[str, Any]:
    """
    Synchronizes queued offline reports with the master incident table when online connectivity is restored.
    Applies idempotent checks so retry cycles never produce duplicate reports.
    """
    init_offline_queue_table()
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    synced_ids = []

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            rows = cursor.execute("""
            SELECT id, client_submission_id, user_id, category, latitude, longitude,
                   description, severity, original_language, attempt_count
            FROM offline_sync_queue
            WHERE sync_status IN ('QUEUED_OFFLINE', 'SYNC_FAILED')
            LIMIT 25
            """).fetchall()

            for r in rows:
                q_id, sub_id, u_id, cat, lat, lng, desc, sev, lang, attempts = r
                
                # Check if already inserted in incidents table
                existing = cursor.execute("""
                SELECT id FROM incidents WHERE source = ?
                """, (f"offline_client:{sub_id}",)).fetchone()

                if not existing:
                    cursor.execute("""
                    INSERT INTO incidents (
                        lat, lng, type, severity, description, timestamp,
                        source, upvotes, downvotes, verified, weight,
                        moderation_status, evidence_status, original_language
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 1.0, 'PUBLISHED', 'UNVERIFIED', ?)
                    """, (
                        lat, lng, cat, sev, desc, now_iso,
                        f"offline_client:{sub_id}", lang
                    ))

                # Update queue status
                cursor.execute("""
                UPDATE offline_sync_queue
                SET sync_status = 'SYNCED_SUCCESS', synced_at = ?, attempt_count = attempt_count + 1
                WHERE id = ?
                """, (now_iso, q_id))
                synced_ids.append(sub_id)

            conn.commit()
            return {"success": True, "synced_count": len(synced_ids), "synced_ids": synced_ids}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_queued_offline_reports(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all pending offline drafts for the current device."""
    init_offline_queue_table()
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
            SELECT client_submission_id, category, latitude, longitude,
                   description, severity, sync_status, queued_at, synced_at
            FROM offline_sync_queue
            WHERE user_id = ?
            ORDER BY queued_at DESC
            """, (user_id,)).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        return []
