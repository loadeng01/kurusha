from django.contrib import admin
from django.urls import path, include
from apps.category.views import CategoryViewSet
from apps.product.views import *
from rest_framework.routers import SimpleRouter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from django.conf.urls.static import static
from django.conf import settings
from apps.account import views

schema_view = get_schema_view(
   openapi.Info(
      title="KURULTAI API",
      default_version='v1',
   ),
   public=True,
)

router = SimpleRouter()
router.register('category', CategoryViewSet)
router.register('product', ProductViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', schema_view.with_ui('swagger')),
    path('api/account/', include('apps.account.urls')),
    path('api/', include(router.urls)),
    path('api/favorite_products/', UserFavoritesListView.as_view()),
    path('api/favorite_products/<int:id>/', UserFavoritesDetailView.as_view()),

]

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
