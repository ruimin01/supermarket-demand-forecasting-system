from werkzeug.security import generate_password_hash
from services.db_service import get_connection

def get_all_users():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT user_id, username, email, role, is_active,
                       can_upload, can_predict, can_export,
                       can_view_all_records, can_manage_users,
                       can_view_upload_records
                FROM system_users
                ORDER BY role DESC, username ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def update_user_permissions(user_id, permissions):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE system_users
                SET can_upload=%s,
                    can_predict=%s,
                    can_export=%s,
                    can_view_all_records=%s,
                    can_view_upload_records=%s,
                    is_active=%s
                WHERE user_id=%s AND role='staff'
            """
            cursor.execute(sql, (
                permissions["can_upload"],
                permissions["can_predict"],
                permissions["can_export"],
                permissions["can_view_all_records"],
                permissions["can_view_upload_records"],
                permissions["is_active"],
                user_id
            ))
            return cursor.rowcount > 0
    finally:
        conn.close()

def create_staff_account(username, email, password, is_active=True):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            check_sql = "SELECT user_id FROM system_users WHERE username = %s LIMIT 1"
            cursor.execute(check_sql, (username,))
            existing = cursor.fetchone()

            if existing:
                return {"error": "username already exists"}

            password_hash = generate_password_hash(password)

            insert_sql = """
                INSERT INTO system_users (
                    username,
                    password_hash,
                    email,
                    role,
                    is_active,
                    can_upload,
                    can_predict,
                    can_export,
                    can_view_all_records,
                    can_manage_users,
                    can_view_upload_records
                ) VALUES (
                    %s, %s, %s, 'staff', %s,
                    TRUE, TRUE, FALSE, FALSE, FALSE, FALSE
                )
            """
            cursor.execute(insert_sql, (
                username,
                password_hash,
                email,
                is_active
            ))

            return {
                "username": username,
                "email": email,
                "role": "staff",
                "is_active": bool(is_active)
            }
    finally:
        conn.close()
# from services.db_service import get_connection

# def get_all_users():
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                 SELECT user_id, username, email, role, is_active,
#                        can_upload, can_predict, can_export,
#                        can_view_all_records, can_manage_users
#                 FROM system_users
#                 ORDER BY role DESC, username ASC
#             """
#             cursor.execute(sql)
#             return cursor.fetchall()
#     finally:
#         conn.close()

# def update_user_permissions(user_id, permissions):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                 UPDATE system_users
#                 SET can_upload=%s,
#                     can_predict=%s,
#                     can_export=%s,
#                     can_view_all_records=%s,
#                     is_active=%s
#                 WHERE user_id=%s AND role='staff'
#             """
#             cursor.execute(sql, (
#                 permissions["can_upload"],
#                 permissions["can_predict"],
#                 permissions["can_export"],
#                 permissions["can_view_all_records"],
#                 permissions["is_active"],
#                 user_id
#             ))
#             return cursor.rowcount > 0
#     finally:
#         conn.close()