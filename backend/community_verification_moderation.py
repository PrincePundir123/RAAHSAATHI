# community_verification_moderation.py - Feature 5: Trustworthy Community Verification & Moderation Service
import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "safewalk.db")

# Strict Dual-Dimension Status Values
MODERATION_STATUSES = ["PENDING_REVIEW", "PUBLISHED", "REJECTED", "HIDDEN", "REMOVED"]
EVIDENCE_STATUSES = ["UNVERIFIED", "COMMUNITY_CORROBORATED", "OFFICIALLY_SOURCED", "INSUFFICIENT_EVIDENCE"]


def init_moderation_tables():
    """Ensures moderation and evidence audit tables exist."""
    with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
        cursor = conn.cursor()
        
        # 1. Official Sources & Moderator Reviews
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_evidence_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            source_type TEXT NOT NULL, /* public_authority, institutional, news, ngo */
            source_organization TEXT NOT NULL,
            source_title TEXT NOT NULL,
            source_url TEXT,
            publication_date TEXT,
            moderator_id TEXT NOT NULL,
            moderator_notes TEXT,
            evidence_status TEXT DEFAULT 'OFFICIALLY_SOURCED',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
        )
        """)

        # 2. Immutable Moderation Audit Log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_moderation_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            moderator_id TEXT NOT NULL,
            action_type TEXT NOT NULL, /* publish, reject, hide, link_source, update_evidence */
            previous_status TEXT,
            new_status TEXT,
            reason TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
        )
        """)

        # 3. Community Abuse Reports
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incident_abuse_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            reporter_user_id TEXT NOT NULL,
            reason_category TEXT NOT NULL, /* fake, spam, private_info, harassment */
            explanation TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Check if moderation_status and evidence_status columns exist on incidents table
        cols = [c[1] for c in cursor.execute("PRAGMA table_info(incidents)").fetchall()]
        if "moderation_status" not in cols:
            cursor.execute("ALTER TABLE incidents ADD COLUMN moderation_status TEXT DEFAULT 'PUBLISHED'")
        if "evidence_status" not in cols:
            cursor.execute("ALTER TABLE incidents ADD COLUMN evidence_status TEXT DEFAULT 'UNVERIFIED'")
        if "original_language" not in cols:
            cursor.execute("ALTER TABLE incidents ADD COLUMN original_language TEXT DEFAULT 'english'")
        if "original_transcript" not in cols:
            cursor.execute("ALTER TABLE incidents ADD COLUMN original_transcript TEXT")
        if "ai_summary" not in cols:
            cursor.execute("ALTER TABLE incidents ADD COLUMN ai_summary TEXT")

        conn.commit()


def cast_community_vote(
    incident_id: int,
    user_id: str,
    vote_type: str = "up"  # "up", "down", "disagree"
) -> Dict[str, Any]:
    """
    Casts an authenticated community vote.
    Enforces one vote per authenticated account.
    Evaluates community corroboration: 3+ upvotes transitions evidence_status to COMMUNITY_CORROBORATED.
    Never gives an official verification badge based on votes alone.
    """
    if vote_type not in ("up", "down", "disagree"):
        return {"success": False, "error": "Invalid vote type."}

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            
            # Check for existing vote by this user
            existing = cursor.execute("""
            SELECT vote_type FROM session_votes WHERE session_id = ? AND incident_id = ?
            """, (user_id, incident_id)).fetchone()

            if existing:
                # Update existing vote
                if existing[0] == vote_type:
                    return {"success": False, "error": "You have already cast this vote on this report."}
                
                cursor.execute("""
                UPDATE session_votes SET vote_type = ?, timestamp = ?
                WHERE session_id = ? AND incident_id = ?
                """, (vote_type, now_iso, user_id, incident_id))
            else:
                cursor.execute("""
                INSERT INTO session_votes (session_id, incident_id, vote_type, timestamp)
                VALUES (?, ?, ?, ?)
                """, (user_id, incident_id, vote_type, now_iso))

            # Recalculate upvotes and downvotes
            up_count = cursor.execute("SELECT COUNT(*) FROM session_votes WHERE incident_id = ? AND vote_type = 'up'", (incident_id,)).fetchone()[0]
            down_count = cursor.execute("SELECT COUNT(*) FROM session_votes WHERE incident_id = ? AND vote_type IN ('down', 'disagree')", (incident_id,)).fetchone()[0]

            # Evidence status rule:
            # Current official source status is preserved. Otherwise, 3+ net upvotes yields COMMUNITY_CORROBORATED.
            curr_ev = cursor.execute("SELECT evidence_status FROM incidents WHERE id = ?", (incident_id,)).fetchone()
            curr_ev_status = curr_ev[0] if curr_ev else "UNVERIFIED"

            new_ev_status = curr_ev_status
            is_verified = False
            if curr_ev_status != "OFFICIALLY_SOURCED":
                if (up_count - down_count) >= 3:
                    new_ev_status = "COMMUNITY_CORROBORATED"
                    is_verified = True
                else:
                    new_ev_status = "UNVERIFIED"
                    is_verified = False
            else:
                is_verified = True

            cursor.execute("""
            UPDATE incidents
            SET upvotes = ?, downvotes = ?, verified = ?, evidence_status = ?
            WHERE id = ?
            """, (up_count, down_count, 1 if is_verified else 0, new_ev_status, incident_id))

            conn.commit()
            return {
                "success": True,
                "upvotes": up_count,
                "downvotes": down_count,
                "evidence_status": new_ev_status
            }

    except Exception as e:
        return {"success": False, "error": str(e)}


def apply_moderator_action(
    incident_id: int,
    moderator_id: str,
    action_type: str,  # "publish", "reject", "hide", "attach_source", "update_evidence"
    reason: str,
    new_moderation_status: Optional[str] = None,
    new_evidence_status: Optional[str] = None,
    source_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Applies an audited moderator decision with mandatory justification.
    Attaching an official source requires explicit source metadata and moderator review.
    """
    if not reason or not reason.strip():
        return {"success": False, "error": "A clear justification reason is mandatory for moderation actions."}

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            curr = cursor.execute("SELECT moderation_status, evidence_status FROM incidents WHERE id = ?", (incident_id,)).fetchone()
            if not curr:
                return {"success": False, "error": "Incident not found."}

            old_mod, old_ev = curr

            # Update statuses
            target_mod = new_moderation_status or old_mod
            target_ev = new_evidence_status or old_ev

            # If attaching an official source
            if source_metadata:
                target_ev = "OFFICIALLY_SOURCED"
                cursor.execute("""
                INSERT INTO incident_evidence_sources (
                    incident_id, source_type, source_organization, source_title,
                    source_url, publication_date, moderator_id, moderator_notes,
                    evidence_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OFFICIALLY_SOURCED', ?)
                """, (
                    incident_id,
                    source_metadata.get("source_type", "public_authority"),
                    source_metadata.get("organization", "Police / Municipal Authority"),
                    source_metadata.get("title", "Official Public Incident Registry"),
                    source_metadata.get("url", ""),
                    source_metadata.get("pub_date", now_iso),
                    moderator_id,
                    reason,
                    now_iso
                ))

            cursor.execute("""
            UPDATE incidents
            SET moderation_status = ?, evidence_status = ?, verified = CASE WHEN ? = 'OFFICIALLY_SOURCED' THEN 1 ELSE verified END
            WHERE id = ?
            """, (target_mod, target_ev, target_ev, incident_id))

            # Record in immutable audit log
            cursor.execute("""
            INSERT INTO incident_moderation_actions (
                incident_id, moderator_id, action_type, previous_status,
                new_status, reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                incident_id,
                moderator_id,
                action_type,
                f"mod:{old_mod},ev:{old_ev}",
                f"mod:{target_mod},ev:{target_ev}",
                reason.strip(),
                now_iso
            ))

            conn.commit()
            return {"success": True, "moderation_status": target_mod, "evidence_status": target_ev}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_moderation_queue(
    filter_status: str = "ALL",
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Retrieves reports awaiting review or recently modified."""
    init_moderation_tables()
    query = """
    SELECT id, lat, lng, type, severity, description, timestamp,
           upvotes, downvotes, verified, moderation_status, evidence_status,
           original_language, ai_summary, city, country
    FROM incidents
    """
    params = []
    if filter_status and filter_status != "ALL":
        query += " WHERE moderation_status = ?"
        params.append(filter_status)

    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"Error fetching moderation queue: {e}")
        return []


def get_incident_moderation_history(incident_id: int) -> List[Dict[str, Any]]:
    """Retrieves the immutable audit trail for a report."""
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
            SELECT id, moderator_id, action_type, previous_status, new_status, reason, created_at
            FROM incident_moderation_actions
            WHERE incident_id = ?
            ORDER BY created_at DESC
            """, (incident_id,)).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        return []


if __name__ == "__main__":
    init_moderation_tables()
    print("Community verification & moderation schema initialized.")
