import incribo
from sentence_transformers import SentenceTransformer
import numpy as np
import time
import threading
import pytest
import os
import tempfile


# 1. testing DynamicEmbeddingWrapper
def test_dynamic_embedding_wrapper():
    print("\nTesting DynamicEmbeddingWrapper")

    # Create an initial vector
    initial_vector = np.random.rand(10).tolist()

    print("Creating DynamicEmbeddingWrapper with initial vector")
    dynamic_emb = incribo.DynamicEmbeddingWrapper(initial_vector)

    print("Initial vector:")
    print(dynamic_emb.get_vector())

    # Create a new vector to update
    new_vector = np.random.rand(10).tolist()

    print("\nUpdating with new vector")
    dynamic_emb.update(new_vector)

    print("Updated vector:")
    print(dynamic_emb.get_vector())

    # Verify that the update worked correctly
    assert dynamic_emb.get_vector() == new_vector, (
        "Update failed: vectors do not match"
    )

    print("\nDynamicEmbeddingWrapper test passed successfully!")
    return initial_vector, new_vector

# 2. testing EmbeddingComparator


def test_embedding_comparator_with_hf_models():
    print("Loading Hugging Face models")
    model1 = SentenceTransformer('all-MiniLM-L6-v2')
    model2 = SentenceTransformer('paraphrase-MiniLM-L3-v2')

    # Random test string
    test_string = (
        "The quick brown fox jumps over the lazy dog. "
        "This sentence contains every letter of the alphabet."
    )

    print("Generating embeddings")
    embedding1 = model1.encode(test_string)
    embedding2 = model2.encode(test_string)

    # Convert to numpy arrays and flatten
    embedding1_flat = np.array(embedding1).flatten()
    embedding2_flat = np.array(embedding2).flatten()

    print(f"Embedding 1 shape: {embedding1_flat.shape}")
    print(f"Embedding 2 shape: {embedding2_flat.shape}")

    print("Creating Incribo EmbeddingComparator")
    comparator = incribo.EmbeddingComparator()

    print("Adding embeddings to comparator")
    comparator.add_embedding(incribo.Embedding(
        embedding1_flat.tolist(), "all-MiniLM-L6-v2"))
    comparator.add_embedding(incribo.Embedding(
        embedding2_flat.tolist(), "paraphrase-MiniLM-L3-v2"))

    print("Comparing embeddings")
    results = comparator.compare()
    print(f"Comparison results: {results}")

    print("Getting best model")
    best_model = comparator.get_best_model()
    print(f"Best model: {best_model}")

    assert best_model is not None, "Best model should not be None"
    assert best_model in [
        "all-MiniLM-L6-v2",
        "paraphrase-MiniLM-L3-v2"
    ], "Best model should be one of the added models"
    return results, best_model


# 3. testing HistoryTrackerWrapper
def test_history_tracker_wrapper(
    comparison_results,
    best_model,
    dynamic_emb_initial,
    dynamic_emb_updated
):
    print("\nTesting HistoryTrackerWrapper")
    max_history = 10
    tracker = incribo.HistoryTrackerWrapper(max_history)

    # Add record for cosine similarity from EmbeddingComparator test
    timestamp = time.time()
    cosine_similarity = comparison_results.get(
        'all-MiniLM-L6-v2 vs paraphrase-MiniLM-L3-v2')
    if cosine_similarity:
        tracker.add_record(timestamp, cosine_similarity)
        print(f"Added record for cosine similarity: ({
              timestamp}, {cosine_similarity})")

    # Add records for L2 norms
    for model in ['all-MiniLM-L6-v2', 'paraphrase-MiniLM-L3-v2']:
        l2_norm = comparison_results.get(f'{model} L2 Norm')
        if l2_norm:
            timestamp += 1
            tracker.add_record(timestamp, l2_norm)
            print(f"Added record for {
                  model} L2 Norm: ({timestamp}, {l2_norm})")

    # Add records from DynamicEmbeddingWrapper test
    for i, vector in enumerate([dynamic_emb_initial, dynamic_emb_updated]):
        timestamp += 1
        average_value = sum(vector) / len(vector)
        tracker.add_record(timestamp, average_value)
        print(f"Added record for DynamicEmbedding {
            'initial' if i == 0 else 'updated'}: ({timestamp},{average_value})"
        )

    # Get the history
    history = tracker.get_history()
    print("\nFinal history:")
    for record in history:
        print(record)

    assert len(history) <= max_history, f"Expected at most {
        max_history} records, but got {len(history)}"

    print("\nHistoryTrackerWrapper test passed successfully!")


# 4. testing UpdateCounterWrapper
def test_update_counter_wrapper():
    print("\nTesting UpdateCounterWrapper")

    # Create a new UpdateCounterWrapper
    counter = incribo.UpdateCounterWrapper()

    print(f"Initial count: {counter.get_count()}")

    # Increment the counter several times
    for i in range(5):
        counter.increment()
        print(f"Count after increment {i+1}: {counter.get_count()}")

    # Verify final count
    assert counter.get_count() == 5, f"Expected count to be 5, but got {
        counter.get_count()}"

    print("UpdateCounterWrapper test passed successfully!")


# 5. testing DynamicEmbeddingWrapper with UpdateCounterWrapper
def test_dynamic_embedding_with_counter():
    print("\nTesting DynamicEmbeddingWrapper with UpdateCounterWrapper")

    # Create a DynamicEmbeddingWrapper with initial vector
    initial_vector = np.random.rand(5).tolist()
    dynamic_emb = incribo.DynamicEmbeddingWrapper(initial_vector)

    # Create an UpdateCounterWrapper
    counter = incribo.UpdateCounterWrapper()

    print(f"Initial vector: {dynamic_emb.get_vector()}")
    print(f"Initial update count: {counter.get_count()}")

    # Update the embedding multiple times
    num_updates = 5
    for i in range(num_updates):
        new_vector = np.random.rand(5).tolist()
        dynamic_emb.update(new_vector)
        counter.increment()

        print(f"\nUpdate {i+1}:")
        print(f"New vector: {dynamic_emb.get_vector()}")
        print(f"Update count: {counter.get_count()}")

    # Verify final state
    assert counter.get_count() == num_updates, f"Expected {
        num_updates} updates, but got {counter.get_count()}"
    assert len(dynamic_emb.get_vector()) == 5, f"Expected vector length 5, but{
        len(dynamic_emb.get_vector())}"

    print("\nFinal state:")
    print(f"Final vector: {dynamic_emb.get_vector()}")
    print(f"Total updates: {counter.get_count()}")

    print(
        "\nDynamicEmbeddingWrapper and UpdateCounterWrapper tests passed!"
    )
    print(f"Final vector: {dynamic_emb.get_vector()}")
    print(f"Total updates: {counter.get_count()}")


# 6. testing DriftManagerWrapper
def test_drift_manager_wrapper():
    print("\nTesting DriftManagerWrapper")

    # Create initial vector and drift threshold
    initial_vector = np.random.rand(5).tolist()
    drift_threshold = 0.5

    # Create DriftManagerWrapper
    drift_manager = incribo.DriftManagerWrapper(
        initial_vector, drift_threshold)

    print(f"Original vector: {drift_manager.get_original_vector()}")
    print(f"Drift threshold: {drift_threshold}")

    # Test with a vector close to the original (small drift)
    small_drift_vector = [x + 0.1 for x in initial_vector]
    small_drift = drift_manager.check_drift(small_drift_vector)
    print(f"\nSmall drift vector: {small_drift_vector}")
    print(f"Drift detected (should be False): {small_drift}")

    # Test with a vector far from the original (large drift)
    large_drift_vector = [x + 1.0 for x in initial_vector]
    large_drift = drift_manager.check_drift(large_drift_vector)
    print(f"\nLarge drift vector: {large_drift_vector}")
    print(f"Drift detected (should be True): {large_drift}")

    # Update threshold and test again
    new_threshold = 0.2
    drift_manager.update_threshold(new_threshold)
    small_drift_with_new_threshold = drift_manager.check_drift(
        small_drift_vector)
    print(f"\nUpdated drift threshold: {new_threshold}")
    print(f"Drift detected new threshold (should be True):{
          small_drift_with_new_threshold}")

    print("\nDriftManagerWrapper test completed successfully!")

# 7. testing ConsistencyManagerWrapper


def test_consistency_manager_wrapper():
    print("\nTesting ConsistencyManagerWrapper")

    # Create initial vector
    initial_vector = np.random.rand(5).tolist()

    # Create ConsistencyManagerWrapper
    consistency_manager = incribo.ConsistencyManagerWrapper(initial_vector)

    print(f"Initial vector: {consistency_manager.get_vector()}")
    print(f"Initial version: {consistency_manager.get_version()}")

    # Function to update the vector
    def update_vector():
        new_vector = np.random.rand(5).tolist()
        new_version = consistency_manager.update(new_vector)
        print(f"Updated to version {new_version}: {new_vector}")

    # Function to read the vector
    def read_vector():
        vector = consistency_manager.get_vector()
        version = consistency_manager.get_version()
        print(f"Read version {version}: {vector}")

    # Create threads for concurrent updates and reads
    threads = []
    for _ in range(5):
        threads.append(threading.Thread(target=update_vector))
        threads.append(threading.Thread(target=read_vector))

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Final state
    final_vector = consistency_manager.get_vector()
    final_version = consistency_manager.get_version()
    print(f"\nFinal vector: {final_vector}")
    print(f"Final version: {final_version}")

    # Verify final state
    assert final_version == 5, f"Expected 5 updates, but got {final_version}"
    assert len(final_vector) == 5, f"Expected vector length 5, but got {
        len(final_vector)}"

    print("\nConsistencyManagerWrapper test completed successfully!")


# 8. testing VersionControlWrapper
def test_version_control_wrapper():
    print("\nTesting VersionControlWrapper")

    # Create initial vector
    initial_vector = np.random.rand(5).astype(np.float32).tolist()

    # Create VersionControlWrapper
    vc = incribo.VersionControlWrapper(initial_vector)

    print(f"Initial vector (version 0): {vc.get_current_vector()}")
    print(f"Version count: {vc.get_version_count()}")

    # Commit new versions
    for i in range(3):
        new_vector = np.random.rand(5).astype(np.float32).tolist()
        version = vc.commit(new_vector)
        print(f"\nCommitted new vector (version {version}): {new_vector}")
        print(f"Current vector: {vc.get_current_vector()}")
        print(f"Version count: {vc.get_version_count()}")

    # Test rollback
    rollback_version = 1
    vc.rollback(rollback_version)
    print(f"\nRolled back to version {rollback_version}")
    print(f"Current vector: {vc.get_current_vector()}")

    # Try invalid rollback
    try:
        vc.rollback(10)
        print("Error: Invalid rollback succeeded")
    except ValueError as e:
        print(f"Caught expected error for invalid rollback: {e}")

    # Final state
    print(f"\nFinal current vector: {vc.get_current_vector()}")
    print(f"Final version count: {vc.get_version_count()}")

    # Verify final state
    assert vc.get_version_count() == 4, f"Expected 4 versions, but got {
        vc.get_version_count()}"
    assert len(vc.get_current_vector()) == 5, f"Expected vector length 5, got {
        len(vc.get_current_vector())}"

    print("\nVersionControlWrapper test completed successfully!")


# 9. testing BranchManagerWrapper
def test_branch_manager_wrapper():
    print("\nTesting BranchManagerWrapper")

    # Create initial vector
    initial_vector = np.random.rand(5).astype(np.float32).tolist()

    # Create BranchManagerWrapper
    bm = incribo.BranchManagerWrapper(initial_vector)

    print(f"Initial vector (branch 0): {bm.get_active_vector()}")
    print(f"Branch count: {bm.get_branch_count()}")

    # Create new branches
    for i in range(2):
        new_vector = np.random.rand(5).astype(np.float32).tolist()
        new_branch = bm.create_branch(new_vector)
        print(f"\nCreated new branch {new_branch}: {new_vector}")
        print(f"Active vector: {bm.get_active_vector()}")
        print(f"Branch count: {bm.get_branch_count()}")

    # Switch to first branch
    bm.switch_branch(0)
    print(f"\nSwitched to branch 0")  # noqa: F541
    print(f"Active vector: {bm.get_active_vector()}")

    # Merge branches
    bm.merge_branches(0, 1)
    print(f"\nMerged branches 0 and 1")  # noqa: F541
    print(f"Active vector (merged): {bm.get_active_vector()}")
    print(f"Branch count: {bm.get_branch_count()}")

    # Try invalid branch switch
    try:
        bm.switch_branch(10)
        print("Error: Invalid branch switch succeeded")
    except ValueError as e:
        print(f"Caught expected error for invalid branch switch: {e}")

    # Try invalid branch merge
    try:
        bm.merge_branches(0, 10)
        print("Error: Invalid branch merge succeeded")
    except ValueError as e:
        print(f"Caught expected error for invalid branch merge: {e}")

    # Final state
    print(f"\nFinal active vector: {bm.get_active_vector()}")
    print(f"Final branch count: {bm.get_branch_count()}")

    # Verify final state
    assert bm.get_branch_count() == 4, f"Expected 4 branches, but got {
        bm.get_branch_count()}"
    assert len(bm.get_active_vector()) == 5, f"Expected vector length 5, got {
        len(bm.get_active_vector())}"

    print("\nBranchManagerWrapper test completed successfully!")

# 10. testing EvaluationWeights


def test_evaluation_weights():
    print("\nTesting EvaluationWeights")

    # Test default constructor
    default_weights = incribo.EvaluationWeights()
    print("Default weights:", default_weights)
    assert_weights(default_weights, 0.3, 0.4, 0.2, 0.1)

    # Test custom weights
    custom_weights = incribo.EvaluationWeights(0.25, 0.25, 0.25, 0.25)
    print("Custom weights:", custom_weights)
    assert_weights(custom_weights, 0.25, 0.25, 0.25, 0.25)

    print("EvaluationWeights tests passed successfully!")

    # Test individual weight setting
    # Ensure these weights do not exceed the sum of 1.0
    try:
        custom_weights.l2_norm_weight = 0.5
        custom_weights.cosine_similarity_weight = 0.3
        custom_weights.sparsity_weight = 0.1
        custom_weights.dimensionality_weight = 0.1
        print("Modified custom weights:", custom_weights)
        assert_weights(custom_weights, 0.5, 0.3, 0.1, 0.1)
    except ValueError as e:
        print(f"Caught ValueError during modification: {e}")

    # Test invalid weights (should sum to 1)
#  with pytest.raises(ValueError):
        # Assuming the condition to raise ValueError is that weights
        # sum must be <= 1.0
        # This should fail
#      invalid_weights = incribo.EvaluationWeights(0.6, 0.6, 0.6, 0.6)
#      print(f"Invalid weights: {invalid_weights}")


def assert_weights(weights, l2, cosine, sparsity, dimensionality):
    assert weights.l2_norm_weight == pytest.approx(
        l2), "L2 Norm weight does not match"
    assert weights.cosine_similarity_weight == pytest.approx(
        cosine), "Cosine Similarity weight does not match"
    assert weights.sparsity_weight == pytest.approx(
        sparsity), "Sparsity weight does not match"
    assert weights.dimensionality_weight == pytest.approx(
        dimensionality), "Dimensionality weight does not match"


# 11. testing EmbeddingStreamer
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
    comparison_results, best_model = test_embedding_comparator_with_hf_models()
    dynamic_emb_initial, dynamic_emb_updated = test_dynamic_embedding_wrapper()
    test_history_tracker_wrapper(
        comparison_results, best_model, dynamic_emb_initial,
        dynamic_emb_updated)
    test_update_counter_wrapper()
    test_dynamic_embedding_with_counter()
    test_drift_manager_wrapper()
    test_consistency_manager_wrapper()
    test_version_control_wrapper()
    test_branch_manager_wrapper()
    test_evaluation_weights()
    test_embedding_streamer()
