import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# 1. MySQL 접속 정보
# =========================
MYSQL_CONFIG = {
    "host": os.getenv("PROD_MYSQL_HOST"),
    "user": os.getenv("PROD_MYSQL_USERNAME"),
    "password": os.getenv("PROD_MYSQL_PASSWORD"),
    "database": os.getenv("PROD_MYSQL_DATABASE"),
    "charset": "utf8mb4",
    "autocommit": False,
}