from django.db import models
from image_cropping import ImageCropField, ImageRatioField


class Image(models.Model):
    title = models.CharField(max_length=200)
    image = ImageCropField(upload_to='images/')
    cropping = ImageRatioField('images/', '430x360')

    def __str__(self):
        return self.title
