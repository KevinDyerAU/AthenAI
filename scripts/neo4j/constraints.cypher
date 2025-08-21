// Node key/uniqueness constraints
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT agent_id_unique IF NOT EXISTS
FOR (n:Agent)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT task_id_unique IF NOT EXISTS
FOR (n:Task)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (n:User)
REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT event_id_unique IF NOT EXISTS
FOR (n:Event)
REQUIRE n.id IS UNIQUE;

// Property existence constraints (Neo4j 5+)
CREATE CONSTRAINT entity_id_exists IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.id IS NOT NULL;

CREATE CONSTRAINT agent_id_exists IF NOT EXISTS
FOR (n:Agent)
REQUIRE n.id IS NOT NULL;

CREATE CONSTRAINT task_id_exists IF NOT EXISTS
FOR (n:Task)
REQUIRE n.id IS NOT NULL;

CREATE CONSTRAINT user_id_exists IF NOT EXISTS
FOR (n:User)
REQUIRE n.id IS NOT NULL;

CREATE CONSTRAINT event_id_exists IF NOT EXISTS
FOR (n:Event)
REQUIRE n.id IS NOT NULL;
