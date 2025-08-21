from neo4j import GraphDatabase
from ..config import get_config


class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self._driver:
            self._driver.close()

    def run_query(self, query: str, parameters: dict | None = None):
        with self._driver.session() as session:
            return list(session.run(query, parameters or {}))


def get_client() -> Neo4jClient:
    cfg = get_config()
    return Neo4jClient(cfg.NEO4J_URI, cfg.NEO4J_USER, cfg.NEO4J_PASSWORD)
