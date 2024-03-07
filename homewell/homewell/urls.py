"""
URL configuration for homewell project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from store.views import ProductViewSet, logout_view, UserProductRelationViewSet, UserProfileViewSet, OrderViewSet

router = SimpleRouter()

router.register(r'product', ProductViewSet)
router.register(r'product_relation', UserProductRelationViewSet),
router.register(r'user-profile', UserProfileViewSet, basename='user-profile')
router.register(r'order', OrderViewSet, basename='order')

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('', include('social_django.urls', namespace='social')),
    path('logout/', logout_view, name='logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("__debug__/", include("debug_toolbar.urls")),
    # path('create_order/', OrderCreateView.as_view(), name='create_order'),
]

urlpatterns += router.urls

# http://127.0.0.1:8000/login/google-oauth2/
