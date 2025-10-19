import os
import sys
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)

def test_connection():
    """Test the database connection and basic operations."""
    print("Testing PostgreSQL connection...")
    
    # Test connection
    conn = get_db_connection()
    print("✅ Successfully connected to PostgreSQL")
    
    # Test if pgvector extension is enabled
    with conn.cursor() as cur:
        cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
        result = cur.fetchone()
        if result:
            print(f"✅ pgvector extension is enabled (version: {result[1]})")
        else:
            print("❌ pgvector extension is not enabled")
            return False
    
    # Test if tables were created
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'audio_embeddings';
        """)
        if cur.fetchone():
            print("✅ audio_embeddings table exists")
        else:
            print("❌ audio_embeddings table does not exist")
            return False
    
    # Test vector operations
    try:
        # Generate a random embedding for testing
        test_embedding = np.random.rand(1536).astype(np.float32).tolist()
        
        with conn.cursor() as cur:
            # Insert a test record
            cur.execute("""
                INSERT INTO audio_embeddings 
                (file_path, file_hash, file_size, duration, embedding)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                "test/path/to/audio.wav",
                "testhash123",
                1024,
                180.5,
                test_embedding
            ))
            record_id = cur.fetchone()[0]
            conn.commit()
            print(f"✅ Successfully inserted test record with ID: {record_id}")
            
            # Test similarity search
            cur.execute("""
                SELECT id, file_path, 
                       1 - (embedding <=> %s) as similarity
                FROM audio_embeddings
                ORDER BY embedding <=> %s
                LIMIT 1;
            """, (test_embedding, test_embedding))
            
            result = cur.fetchone()
            if result:
                print(f"✅ Similarity search works. Best match: {result[1]} (similarity: {result[2]:.4f})")
            
            # Clean up
            cur.execute("DELETE FROM audio_embeddings WHERE id = %s", (record_id,))
            conn.commit()
            
    except Exception as e:
        print(f"❌ Error testing vector operations: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    if test_connection():
        print("\n✅ All PostgreSQL tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)
