from flask import Blueprint
from services.db_service import get_connection

test_bp = Blueprint("test_bp", __name__)

@test_bp.route("/test-users", methods=["GET"])
def test_users():
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, username, role
                FROM system_users
                LIMIT 5;
            """)
            result = cursor.fetchall()

        return {
            "success": True,
            "message": "Query successful",
            "data": result
        }, 200

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }, 500

    finally:
        conn.close()
# from flask import Blueprint
# from services.db_service import get_connection

# test_bp = Blueprint("test_bp", __name__)

# @test_bp.route("/test-db", methods=["GET"])
# def test_db():
#     conn = get_connection()

#     try:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT NOW() AS db_time;")
#             result = cursor.fetchone()

#         return {
#             "success": True,
#             "message": "Database connection successful",
#             "data": result
#         }, 200

#     except Exception as e:
#         return {
#             "success": False,
#             "message": str(e)
#         }, 500

#     finally:
#         conn.close()
# # from flask import Blueprint
# # from services.db_service import get_connection

# # test_bp = Blueprint("test_bp", __name__)

# # @test_bp.route("/api/test-db", methods=["GET"])
# # def test_db():
# #     conn = get_connection()

# #     try:
# #         with conn.cursor() as cursor:
# #             cursor.execute("SELECT NOW() AS current_time;")
# #             result = cursor.fetchone()

# #         return {
# #             "success": True,
# #             "message": "Database connection successful",
# #             "data": result
# #         }, 200

# #     except Exception as e:
# #         return {
# #             "success": False,
# #             "message": str(e)
# #         }, 500

# #     finally:
# #         conn.close()