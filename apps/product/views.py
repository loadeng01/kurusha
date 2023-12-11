from rest_framework.decorators import action
from rest_framework import permissions, generics
from .models import Product
from .serializers import ProductSerializer
from apps.account.permissions import IsAdmin, IsActive
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from apps.favorite.models import Favorite
from django.contrib.auth import get_user_model
from ..account.serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

User = get_user_model()


class Pagination(PageNumberPagination):
    page_size = 8
    page_query_param = 'page'


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    pagination_class = Pagination
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('title', )
    filterset_fields = ('category',)

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE', 'POST'):
            return IsAdmin(),
            # return permissions.AllowAny(),
        return permissions.AllowAny(),

    @action(['POST', 'DELETE', 'GET'], detail=True)
    def favorites(self, request, pk):
        product = self.get_object()
        user = request.user

        if request.method == 'POST':
            if user.favorites.filter(product=product).exists():
                return Response('This post is already in favorites', status=400)
            Favorite.objects.create(product=product, owner=user)
            return Response('Added to favorites', status=201)

        elif request.method == 'GET':
            users = product.favorites.all().values('owner')
            favorites_users = User.objects.filter(id__in=users)
            serializer = UserSerializer(favorites_users, many=True)
            count = len(serializer.data)
            return Response({"count": count}, status=200)

        else:
            favorite = user.favorites.filter(product=product)
            if favorite.exists():
                favorite.delete()
                return Response('Deleted from favorites', status=204)
            return Response('Post not found', status=404)


class UserFavoritesListView(APIView):
    permission_classes = permissions.IsAuthenticated,

    def get(self, request):
        user = request.user
        favorites = Favorite.objects.filter(owner=user)
        data = []
        for item in favorites:
            serializer = ProductSerializer(item.product)
            data.append(serializer.data)

        return Response(data, status=200)


class UserFavoritesDetailView(generics.RetrieveDestroyAPIView):
    queryset = Product.objects.all()
    permission_class = IsActive,
    lookup_field = 'id'
    serializer_class = ProductSerializer

    def get_permissions(self):
        return IsActive(),

    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        user = request.user

        favorite = user.favorites.filter(product=product)
        if favorite.exists():
            favorite.delete()
            return Response('Deleted from favorites', status=204)
        return Response('Post not found', status=404)


