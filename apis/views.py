from datetime import datetime

import random

from annoy import AnnoyIndex
from django.core.management import call_command
from django.db.models import Q, Count
from django.db import connection
from rest_framework.permissions import IsAuthenticated

from apis.models import Book, User, Author
from apis.serializers import BookSerializer, UserSignupSerializer, UserLoginSerializer, AuthorSerializer
from common.response_mixins import BaseAPIView
from rest_framework.viewsets import ModelViewSet

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Book, Favorite
from .serializers import BookSerializer, FavoriteSerializer


class BooksAPIViewSet(BaseAPIView, ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__name__icontains=search_query)
            )
        return queryset


class AuthorAPIViewSet(BaseAPIView, ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]


class UserSignUpView(BaseAPIView, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=False):
                serializer.save()
                return self.send_success_response(
                    message="User signed up successfully.",
                    data=serializer.data,
                )
            return self.send_bad_request_response(
                message=serializer.errors,
            )
        except Exception as e:
            return self.send_bad_request_response(
                message=e.args[0],
            )


class UserLoginView(BaseAPIView, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=False):
                return self.send_success_response(
                    message="User logged in successfully.",
                    data=serializer.data,
                )
            return self.send_bad_request_response(
                message=serializer.errors,
            )
        except Exception as e:
            return self.send_bad_request_response(
                message=e.args[0])


class FavoriteBooksAPIViewSet(ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

        book = favorite.book
        if not book.embedding:
            call_command('generate_embeddings')

        recommendations = self.get_recommendations(book)
        serializer = self.get_serializer(favorite)
        return Response({
            "favorite": serializer.data,
            "recommendations": BookSerializer(recommendations, many=True).data
        })

    def create(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({"error": "Book ID is required."}, status=400)

        if Favorite.objects.filter(user=user).count() >= 20:
            return Response({"error": "Max of 20 favorite books allowed."}, status=400)

        favorite, created = Favorite.objects.get_or_create(user=user, book_id=book_id)
        # if not created:
        # favorite, created = Favorite.objects.get_or_create(user=user, book_id=book_id)
        # favorite=Favorite.objects.get(id=1)
        #     return Response({"error": "Book is already in your favorites."}, status=400)

        # Generate embeddings if they don't exist
        book = favorite.book
        if not book.embedding:
            call_command('importembbed')

        recommendations = self.get_recommendations(book)
        serializer = self.get_serializer(favorite)
        return Response({
            "favorite": serializer.data,
            "recommendations": BookSerializer(recommendations, many=True).data
        })

    def get_recommendations(self, book, top_k=5):
        """
        Get recommendations for a given book based on content similarity.
        """
        # Load book embedding
        book = Book.objects.get(id=book.id)
        if not book.embedding:
            return []

        # Initialize ANN index
        f = len(book.embedding)
        t = AnnoyIndex(f, 'angular')

        # Add all book embeddings to the ANN index
        for b in Book.objects.exclude(id=book.id).values('id', 'embedding'):
            t.add_item(int(b['id']), b['embedding'])
        t.build(10)


        # Find nearest neighbors using ANN
        similar_ids = t.get_nns_by_vector(book.embedding, top_k)

        # Fetch recommended books from the database
        recommendations = Book.objects.filter(id__in=similar_ids)

        return recommendations