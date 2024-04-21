from django.urls import path, include
from products import views
from rest_framework import routers


router = routers.DefaultRouter()


urlpatterns = [
    path("latest-products/", views.LatestProductsList.as_view()),
    path("products/search/", views.search),
    path(
        "products/<slug:category_slug>/<slug:product_slug>/",
        views.ProductDetail.as_view(),
    ),
    path(
        "products/<slug:category_slug>/<slug:product_slug>/reviews/",
        views.ReviewsList.as_view(),
    ),
    path("products/<slug:category_slug>/", views.CategoryDetail.as_view()),
]
