import pymysql
import os
from dotenv import load_dotenv  # 用 python-dotenv 加载 .env 文件

# 加载 .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CA_PATH = os.path.join(BASE_DIR, "ca.pem")  # 确保 ca.pem 在 backend/ 目录下

def get_connection():
    """
    每次调用都返回新的连接
    """
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl={
            "ca": CA_PATH,          # Aiven 提供的 CA
            "check_hostname": False # 开发阶段可以先关闭 hostname 检查
        },
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection