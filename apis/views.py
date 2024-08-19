from django.db.models import Q, Count
from rest_framework import status
from rest_framework.generics import DestroyAPIView

from apis.models import User, Author
from apis.serializers import UserSignupSerializer, UserLoginSerializer, AuthorSerializer
from common.response_mixins import BaseAPIView
from rest_framework.viewsets import ModelViewSet

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.utils import recommend_books
from .models import Book, Favorite
from .serializers import BookSerializer, FavoriteSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination


class DefaultPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class BooksAPIViewSet(BaseAPIView, ModelViewSet):
    serializer_class = BookSerializer
    pagination_class = None  # Disable pagination for this view

    def get_permissions(self):
        if self.request.method in ['GET']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        search_query = self.request.query_params.get('search', None)
        queryset = Book.objects.all()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(authors__name__icontains=search_query)
            )
        return queryset[:5]  # Limit to 5 results

class BookDeleteAPIView(BaseAPIView, DestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        book_id = self.kwargs.get('pk')
        try:
            book = self.get_queryset().get(id=book_id)
            book.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

class AuthorAPIViewSet(BaseAPIView, ModelViewSet):
    serializer_class = AuthorSerializer
    pagination_class = None  # Disable pagination for this view

    def get_permissions(self):
        if self.request.method in ['GET']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        search_query = self.request.query_params.get('search', None)
        queryset = Author.objects.all()

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
            )
        return queryset[:5]  # Limit to 5 results


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

    def create(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')
        if not book_id:
            return Response({"error": "Book ID is required."}, status=400)

        if Favorite.objects.filter(user=user).count() >= 20:
            return Response({"error": "Max of 20 favorite books allowed."}, status=400)

        favorite, created = Favorite.objects.get_or_create(user=user, book_id=book_id)
        recommendations = recommend_books(favorite.book.description)
        book_list = Book.objects.filter(id__in=recommendations)
        serializer = self.get_serializer(favorite)
        return Response({
            "favorite": serializer.data,
            "recommendations": BookSerializer(book_list, many=True).data
        })
