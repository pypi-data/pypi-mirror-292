
import os
import incribo
import numpy as np
import tempfile


def test_embedding_streamer():
    print("\nTesting EmbeddingStreamer")

    # Create a mock embedding function
    def mock_embedding_fn(text):
        return np.random.rand(5).astype(np.float32).tolist()

    # Create EmbeddingStreamer
    streamer = incribo.EmbeddingStreamer(mock_embedding_fn)

    # Test update_embedding and get_embedding
    key = "test_key"
    data = "This is a test sentence."
    learning_rate = 0.5

    print(f"Updating embedding for key '{key}' with data '{data}'")
    update_result = streamer.update_embedding(key, data, learning_rate)
    print(f"Update result: {update_result}")

    print(f"Getting embedding for key '{key}'")
    embedding = streamer.get_embedding(key)

    print(f"Embedding for '{key}': {embedding}")

    if embedding is None:
        print("WARNING: Embedding is None. Checking if key exists in store")
        # Assuming there's a method to check if a key exists
        if hasattr(streamer, 'has_embedding'):
            exists = streamer.has_embedding(key)
            print(f"Does key '{key}' exist in the store? {exists}")

    assert embedding is not None, "Embedding should not be None"
    assert isinstance(embedding, dict), "Embedding should be a dictionary"
    assert "vector" in embedding, "Embedding should have a 'vector' key"
    assert len(embedding["vector"]
               ) == 5, "Embedding vector should have length 5"

    # Test stream_local_file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write("Line 1\nLine 2\nLine 3\n")
        temp_file_path = temp_file.name

    try:
        print(f"Streaming from local file: {temp_file_path}")
        streamer.stream_local_file(temp_file_path)
        for i in range(1, 4):
            key = f"Line {i}"
            print(f"Getting embedding for '{key}'")
            embedding = streamer.get_embedding(key)
            print(f"Embedding for '{key}': {embedding}")
            assert embedding is not None, f"Embedding for '{
                key}' should not be None"
    finally:
        os.unlink(temp_file_path)

    # Test stream_database (mock)
    connection_string = "mock_connection_string"
    query = "SELECT mock_column FROM mock_table"
    print("Initiating mock database streaming")
    streamer.stream_database(connection_string, query)
    print("Database streaming initiated (mock)")

    print("EmbeddingStreamer test completed successfully!")


if __name__ == "__main__":
    test_embedding_streamer()
