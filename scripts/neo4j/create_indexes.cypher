// Full-text index for Entities (fallback search)
CALL db.index.fulltext.createNodeIndex('entityIndex', ['Entity'], ['id', 'name', 'description']) YIELD name
RETURN name;

// Vector index for Entity embeddings (enable after you store n.embedding as a float[])
CREATE VECTOR INDEX entityEmbedding IF NOT EXISTS
FOR (n:Entity) ON (n.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'
  }
};
