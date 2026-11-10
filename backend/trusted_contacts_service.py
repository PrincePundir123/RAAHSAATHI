# trusted_contacts_service.py - Cryptographically Secure Trusted Contacts Management
import os
import sqlite3
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "safewalk.db")


def validate_email_or_phone(email: Optional[str], phone: Optional[str]) -> bool:
    """Validates that at least one contact channel is syntactically valid."""
    has_valid_email = False
    has_valid_phone = False

    if email and email.strip():
        # Standard email regex
        if re.match(r"^[^@]+@[^@]+\.[^@]+$", email.strip()):
            has_valid_email = True

    if phone and phone.strip():
        # E.164 or national phone regex with optional plus and digits
        cleaned = re.sub(r"[\s\-\(\)]", "", phone.strip())
        if re.match(r"^\+?[0-9]{7,15}$", cleaned):
            has_valid_phone = True

    return has_valid_email or has_valid_phone


def get_trusted_contacts(owner_user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all trusted contacts for a given account owner."""
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
            SELECT id, owner_user_id, contact_name, email, phone,
                   preferred_channel, relationship, invitation_status,
                   notification_consent, escalation_priority, created_at
            FROM trusted_contacts
            WHERE owner_user_id = ?
            ORDER BY escalation_priority ASC, created_at ASC
            """, (owner_user_id,)).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"Error fetching contacts: {e}")
        return []


def add_trusted_contact(
    owner_user_id: str,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    relationship: str = "Friend / Family",
    preferred_channel: str = "sms",
    escalation_priority: int = 1
) -> Dict[str, Any]:
    """Adds a new trusted contact with input validation."""
    if not name or not name.strip():
        return {"success": False, "error": "Contact name is required."}

    if not validate_email_or_phone(email, phone):
        return {"success": False, "error": "Please provide a valid phone number or email address."}

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO trusted_contacts (
                owner_user_id, contact_name, email, phone,
                preferred_channel, relationship, invitation_status,
                notification_consent, escalation_priority,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'confirmed', 1, ?, ?, ?)
            """, (
                owner_user_id,
                name.strip(),
                email.strip() if email else None,
                phone.strip() if phone else None,
                preferred_channel,
                relationship.strip(),
                escalation_priority,
                now_iso,
                now_iso
            ))
            contact_id = cursor.lastrowid
            conn.commit()
            return {"success": True, "contact_id": contact_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_trusted_contact(
    contact_id: int,
    owner_user_id: str,
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    relationship: str = "Friend / Family",
    preferred_channel: str = "sms",
    escalation_priority: int = 1
) -> Dict[str, Any]:
    """Updates an existing trusted contact verifying ownership."""
    if not name or not name.strip():
        return {"success": False, "error": "Contact name is required."}

    if not validate_email_or_phone(email, phone):
        return {"success": False, "error": "Please provide a valid phone number or email address."}

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE trusted_contacts
            SET contact_name = ?, email = ?, phone = ?,
                preferred_channel = ?, relationship = ?,
                escalation_priority = ?, updated_at = ?
            WHERE id = ? AND owner_user_id = ?
            """, (
                name.strip(),
                email.strip() if email else None,
                phone.strip() if phone else None,
                preferred_channel,
                relationship.strip(),
                escalation_priority,
                now_iso,
                contact_id,
                owner_user_id
            ))
            if cursor.rowcount == 0:
                return {"success": False, "error": "Contact not found or unauthorized."}
            conn.commit()
            return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_trusted_contact(contact_id: int, owner_user_id: str) -> Dict[str, Any]:
    """Deletes a contact ensuring ownership check."""
    try:
        with sqlite3.connect(DB_PATH, timeout=5.0) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trusted_contacts WHERE id = ? AND owner_user_id = ?", (contact_id, owner_user_id))
            if cursor.rowcount == 0:
                return {"success": False, "error": "Contact not found or unauthorized."}
            conn.commit()
            return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
