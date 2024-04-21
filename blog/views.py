import http

from django.http import HttpRequest
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Article
from .serializers import ArticleSerializer


class LatestArticles(APIView):
    def get(self, _: HttpRequest) -> Response:
        articles = Article.objects.all()[0:3]
        serializer = ArticleSerializer(articles, many=True, context={"request": None})
        return Response(serializer.data)


class ArticlesList(APIView):
    def get(self, _: HttpRequest) -> Response:
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class ArticleDetail(APIView):
    @staticmethod
    def get_object(article_slug: str) -> Article | None:
        return Article.objects.filter(slug=article_slug).first()

    def get(self, _: HttpRequest, article_slug) -> Response:
        if (article := self.get_object(article_slug)) is None:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"slug": article_slug})

        serializer = ArticleSerializer(article)
        return Response(serializer.data)
