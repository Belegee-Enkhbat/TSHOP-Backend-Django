import logging
import sys
from django.db.models import Q
from django.http import HttpRequest
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated

import base64
from django.core.files.base import ContentFile
import uuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status


from .models import Product, Category, ProductReview
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s "
    "[%(name)s:%(funcName)s:%(lineno)s] -> %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
    stream=sys.stdout,
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


class LatestProductsList(APIView):
    def get(self, _: HttpRequest) -> Response:
        products = Product.objects.all()[0:4]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetail(APIView):

    @staticmethod
    def get_object(category_slug: str, product_slug: str) -> Product | None:
        return Product.objects.filter(category__slug=category_slug, slug=product_slug).first()

    def get(self, _: HttpRequest, category_slug: str, product_slug: str) -> Response:
        if (product := self.get_object(category_slug, product_slug)) is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"category_slug": category_slug, "product_slug": product_slug}
            )

        serializer = ProductSerializer(product)
        return Response(serializer.data)


class ReviewsList(APIView):
    @staticmethod
    def get_object(category_slug: str, product_slug: str) -> Product | None:
        return Product.objects.filter(category__slug=category_slug, slug=product_slug).first()

    def get(self, _: HttpRequest, category_slug: str, product_slug: str) -> Response:
        reviews = ProductReview.objects.select_related("product").filter(
            product__category__slug=category_slug, product__slug=product_slug
        )
        serializer = ReviewSerializer(reviews.all(), many=True)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def post(self, request: HttpRequest, category_slug: str, product_slug: str) -> Response:
        serializer = ReviewSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if (product := self.get_object(category_slug, product_slug)) is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"category_slug": category_slug, "product_slug": product_slug}
            )

        serializer.save(product=product)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetail(APIView):

    @staticmethod
    def get_object(category_slug: str) -> Category | None:
        return Category.objects.filter(slug=category_slug).first()

    def get(self, _: HttpRequest, category_slug) -> Response:
        if (category := self.get_object(category_slug)) is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={'category_slug': category_slug}
            )

        serializer = CategorySerializer(category)
        return Response(serializer.data)


@api_view(["POST"])
def search(request) -> Response:
    query = request.data.get("query", "")

    if not query:
        return Response({"products": []})

    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def postProduct(request):
    data = request.data
    thumbnail_base64 = data.get('thumbnail')
    thumbnail_data = base64.b64decode(thumbnail_base64.split(",")[1])     
    print("-----------")
    print("Received data:", data)  # Log the received data
    print("-----------")

    try:
        # давтагдахгүй нэр
        filename = f"thumbnail_{uuid.uuid4().hex}.png"
         # Create a ContentFile with the decoded data
        thumbnail_file = ContentFile(thumbnail_data, name=filename) 
        product = Product.objects.create(
            name=data["name"],
            slug=data["slug"],
            description=data["description"],
            price=data["price"],
            image=data["image"],
            thumbnail=thumbnail_file,
            category_id=data["category_id"]
        )
        return Response({"message": "Product created successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print("Error:", str(e))  # Log the error
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)