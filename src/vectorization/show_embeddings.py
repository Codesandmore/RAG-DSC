import numpy as np

# Load the saved embeddings
embeddings = np.load("sentence_embeddings.npy")

# Print full embeddings
np.set_printoptions(threshold=np.inf)  # Ensure full output
print(embeddings)
