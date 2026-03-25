from services.db_service import get_connection

def get_upload_records():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    uf.file_id,
                    uf.file_name,
                    uf.dataset_type,
                    su.username AS uploaded_by,
                    uf.row_count,
                    DATE_FORMAT(uf.upload_time, '%Y-%m-%d %H:%i:%s') AS upload_time,
                    uf.status,
                    uf.remarks
                FROM upload_files uf
                JOIN system_users su ON uf.upload_user_id = su.user_id
                ORDER BY uf.upload_time DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()
# from services.db_service import get_connection

# def get_upload_records():
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                 SELECT
#                     uf.file_id,
#                     uf.file_name,
#                     uf.dataset_type,
#                     su.username AS uploaded_by,
#                     uf.row_count,
#                     DATE_FORMAT(uf.upload_time, '%%Y-%%m-%%d %%H:%%i') AS upload_time,
#                     uf.status,
#                     uf.remarks
#                 FROM upload_files uf
#                 JOIN system_users su ON uf.upload_user_id = su.user_id
#                 ORDER BY uf.upload_time DESC
#             """
#             cursor.execute(sql)
#             return cursor.fetchall()
#     finally:
#         conn.close()