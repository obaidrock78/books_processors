import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the index and book IDs
index = faiss.read_index('book_index.faiss')
book_ids = np.load('book_ids.npy')
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
#
def recommend_books(favorite_book_description):
    favorite_embedding = model.encode([favorite_book_description])
    D, I = index.search(favorite_embedding, 5)
    recommended_ids = [book_ids[i] for i in I[0]]
    return recommended_ids