from elasticsearch import Elasticsearch

def get_es_conn(es_config: dict) -> Elasticsearch | None:
    """
    ES_CONFIG를 기반으로 Elasticsearch 연결을 생성한다.
    연결 실패 시 None 반환
    """
    try:
        es = Elasticsearch(
            hosts=es_config["hosts"],
            http_auth=es_config["http_auth"],
            max_retries=es_config["max_retries"],
            retry_on_timeout=es_config["retry_on_timeout"]
        )

        # 연결 확인 (권장)
        if not es.ping():
            return None

        return es

    except Exception:
        return None