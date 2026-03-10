import bcrypt
from database import get_connection

# Role level mapping
role_level = {"staff": 1, "manager": 2, "admin": 3}


def create_user(username: str, password: str, role: str):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if admin already exists
    if role == "admin":
        cursor.execute("SELECT COUNT(*) AS cnt FROM system_users WHERE role='admin'")
        if cursor.fetchone()["cnt"] > 0:
            return {"error": "Admin already exists"}

    # Check if username already exists
    cursor.execute("SELECT * FROM system_users WHERE username=%s", (username,))
    if cursor.fetchone():
        return {"error": "Username already exists"}

    # Hash the password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Insert user
    cursor.execute(
        "INSERT INTO system_users (username, password_hash, role) VALUES (%s, %s, %s)",
        (username, password_hash, role)
    )
    conn.commit()
    return {"message": f"User '{username}' created successfully with role '{role}'"}


def login(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM system_users WHERE username=%s", (username,))
    user = cursor.fetchone()
    if not user:
        return {"error": "Username not found"}

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return {"error": "Wrong password"}

    return {"message": f"Login successful", "username": user["username"], "role": user["role"]}


def get_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, role, created_at FROM system_users")
    return cursor.fetchall()


def delete_user(requester_username: str, requester_password: str, target_username: str):
    """
    Delete a user.
    Rules:
      - Admin can delete anyone (including self)
      - Manager can delete staff and self
      - Staff can delete only self
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get the requester
    cursor.execute("SELECT * FROM system_users WHERE username=%s", (requester_username,))
    requester = cursor.fetchone()
    if not requester:
        return {"error": "Requester not found"}

    # Verify password
    if not bcrypt.checkpw(requester_password.encode(), requester["password_hash"].encode()):
        return {"error": "Wrong password"}

    # Get the target user
    cursor.execute("SELECT * FROM system_users WHERE username=%s", (target_username,))
    target = cursor.fetchone()
    if not target:
        return {"error": "Target user not found"}

    # Permission check
    requester_level = role_level[requester["role"]]
    target_level = role_level[target["role"]]

    # Staff can only delete themselves
    if requester_level == 1 and requester["username"] != target["username"]:
        return {"error": "Staff can only delete themselves"}

    # Manager can only delete users with lower roles or themselves
    if requester_level == 2 and target_level > requester_level:
        return {"error": "Manager cannot delete users with same or higher role"}

    # Admin can delete anyone without restriction

    cursor.execute("DELETE FROM system_users WHERE username=%s", (target_username,))
    conn.commit()
    return {"message": f"User '{target_username}' deleted successfully"}


def change_password(requester_username: str, requester_password: str, target_username: str, new_password: str):
    """
    Change password.
    Rules:
      - Admin can change own and any lower-level user's password
      - Manager can change own and staff password
      - Staff can change only own password
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get the requester
    cursor.execute("SELECT * FROM system_users WHERE username=%s", (requester_username,))
    requester = cursor.fetchone()
    if not requester:
        return {"error": "Requester not found"}

    # Verify password
    if not bcrypt.checkpw(requester_password.encode(), requester["password_hash"].encode()):
        return {"error": "Wrong password"}

    # Get the target user
    cursor.execute("SELECT * FROM system_users WHERE username=%s", (target_username,))
    target = cursor.fetchone()
    if not target:
        return {"error": "Target user not found"}

    requester_level = role_level[requester["role"]]
    target_level = role_level[target["role"]]

    # Permission check
    if requester_level < target_level:
        return {"error": "Not enough permission to change this user's password"}

    # Update password
    new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cursor.execute(
        "UPDATE system_users SET password_hash=%s WHERE username=%s",
        (new_hash, target_username)
    )
    conn.commit()
    return {"message": f"Password for '{target_username}' changed successfully"}