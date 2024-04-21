from django.db import models
from django.core.files import File
from my_shop.settings import APP_URL
from io import BytesIO
from PIL import Image


class Article(models.Model):
    title = models.CharField(max_length=400)
    article_text = models.TextField()
    slug = models.SlugField()
    author_name = models.CharField(max_length=100)
    created_at = models.DateField()
    image = models.ImageField(upload_to="uploads/blog_images/", blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to="uploads/blog_thumbnails/", blank=True, null=True
    )

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return f"/{self.slug}"

    def get_image(self) -> str:
        if self.image:
            return APP_URL + self.image.url
        return ""

    def get_thumbnail(self) -> str:
        if self.thumbnail:
            return APP_URL + self.thumbnail.url

        if self.image:
            self.thumbnail = self.make_thumbnail(self.image)
            self.save()

            return APP_URL + self.thumbnail.url

    def make_thumbnail(self, image, size=(370, 250)) -> File:
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, "PNG", quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail
