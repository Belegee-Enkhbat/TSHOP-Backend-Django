from django.db import models
from django.core.files import File
from django.contrib.auth.models import User
from my_shop.settings import APP_URL

from io import BytesIO
from PIL import Image


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    thumbnail = models.ImageField(upload_to="uploads/", blank=True, null=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/{self.slug}"

    def get_thumbnail(self) -> str:
        print("get thumb")
        if self.thumbnail:
            print("url, ",  self.thumbnail.url)
            return APP_URL + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                print("url, ",  APP_URL + self.thumbnail.url)

                return APP_URL + self.thumbnail.url



    def make_thumbnail(self, image, size=(300, 200)) -> File:
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "PNG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
    
class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="uploads/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="uploads/", blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-date_added",)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return f"/{self.category.slug}/{self.slug}"

    def get_image(self) -> str:
        if self.image:
            return APP_URL + self.image.url

    def get_thumbnail(self) -> str:
        print("get thumb product")
        if self.thumbnail:
            return APP_URL + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return APP_URL + self.thumbnail.url

    def make_thumbnail(self, image, size=(300, 200)) -> File:
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "PNG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    stars = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)


class ProductBrand(models.Model):
    cName = models.CharField(max_length=255)
    strDescription = models.TextField(blank=True, null=True)
    imgLogo = models.ImageField(upload_to="uploads/", blank=True, null=True)
    dateAdded = models.DateTimeField(auto_now_add=True)
    iRating = models.IntegerField()

