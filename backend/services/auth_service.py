from werkzeug.security import check_password_hash
from services.db_service import get_connection

def login_user(username, password):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT user_id, username, email, role, is_active,
                       can_upload, can_predict, can_export,
                       can_view_all_records, can_manage_users,
                       can_view_upload_records,
                       password_hash
                FROM system_users
                WHERE username = %s
                LIMIT 1
            """
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

            if not user:
                return None

            if not user["is_active"]:
                return {"error": "account disabled"}

            if not check_password_hash(user["password_hash"], password):
                return None

            return {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "is_active": bool(user["is_active"]),
                "permissions": {
                    "can_upload": bool(user["can_upload"]),
                    "can_predict": bool(user["can_predict"]),
                    "can_export": bool(user["can_export"]),
                    "can_view_all_records": bool(user["can_view_all_records"]),
                    "can_manage_users": bool(user["can_manage_users"]),
                    "can_view_upload_records": bool(user["can_view_upload_records"]),
                }
            }
    finally:
        conn.close()
# from services.db_service import get_connection

# def login_user(username, password):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                 SELECT user_id, username, email, role, is_active,
#                        can_upload, can_predict, can_export,
#                        can_view_all_records, can_manage_users,
#                        password_hash
#                 FROM system_users
#                 WHERE username = %s
#                 LIMIT 1
#             """
#             cursor.execute(sql, (username,))
#             user = cursor.fetchone()

#             if not user:
#                 return None

#             # TODO:
#             # 这里后面应该用 bcrypt / werkzeug 校验密码哈希
#             # 现在先简化成“只要传了密码就当成功”
#             if not password:
#                 return None

#             if not user["is_active"]:
#                 return {"error": "account disabled"}

#             return {
#                 "user_id": user["user_id"],
#                 "username": user["username"],
#                 "email": user["email"],
#                 "role": user["role"],
#                 "is_active": bool(user["is_active"]),
#                 "permissions": {
#                     "can_upload": bool(user["can_upload"]),
#                     "can_predict": bool(user["can_predict"]),
#                     "can_export": bool(user["can_export"]),
#                     "can_view_all_records": bool(user["can_view_all_records"]),
#                     "can_manage_users": bool(user["can_manage_users"]),
#                 }
#             }
#     finally:
#         conn.close()