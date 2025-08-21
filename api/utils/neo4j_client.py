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

    def read_tx(self, fn, *args, **kwargs):
        """Execute a read transaction with a callback(tx, *args, **kwargs). Returns callback result."""
        with self._driver.session(default_access_mode="READ") as session:
            return session.execute_read(fn, *args, **kwargs)

    def write_tx(self, fn, *args, **kwargs):
        """Execute a write transaction with a callback(tx, *args, **kwargs). Returns callback result."""
        with self._driver.session(default_access_mode="WRITE") as session:
            return session.execute_write(fn, *args, **kwargs)

    def run_queries_atomic(self, queries: list[tuple[str, dict | None]]):
        """Run multiple Cypher statements atomically in a single write transaction.
        queries: list of (query, parameters)
        Returns list of list of records for each query.
        """
        def _runner(tx):
            results = []
            for q, p in queries:
                res = tx.run(q, (p or {}))
                results.append(list(res))
            return results
        with self._driver.session(default_access_mode="WRITE") as session:
            return session.execute_write(_runner)


def get_client() -> Neo4jClient:
    cfg = get_config()
    return Neo4jClient(cfg.NEO4J_URI, cfg.NEO4J_USER, cfg.NEO4J_PASSWORD)
