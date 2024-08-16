from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer
from apis.models import Book  # Replace 'your_app' with your actual app name
import numpy as np


class Command(BaseCommand):
    help = 'Generate book embeddings and update the database.'

    def handle(self, *args, **kwargs):
        self.create_book_embeddings()

    def create_book_embeddings(self, batch_size=1000):
        """
        Generate book embeddings using a pre-trained model and update the database.
        """
        # Load pre-trained model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Get the total count of books
        total_books = Book.objects.count()
        print(f"Total books: {total_books}")

        # Generate embeddings in batches
        for i in range(0, total_books, batch_size):
            # Fetch a batch of books
            batch = Book.objects.all()[i:i + batch_size]
            descriptions = [book.description for book in batch if book.description]

            if not descriptions:
                continue

            # Generate embeddings
            embeddings = model.encode(descriptions, show_progress_bar=True)

            # Update embeddings in the database
            for book, embedding in zip(batch, embeddings):
                book.embedding = embedding.tolist()  # Convert numpy array to list
                book.save(update_fields=['embedding'])

            print(f"Processed books from {i} to {i + len(batch) - 1}")

        print("Finished generating embeddings for all books.")
