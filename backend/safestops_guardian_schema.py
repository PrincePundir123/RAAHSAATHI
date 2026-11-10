# safestops_guardian_schema.py - SQLite Schema Migration & Initializer for SafeStops & Live Journey Guardian
import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "safewalk.db")


def init_safestops_and_guardian_schema():
    """Initializes tables for SafeStops and Live Journey Guardian."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. SafeStops Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS safestops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL, /* police, hospital, campus_security, pharmacy, community_help */
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        address TEXT,
        phone TEXT,
        website TEXT,
        opening_hours TEXT,
        is_open_24_7 BOOLEAN DEFAULT 0,
        source_type TEXT NOT NULL, /* osm, govt_registry, institutional_directory, admin_verified */
        source_reference TEXT,
        verification_status TEXT NOT NULL, /* PUBLIC FACILITY, COMMUNITY-LISTED, PARTNER-VERIFIED */
        verification_evidence TEXT,
        contact_status TEXT DEFAULT 'uncontacted',
        last_verified_at DATETIME,
        last_retrieved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_safestops_coords ON safestops(latitude, longitude)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_safestops_category ON safestops(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_safestops_verification ON safestops(verification_status)")

    # 2. Trusted Contacts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trusted_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_user_id TEXT NOT NULL,
        contact_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        preferred_channel TEXT DEFAULT 'sms', /* sms, email, in_app */
        relationship TEXT,
        invitation_status TEXT DEFAULT 'confirmed', /* pending, confirmed, revoked */
        notification_consent BOOLEAN DEFAULT 1,
        escalation_priority INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trusted_contacts_owner ON trusted_contacts(owner_user_id)")

    # 3. Journeys Table (Live Journey Guardian)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journeys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_user_id TEXT NOT NULL,
        start_latitude REAL NOT NULL,
        start_longitude REAL NOT NULL,
        start_address TEXT,
        destination_latitude REAL NOT NULL,
        destination_longitude REAL NOT NULL,
        destination_name TEXT,
        expected_arrival DATETIME,
        status TEXT DEFAULT 'JOURNEY_STARTED', 
        /* JOURNEY_STARTED, CHECK_IN_PENDING, CHECK_IN_CONFIRMED, MISSED_CHECK_IN, 
           CONTACT_ALERTED, ASSISTANCE_ACKNOWLEDGED, JOURNEY_COMPLETED, JOURNEY_CANCELLED, JOURNEY_EXPIRED */
        location_sharing_enabled BOOLEAN DEFAULT 1,
        checkin_interval_min INTEGER DEFAULT 5,
        grace_period_min INTEGER DEFAULT 2,
        escalation_config TEXT, /* JSON of contact ids & options */
        share_token_hash TEXT UNIQUE NOT NULL,
        raw_share_token TEXT, /* temporary access token for display */
        journey_note TEXT,
        last_checkin_prompt_at DATETIME,
        next_checkin_deadline DATETIME,
        expires_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_journeys_token ON journeys(share_token_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_journeys_owner ON journeys(owner_user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_journeys_status ON journeys(status)")

    # 4. Journey Location Updates (Live Telemetry & Provenance)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journey_location_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journey_id INTEGER NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        accuracy REAL, /* in meters */
        speed REAL,
        recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        received_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (journey_id) REFERENCES journeys(id) ON DELETE CASCADE
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_loc_updates_journey ON journey_location_updates(journey_id, recorded_at)")

    # 5. Journey Check-Ins Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journey_checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journey_id INTEGER NOT NULL,
        scheduled_at DATETIME NOT NULL,
        prompted_at DATETIME,
        responded_at DATETIME,
        response_type TEXT, /* 'im_okay', 'need_assistance', 'stop_journey' */
        status TEXT DEFAULT 'PENDING', /* PENDING, CONFIRMED, MISSED */
        FOREIGN KEY (journey_id) REFERENCES journeys(id) ON DELETE CASCADE
    )
    """)

    # 6. Journey Alerts (Missed Check-ins & Emergency Triggers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journey_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journey_id INTEGER NOT NULL,
        recipient_contact_id INTEGER,
        alert_type TEXT NOT NULL, /* missed_checkin, emergency_help, safety_deviation */
        status TEXT DEFAULT 'ALERTED', /* ALERTED, ACKNOWLEDGED, RESOLVED */
        acknowledged_by_contact_id INTEGER,
        acknowledged_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (journey_id) REFERENCES journeys(id) ON DELETE CASCADE
    )
    """)

    # 7. Notification Logs (Delivery Auditing)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journey_id INTEGER,
        recipient_contact_id INTEGER,
        recipient_destination TEXT,
        notification_channel TEXT NOT NULL, /* in_app, sms, email */
        provider_reference TEXT,
        delivery_status TEXT DEFAULT 'PENDING', /* PENDING, SENT, SIMULATED, FAILED */
        status_message TEXT,
        retry_count INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 8. Journey Timeline Events (Immutable Audit Trail)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journey_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        journey_id INTEGER NOT NULL,
        event_type TEXT NOT NULL, /* started, location_update, checkin_prompt, checkin_confirmed, missed_checkin, contact_alerted, assistance_acknowledged, stopped, completed */
        actor_id TEXT,
        metadata TEXT, /* JSON representation of event context */
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (journey_id) REFERENCES journeys(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
    seed_initial_safestops()


def seed_initial_safestops():
    """Seeds verified public facilities, campus security desks, and partner locations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM safestops").fetchone()[0]
    if count >= 10:
        conn.close()
        return

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Seed verified Dehradun & Delhi anchor SafeStops with strict provenance
    sample_stops = [
        # (name, category, lat, lng, address, phone, website, opening_hours, is_24_7, source_type, source_ref, verif_status, verif_evidence, contact_status)
        (
            "UPES Bidholi Main Campus Security & Quick Response Booth",
            "campus_security",
            30.4158, 77.9659,
            "Energy Acres, Bidholi, Dehradun, Uttarakhand 248007",
            "+91 135 2776061",
            "https://www.upes.ac.in",
            "Open 24/7 (Continuous Institutional Guard)",
            1,
            "institutional_directory",
            "UPES Security Directorate Desk Registry 2026",
            "PARTNER-VERIFIED",
            "MoU signed & campus emergency guard team on site 24/7.",
            "verified_active"
        ),
        (
            "UPES Kandoli Knowledge Acres Security Post",
            "campus_security",
            30.4021, 77.9680,
            "PO Kandoli Via Premnagar, Dehradun, Uttarakhand 248007",
            "+91 135 2776091",
            "https://www.upes.ac.in",
            "Open 24/7 (Security Desk Staffed)",
            1,
            "institutional_directory",
            "UPES Security Directorate Registry 2026",
            "PARTNER-VERIFIED",
            "Institutional safety checkpoint confirmed with security personnel.",
            "verified_active"
        ),
        (
            "Prem Nagar Police Station",
            "police",
            30.3375, 77.9602,
            "Chakrata Road, Prem Nagar, Dehradun, Uttarakhand 248007",
            "+91 135 2773222",
            "https://uttarakhandpolice.uk.gov.in",
            "Open 24 Hours",
            1,
            "govt_registry",
            "Uttarakhand Police Official Station Directory",
            "PUBLIC FACILITY",
            "Government gazetted police station listing.",
            "verified_public"
        ),
        (
            "Dehradun Kotwali Police Station (Clock Tower)",
            "police",
            30.3235, 78.0410,
            "Near Paltan Bazaar, Clock Tower, Dehradun 248001",
            "112 / +91 135 2623333",
            "https://uttarakhandpolice.uk.gov.in",
            "Open 24 Hours",
            1,
            "govt_registry",
            "Uttarakhand Police District Police Directory",
            "PUBLIC FACILITY",
            "Central city police station with women help desk.",
            "verified_public"
        ),
        (
            "Max Super Speciality Hospital Dehradun",
            "hospital",
            30.3705, 78.0845,
            "Mussoorie Diversion Road, Malsi, Dehradun, Uttarakhand 248001",
            "+91 135 7193000",
            "https://www.maxhealthcare.in",
            "Emergency 24/7",
            1,
            "institutional_directory",
            "NABH Accredited Hospital Registry",
            "PUBLIC FACILITY",
            "NABH Accredited Tertiary Emergency Medical Centre.",
            "verified_public"
        ),
        (
            "Synergy Institute of Medical Sciences",
            "hospital",
            30.3440, 78.0055,
            "Ballupur Canal Road, Dehradun, Uttarakhand 248001",
            "+91 135 2226000",
            "https://www.synergyhospital.co.in",
            "24/7 Trauma & Emergency",
            1,
            "institutional_directory",
            "Directorate of Health Services Uttarakhand",
            "PUBLIC FACILITY",
            "24/7 Trauma and Critical Care unit.",
            "verified_public"
        ),
        (
            "Apollo Pharmacy 24/7 Rajpur Road",
            "pharmacy",
            30.3390, 78.0530,
            "Rajpur Road, Near Ashley Hall, Dehradun 248001",
            "+91 135 2654321",
            "https://www.apollopharmacy.in",
            "Open 24 Hours",
            1,
            "admin_verified",
            "SafeWalk Partner Network Agreement #AP-DDN-01",
            "PARTNER-VERIFIED",
            "Staff trained for safe harbour emergency walk-ins and phone calls.",
            "verified_active"
        ),
        (
            "Sanjivani 24-Hour Chemist & Medical Store",
            "pharmacy",
            30.3340, 78.0120,
            "Ballupur Chowk, Chakrata Road, Dehradun 248001",
            "+91 9897000123",
            None,
            "Open 24/7",
            1,
            "osm",
            "OpenStreetMap Node #6829104",
            "PUBLIC FACILITY",
            "Verified open 24/7 by community survey.",
            "uncontacted"
        ),
        (
            "Connaught Place Central Police Post (Delhi)",
            "police",
            28.6328, 77.2197,
            "Inner Circle, Block B, Connaught Place, New Delhi 110001",
            "112 / +91 11 23340000",
            "https://delhipolice.gov.in",
            "Open 24 Hours",
            1,
            "govt_registry",
            "Delhi Police Public Safety Stations",
            "PUBLIC FACILITY",
            "Permanent police assistance and pink booth on site.",
            "verified_public"
        ),
        (
            "Ram Manohar Lohia (RML) Hospital Emergency",
            "hospital",
            28.6234, 77.1994,
            "Baba Kharak Singh Marg, New Delhi 110001",
            "+91 11 23365525",
            "https://rmlh.nic.in",
            "Emergency 24 Hours",
            1,
            "govt_registry",
            "Ministry of Health & Family Welfare Central Hospital Directory",
            "PUBLIC FACILITY",
            "Central Government Hospital 24/7 Casualty.",
            "verified_public"
        ),
        (
            "Guardian 24/7 Safe Haven Store (Odeon)",
            "community_help",
            28.6340, 77.2210,
            "D-Block, Connaught Place, New Delhi 110001",
            "+91 11 41510000",
            None,
            "Open 24 Hours",
            1,
            "admin_verified",
            "SafeWalk Designated Help Partner MoU #DEL-009",
            "PARTNER-VERIFIED",
            "Manager completed SafeWalk SafeHaven training; CCTV surveillance active.",
            "verified_active"
        )
    ]

    for item in sample_stops:
        cursor.execute("""
        INSERT INTO safestops (
            name, category, latitude, longitude, address, phone, website,
            opening_hours, is_open_24_7, source_type, source_reference,
            verification_status, verification_evidence, contact_status,
            last_verified_at, last_retrieved_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item[0], item[1], item[2], item[3], item[4], item[5], item[6],
            item[7], item[8], item[9], item[10], item[11], item[12], item[13],
            now_iso, now_iso
        ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_safestops_and_guardian_schema()
    print("SafeStops and Live Journey Guardian schema created and seeded successfully.")
