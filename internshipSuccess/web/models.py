from django.db import models

# Create your models here.


def newsletter_img_directory_path(instance, filename):
    return "newsletters/{0}/{1}".format(instance.title, filename)
class NewsLetters(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    image = models.FileField(
        blank=True, null=True, upload_to=newsletter_img_directory_path
    )

