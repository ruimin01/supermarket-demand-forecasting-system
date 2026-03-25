import pymysql
from config import Config

def get_connection():
    timeout = 10

    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=timeout,
        read_timeout=timeout,
        write_timeout=timeout,
        autocommit=True,
    )
# 1st
# import pymysql
# from config import Config

# def get_connection():
#     return pymysql.connect(
#         host=Config.DB_HOST,
#         port=Config.DB_PORT,
#         user=Config.DB_USER,
#         password=Config.DB_PASSWORD,
#         database=Config.DB_NAME,
#         cursorclass=pymysql.cursors.DictCursor,
#         autocommit=True
#     )