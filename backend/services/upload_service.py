from services.db_service import get_connection

def save_upload_record(file_name, dataset_type, upload_user_id, row_count=0, status="completed", remarks=None, file_path=None):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO upload_files (
                    file_name,
                    dataset_type,
                    upload_user_id,
                    row_count,
                    file_path,
                    status,
                    remarks
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                file_name,
                dataset_type,
                upload_user_id,
                row_count,
                file_path,
                status,
                remarks
            ))
            return cursor.lastrowid
    finally:
        conn.close()





        
# from services.db_service import get_connection

# def save_upload_record(file_name, dataset_type, upload_user_id, row_count=0, status="completed", remarks=None, file_path=None):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cursor:
#             sql = """
#                 INSERT INTO upload_files (
#                     file_name,
#                     dataset_type,
#                     upload_user_id,
#                     row_count,
#                     file_path,
#                     status,
#                     remarks
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s)
#             """
#             cursor.execute(sql, (
#                 file_name,
#                 dataset_type,
#                 upload_user_id,
#                 row_count,
#                 file_path,
#                 status,
#                 remarks
#             ))
#             return cursor.lastrowid
#     finally:
#         conn.close()