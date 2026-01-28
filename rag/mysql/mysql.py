import pymysql
import datetime
from rag.mysql.config import MYSQL_CONFIG
from typing import List, Dict

# =========================
# DB연결 함수
# =========================
def get_db_conn(db_config: dict):
    """
    DB_CONFIG 기반 MySQL 커넥션 생성
    """
    return pymysql.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
        charset=db_config.get("charset", "utf8mb4"),
        autocommit=db_config.get("autocommit", False),
        cursorclass=pymysql.cursors.DictCursor
    )

# =========================
# CMP_LIST 회사명 조회
# =========================
def fetch_cmp_list(db_config: dict, biz_no: str):
    """
    cmp_list 테이블 조회
    """
    conn = get_db_conn(db_config)

    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT CMP_NM
                FROM cmp_list
                WHERE BIZ_NO = %s
                LIMIT 1
            """
            cursor.execute(sql, (biz_no,))
            return cursor.fetchall()

    finally:
        conn.close()