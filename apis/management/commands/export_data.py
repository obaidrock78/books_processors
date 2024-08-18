import os
from django.core.management.base import BaseCommand
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from multiprocessing import Pool, cpu_count
from apis.models import Book
import cProfile
import pstats

CHECKPOINT_PATH = 'checkpoint.npy'
INDEX_PATH = 'book_index.faiss'
BOOK_IDS_PATH = 'book_ids.npy'

def encode_in_batches(descriptions, model, batch_size=1000):
    encoded = []
    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i:i + batch_size]
        embeddings = model.encode(batch, convert_to_numpy=True)
        encoded.append(embeddings)
    return np.vstack(encoded)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            print("Execution started...")
            model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            batch_size = 10000
            num_workers = cpu_count()
            print(f"Number of workers: {num_workers}")
            pool = Pool(num_workers)

            books_iterator = Book.objects.all().values('id', 'description').iterator(chunk_size=batch_size)
            current_index = 0

            if os.path.exists(CHECKPOINT_PATH):
                checkpoint = np.load(CHECKPOINT_PATH, allow_pickle=True).item()
                start_batch = checkpoint['batch_index']
                all_book_ids = checkpoint['book_ids']
                index = faiss.read_index(INDEX_PATH)
                print(f"Resuming from batch {start_batch}...")
            else:
                start_batch = 0
                all_book_ids = []
                index = None
                print("Starting from scratch...")

            total_batches = 0

            for i, book_batch in enumerate(self._batch(books_iterator, batch_size)):
                current_index += 1
                total_batches += 1
                if i < start_batch:
                    continue  # Skip already processed batches

                descriptions = [book['description'] for book in book_batch]

                print(f"Processing batch {i + 1}...")

                profiler = cProfile.Profile()
                profiler.enable()

                embeddings = encode_in_batches(descriptions, model, batch_size=1000)

                profiler.disable()
                stats = pstats.Stats(profiler).sort_stats(pstats.SortKey.TIME)
                stats.print_stats()

                if index is None:
                    dimension = embeddings.shape[1]
                    index = faiss.IndexFlatL2(dimension)
                    faiss.omp_set_num_threads(num_workers)
                    print("FAISS index created...")

                index.add(embeddings)

                # Accumulate book IDs in memory
                all_book_ids.extend([book['id'] for book in book_batch])

                # Save checkpoint and book IDs after each batch
                checkpoint = {'batch_index': i + 1, 'book_ids': all_book_ids}
                np.save(CHECKPOINT_PATH, checkpoint)
                np.save(BOOK_IDS_PATH, all_book_ids)
                faiss.write_index(index, INDEX_PATH)

                print(f"Batch {i + 1} processed and added to the FAISS index...")

            pool.close()
            pool.join()

            # Save FAISS index and remove checkpoint file
            faiss.write_index(index, INDEX_PATH)
            os.remove(CHECKPOINT_PATH)
            print(f"Execution completed with {total_batches} total batches.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def _batch(self, iterator, batch_size):
        batch = []
        for item in iterator:
            batch.append(item)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch