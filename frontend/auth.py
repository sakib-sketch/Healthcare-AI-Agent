import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Force reload of database package to clear out old SQLite caching from active Streamlit memory
if 'database' in sys.modules:
    import importlib
    if 'database.db' in sys.modules:
        import database.db
        importlib.reload(database.db)
    import database
    importlib.reload(database)

import bcrypt
import psycopg2
from email_validator import validate_email, EmailNotValidError
from database import get_connection

# =========================
# HASH PASSWORD
# =========================
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# =========================
# VERIFY PASSWORD
# =========================
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# =========================
# REGISTER USER
# =========================
def register_user(name, email, password):

    try:
        validate_email(email)
    except EmailNotValidError:
        return False, "Invalid email address"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        hashed = hash_password(password)

        cursor.execute("""
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """, (name, email, hashed))

        conn.commit()

        return True, "Registration successful"

    except psycopg2.IntegrityError:
        return False, "Email already exists"

    finally:
        conn.close()

# =========================
# LOGIN USER
# =========================
def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM users WHERE email=%s
    """, (email,))

    user = cursor.fetchone()

    if user:
        stored_password = user[3]

        if verify_password(password, stored_password):
            # Record login status and timestamp in Neon
            cursor.execute("""
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP, is_logged_in = TRUE 
            WHERE id = %s
            """, (user[0],))
            conn.commit()
            
            # Fetch updated user record with new column state
            cursor.execute("SELECT * FROM users WHERE id=%s", (user[0],))
            user = cursor.fetchone()
            conn.close()
            return True, user

    conn.close()
    return False, "Invalid email or password"

# =========================
# RESET PASSWORD
# =========================
def reset_password(email, new_password):

    conn = get_connection()
    cursor = conn.cursor()

    hashed = hash_password(new_password)

    cursor.execute("""
    UPDATE users
    SET password=%s
    WHERE email=%s
    """, (hashed, email))

    conn.commit()

    updated = cursor.rowcount

    conn.close()

    if updated:
        return True, "Password updated successfully"

    return False, "Email not found"

# =========================
# LOGOUT USER (DATABASE)
# =========================
def logout_user(user_id):
    """
    Updates the database with the user's logout time and clears active session state.
    """
    if not user_id:
        return False

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users 
        SET last_logout = CURRENT_TIMESTAMP, is_logged_in = FALSE 
        WHERE id = %s
        """, (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating logout in database: {e}")
        return False
    finally:
        conn.close()