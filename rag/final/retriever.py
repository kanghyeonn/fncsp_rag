import psycopg
from typing import List, Dict
from rag.config import POSTGRES_CONN

SQL_TEMPLATE = """
WITH q AS (SELECT %s::vector AS qv)
SELECT
  section,
  content,
  (1 - (embedding <=> q.qv)) AS similarity
FROM business_plan_embeddings, q
WHERE (metadata->>'doc_type') = 'business_plan'
  AND (metadata->>'company')  = %s
  AND section = ANY(%s)
ORDER BY embedding <=> q.qv
LIMIT %s;
"""

def retrieve_context(
    query_vec: list,
    company: str,
    sections: List[str],
    k: int = 10
) -> List[Dict]:

    with psycopg.connect(POSTGRES_CONN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                SQL_TEMPLATE,
                (query_vec, company, sections, k)
            )
            rows = cur.fetchall()

    return [
        {
            "section": r[0],
            "content": r[1],
            "similarity": round(r[2], 4)
        }
        for r in rows
    ]
