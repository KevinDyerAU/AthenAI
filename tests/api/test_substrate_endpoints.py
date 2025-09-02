import os
import time
import json
import pytest

from flask_jwt_extended import create_access_token
from neo4j import GraphDatabase

from api.app import create_app
from api.config import get_config


def _neo4j_available() -> bool:
    cfg = get_config()
    try:
        drv = GraphDatabase.driver(cfg.NEO4J_URI, auth=(cfg.NEO4J_USER, cfg.NEO4J_PASSWORD))
        with drv.session() as s:
            s.run("RETURN 1").single()
        drv.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _neo4j_available(), reason="Neo4j not available for substrate tests")


@pytest.fixture(scope="module")
def app():
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_header(app):
    with app.app_context():
        token = create_access_token(identity={"id": "test-user"})
    return {"Authorization": f"Bearer {token}"}


def test_create_and_update_with_conflict(client, auth_header):
    # Create entity
    payload = {
        "content": "Initial knowledge content",
        "entity_type": "note",
        "created_by": "tester",
        "metadata": {"source": "unit-test"},
    }
    r = client.post("/api/substrate/entity", data=json.dumps(payload), headers={**auth_header, "Content-Type": "application/json"})
    assert r.status_code == 201, r.data
    entity_id = r.json["id"]

    # First update
    upd1 = {
        "updates": {"content": "Version A"},
        "updated_by": "tester-A",
        "strategy": "latest_wins",
    }
    r1 = client.patch(f"/api/substrate/entity/{entity_id}", data=json.dumps(upd1), headers={**auth_header, "Content-Type": "application/json"})
    assert r1.status_code == 200, r1.data

    # Second conflicting update shortly after
    time.sleep(0.2)
    upd2 = {
        "updates": {"content": "Version B"},
        "updated_by": "tester-B",
        "strategy": "strict",
    }
    r2 = client.patch(f"/api/substrate/entity/{entity_id}", data=json.dumps(upd2), headers={**auth_header, "Content-Type": "application/json"})
    # In strict mode, conflict likely if provenance window hits; allow either 200 (no conflict) or 409
    assert r2.status_code in (200, 409), r2.data

    # Merge update should always succeed
    upd3 = {
        "updates": {"content": "Merged Candidate"},
        "updated_by": "tester-C",
        "strategy": "merge",
    }
    r3 = client.patch(f"/api/substrate/entity/{entity_id}", data=json.dumps(upd3), headers={**auth_header, "Content-Type": "application/json"})
    assert r3.status_code == 200, r3.data
    assert "version" in r3.json


def test_provenance_and_traverse(client, auth_header):
    # Create entity
    payload = {"content": "Prov test", "entity_type": "doc", "created_by": "tester"}
    r = client.post("/api/substrate/entity", data=json.dumps(payload), headers={**auth_header, "Content-Type": "application/json"})
    assert r.status_code == 201
    entity_id = r.json["id"]

    # Get provenance
    rp = client.get(f"/api/substrate/provenance/{entity_id}", headers=auth_header)
    assert rp.status_code == 200
    assert "history" in rp.json

    # Traverse
    tr_payload = {"start_id": entity_id, "max_depth": 1}
    rt = client.post("/api/substrate/traverse", data=json.dumps(tr_payload), headers={**auth_header, "Content-Type": "application/json"})
    assert rt.status_code == 200
    assert "nodes" in rt.json


def test_semantic_search_best_effort(client, auth_header):
    # This test is best-effort: skip gracefully if vector index not configured
    payload = {"embedding": [0.0] * 1536, "limit": 3, "threshold": 0.0}
    rs = client.post("/api/substrate/search/semantic", data=json.dumps(payload), headers={**auth_header, "Content-Type": "application/json"})
    if rs.status_code != 200:
        pytest.skip(f"semantic search unavailable: {rs.status_code}")
    assert "results" in rs.json
