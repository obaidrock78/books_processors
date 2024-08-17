from django.core.management.base import BaseCommand
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from multiprocessing import Pool, cpu_count
from apis.models import Book
import cProfile
import pstats

def encode_in_batches(descriptions, model, batch_size=1000):
    encoded = []
    print("encoding")
    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i:i + batch_size]
        embeddings = model.encode(batch, convert_to_numpy=True)
        encoded.append(embeddings)
        print("embeddings", embeddings)
    return np.vstack(encoded)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            batch_size = 10000
            num_workers = cpu_count()
            print(f"Number of workers: {num_workers}", flush=True)
            pool = Pool(num_workers)

            books_iterator = Book.objects.all().values('id', 'description').iterator(chunk_size=batch_size)
            print("Book fetching", flush=True)

            index = None
            all_book_ids = []

            for i, book_batch in enumerate(self._batch(books_iterator, batch_size)):
                descriptions = [book['description'] for book in book_batch]

                # Profile the encoding process
                profiler = cProfile.Profile()
                profiler.enable()

                # Use smaller batches for encoding
                embeddings = encode_in_batches(descriptions, model, batch_size=1000)

                profiler.disable()
                stats = pstats.Stats(profiler).sort_stats(pstats.SortKey.TIME)
                print(f"Profiling stats for batch {i}:")
                stats.print_stats()

                if index is None:
                    dimension = embeddings.shape[1]
                    index = faiss.IndexFlatL2(dimension)
                    faiss.omp_set_num_threads(num_workers)

                index.add(embeddings)
                print(f"Batch {i} added to index", flush=True)

                # Accumulate book IDs in memory
                all_book_ids.extend([book['id'] for book in book_batch])

            pool.close()
            pool.join()

            # Save all book IDs and FAISS index
            np.save('book_ids.npy', all_book_ids)
            faiss.write_index(index, 'book_index.faiss')
            print("Indexing complete", flush=True)
        except Exception as e:
            print(f"An error occurred: {e}", flush=True)

    def _batch(self, iterator, batch_size):
        batch = []
        for item in iterator:
            batch.append(item)
            if len(batch) == batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
