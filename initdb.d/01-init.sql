-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for audio embeddings
CREATE TABLE IF NOT EXISTS audio_embeddings (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    file_hash TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    duration FLOAT,
    sample_rate INT,
    channels INT,
    format TEXT,
    embedding VECTOR(1536),  -- Adjust dimensions based on your model
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster search
CREATE INDEX IF NOT EXISTS idx_audio_embeddings_file_hash ON audio_embeddings(file_hash);
CREATE INDEX IF NOT EXISTS idx_audio_embeddings_embedding ON audio_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update updated_at
CREATE TRIGGER update_audio_embeddings_updated_at
BEFORE UPDATE ON audio_embeddings
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create a function for similarity search
CREATE OR REPLACE FUNCTION find_similar_embeddings(
    query_embedding VECTOR(1536),
    similarity_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id INT,
    file_path TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ae.id,
        ae.file_path,
        1 - (ae.embedding <=> query_embedding) AS similarity
    FROM 
        audio_embeddings ae
    WHERE 
        1 - (ae.embedding <=> query_embedding) > similarity_threshold
    ORDER BY 
        ae.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
