from django.urls import path
from blog import views

urlpatterns = [
    path("articles/", views.ArticlesList.as_view()),
    path("latest-articles/", views.LatestArticles.as_view()),
    path("articles/<slug:article_slug>/", views.ArticleDetail.as_view()),
]
