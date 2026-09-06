import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'screening.db')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            phone           TEXT NOT NULL UNIQUE,
            password        TEXT NOT NULL,
            age             INTEGER,
            dominant_hand   TEXT,
            gender          TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_auth (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT NOT NULL UNIQUE,
            password   TEXT NOT NULL,
            role       TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            screening_id        TEXT NOT NULL,
            user_id             INTEGER NOT NULL,
            date_line           TEXT NOT NULL,
            time_line           TEXT NOT NULL,
            detected_type       TEXT NOT NULL,
            label               TEXT NOT NULL,
            confidence          REAL NOT NULL,
            age                 INTEGER,
            hand                TEXT,
            ink_pixels          REAL,
            ink_ratio           REAL,
            num_contours        REAL,
            contour_area        REAL,
            contour_perimeter   REAL,
            bounding_box_width  REAL,
            bounding_box_height REAL,
            aspect_ratio        REAL,
            centroid_x          REAL,
            centroid_y          REAL,
            extent              REAL,
            solidity            REAL,
            hidden              INTEGER DEFAULT 0,
            created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_questions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            question    TEXT NOT NULL,
            answer      TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            phone       TEXT NOT NULL,
            code        TEXT NOT NULL,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at  TIMESTAMP NOT NULL,
            attempts    INTEGER DEFAULT 0,
            verified    BOOLEAN DEFAULT 0
        )
    """)

    conn.commit()

    # Migrate existing DB 
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT")
        conn.commit()
    except Exception:
        pass 

    try:
        cursor.execute("ALTER TABLE screenings ADD COLUMN hidden INTEGER DEFAULT 0")
        conn.commit()
    except Exception:
        pass 

    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def hash_security_answer(answer: str) -> str:
    """Hash security answers for verification"""
    return hashlib.sha256(answer.lower().strip().encode()).hexdigest()

def register_user(name: str, phone: str, password: str, age: int = None,
                  dominant_hand: str = None, gender: str = None,
                  security_questions: dict = None) -> bool:
    """Returns True if registered successfully, False if phone exists."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, phone, password, age, dominant_hand, gender) VALUES (?, ?, ?, ?, ?, ?)",
            (name, phone, hash_password(password), age, dominant_hand, gender)
        )
        user_id = cursor.lastrowid

        # Save security questions
        if security_questions:
            cursor.execute("INSERT INTO security_questions (user_id, question, answer) VALUES (?, ?, ?)",
                          (user_id, security_questions["q1"], hash_security_answer(security_questions["a1"])))
            cursor.execute("INSERT INTO security_questions (user_id, question, answer) VALUES (?, ?, ?)",
                          (user_id, security_questions["q2"], hash_security_answer(security_questions["a2"])))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(phone: str, password: str):
    """Returns user dict if valid, None otherwise."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, phone FROM users WHERE phone = ? AND password = ?",
        (phone, hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "phone": row[2]}
    return None

def get_user_profile(user_id: int):
    """Returns user's age and dominant hand from registration."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT age, dominant_hand FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"age": row[0], "hand": row[1]}
    return {"age": None, "hand": None}

def get_user_by_phone(phone: str):
    """Returns user dict by phone number."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, phone FROM users WHERE phone = ?",
        (phone,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "phone": row[2]}
    return None

def get_security_questions(phone: str):
    """Returns security questions for a phone number."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question FROM security_questions WHERE user_id = (SELECT id FROM users WHERE phone = ?)",
        (phone,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "question": row[1]} for row in rows]

def verify_security_answers(phone: str, answers: dict) -> bool:
    """
    Verify security answers for password recovery.
    answers = {"a1": answer1, "a2": answer2}
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, answer FROM security_questions WHERE user_id = (SELECT id FROM users WHERE phone = ?)",
        (phone,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows or len(rows) < 2:
        return False

    correct_count = 0
    for i, (_, stored_answer) in enumerate(rows):
        answer_key = f"a{i+1}"
        if answer_key in answers and hash_security_answer(answers[answer_key]) == stored_answer:
            correct_count += 1

    return correct_count == 2

# OTP FUNCTIONS 

def generate_otp(phone: str, otp_code: str, expiration_minutes: int = 10) -> bool:
    """Store OTP code for a phone number. Expires in 10 minutes by default."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM otp_codes WHERE phone = ?", (phone,))
        expires_at = datetime.now() + timedelta(minutes=expiration_minutes)
        cursor.execute(
            "INSERT INTO otp_codes (phone, code, expires_at) VALUES (?, ?, ?)",
            (phone, hash_password(otp_code), expires_at.isoformat())
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def verify_otp(phone: str, otp_code: str, max_attempts: int = 5) -> bool:
    """Verify OTP code. Returns True if valid, False if expired/invalid/too many attempts."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, code, expires_at, attempts, verified FROM otp_codes WHERE phone = ?",
            (phone,)
        )
        row = cursor.fetchone()

        if not row:
            return False

        otp_id, stored_code, expires_at, attempts, verified = row

        if verified:
            conn.close()
            return False

        if datetime.now() > datetime.fromisoformat(expires_at):
            cursor.execute("DELETE FROM otp_codes WHERE id = ?", (otp_id,))
            conn.commit()
            conn.close()
            return False

        if attempts >= max_attempts:
            cursor.execute("DELETE FROM otp_codes WHERE id = ?", (otp_id,))
            conn.commit()
            conn.close()
            return False

        if hash_password(otp_code) == stored_code:
            cursor.execute("UPDATE otp_codes SET verified = 1 WHERE id = ?", (otp_id,))
            conn.commit()
            conn.close()
            return True
        else:
            cursor.execute("UPDATE otp_codes SET attempts = attempts + 1 WHERE id = ?", (otp_id,))
            conn.commit()
            conn.close()
            return False
    except Exception:
        conn.close()
        return False

def get_otp_attempts_remaining(phone: str, max_attempts: int = 5) -> int:
    """Returns remaining attempts for OTP verification."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT attempts FROM otp_codes WHERE phone = ? AND verified = 0",
        (phone,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return max(0, max_attempts - row[0])
    return max_attempts

def get_otp_expiration_time(phone: str) -> int:
    """Returns seconds remaining until OTP expires. Returns -1 if not found."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT expires_at FROM otp_codes WHERE phone = ? AND verified = 0",
        (phone,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        expires_at = datetime.fromisoformat(row[0])
        remaining = (expires_at - datetime.now()).total_seconds()
        return int(max(0, remaining))
    return -1

def update_phone_number(phone: str, new_phone: str) -> bool:
    """Update user's phone number after security verification."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET phone = ? WHERE phone = ?",
            (new_phone, phone)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def reset_password(phone: str, new_password: str) -> bool:
    """Reset user's password."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET password = ? WHERE phone = ?",
            (hash_password(new_password), phone)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def verify_admin(email: str, password: str):
    """Returns admin dict if valid, None otherwise."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, role FROM admin_auth WHERE email = ? AND password = ?",
        (email, hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}
    return None

def save_screening(screening_id, user_id, date_line, time_line,
                   detected_type, label, confidence, age=None, hand=None, features=None):
    conn = get_connection()
    cursor = conn.cursor()
    f = features or {}
    cursor.execute("""
        INSERT INTO screenings (
            screening_id, user_id, date_line, time_line,
            detected_type, label, confidence,
            age, hand,
            ink_pixels, ink_ratio, num_contours,
            contour_area, contour_perimeter,
            bounding_box_width, bounding_box_height,
            aspect_ratio, centroid_x, centroid_y,
            extent, solidity
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        screening_id, user_id, date_line, time_line,
        detected_type, label, confidence,
        age, hand,
        f.get("ink_pixels"),       f.get("ink_ratio"),
        f.get("num_contours"),     f.get("contour_area"),
        f.get("contour_perimeter"),
        f.get("bounding_box_width"), f.get("bounding_box_height"),
        f.get("aspect_ratio"),     f.get("centroid_x"),
        f.get("centroid_y"),       f.get("extent"),
        f.get("solidity"),
    ))
    conn.commit()
    conn.close()

def get_user_screenings(user_id: int):
    """Returns screenings visible to the user — excludes hidden (soft-deleted) records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT screening_id, date_line, time_line, detected_type, label, confidence,
               age, hand,
               ink_pixels, ink_ratio, num_contours, contour_area, contour_perimeter,
               bounding_box_width, bounding_box_height, aspect_ratio,
               centroid_x, centroid_y, extent, solidity
        FROM screenings
        WHERE user_id = ? AND (hidden IS NULL OR hidden = 0)
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_screening(screening_id: str, user_id: int):
    """Soft delete — hides from user view but keeps record for admin."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE screenings SET hidden = 1 WHERE screening_id = ? AND user_id = ?",
        (screening_id, user_id)
    )
    conn.commit()
    conn.close()

def delete_all_user_screenings(user_id: int):
    """Soft delete all — hides from user view but keeps all records for admin."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE screenings SET hidden = 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()

# ADMIN DASHBOARD FUNCTIONS 
def get_total_users_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_total_screenings_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM screenings")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_screening_results_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT label, COUNT(*) as count
        FROM screenings
        GROUP BY label
    """)
    rows = cursor.fetchall()
    conn.close()
    results = {"High Likelihood": 0, "Low Likelihood": 0}
    for label, count in rows:
        if label in results:
            results[label] = count
    return results

def get_average_user_age():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(age) FROM screenings WHERE age IS NOT NULL")
    result = cursor.fetchone()[0]
    conn.close()
    return int(result) if result else 0

def get_active_users_this_month():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM screenings
        WHERE created_at >= datetime('now', '-30 days')
    """)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_screenings_last_30_days():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM screenings
        WHERE created_at >= datetime('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_recent_screenings(limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT created_at, label, age, hand, detected_type, confidence
        FROM screenings
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"date": r[0], "result": r[1], "age": r[2], "hand": r[3], "pattern": r[4], "confidence": r[5]}
        for r in rows
    ]

def get_new_users_last_7_days():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM users
        WHERE created_at >= datetime('now', '-7 days')
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

# DEMOGRAPHIC FUNCTIONS 
def get_gender_distribution():
    """Returns gender distribution (Male / Female / Prefer not to say) from users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT gender, COUNT(*) as count
        FROM users
        WHERE gender IS NOT NULL
        GROUP BY gender
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"Gender": g, "Count": c} for g, c in rows] if rows else []

def get_dominant_hand_distribution():
    """Returns dominant hand distribution from users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT dominant_hand, COUNT(*) as count
        FROM users
        WHERE dominant_hand IS NOT NULL
        GROUP BY dominant_hand
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"Hand": h, "Count": c} for h, c in rows] if rows else []

def get_age_distribution():
    """Returns age distribution in age groups from users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            CASE 
                WHEN age < 30 THEN '18-30'
                WHEN age < 40 THEN '30-40'
                WHEN age < 50 THEN '40-50'
                WHEN age < 60 THEN '50-60'
                ELSE '60+'
            END as age_group,
            COUNT(*) as count
        FROM users
        WHERE age IS NOT NULL
        GROUP BY age_group
        ORDER BY 
            CASE age_group
                WHEN '18-30' THEN 1
                WHEN '30-40' THEN 2
                WHEN '40-50' THEN 3
                WHEN '50-60' THEN 4
                WHEN '60+' THEN 5
            END
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"Age": a, "Count": c} for a, c in rows] if rows else []