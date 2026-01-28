from dotenv import load_dotenv
import os

load_dotenv()

ES_CONFIG = {
    "hosts": os.getenv("PROD_ELASTICSEARCH_HOST"),            # 예: http://localhost
    "port": int(os.getenv("PROD_ELASTICSEARCH_PORT", 9200)),  # 기본 9200
    "http_auth": (
        os.getenv("PROD_ELASTICSEARCH_ID"),
        os.getenv("PROD_ELASTICSEARCH_PASSWORD"),
    ),
    "timeout": int(os.getenv("PROD_ELASTICSEARCH_TIMEOUT", 30)),
    "max_retries": int(os.getenv("PROD_ELASTICSEARCH_MAX_RETRIES", 3)),
    "retry_on_timeout": True,
}