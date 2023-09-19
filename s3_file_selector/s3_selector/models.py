from django.db import models

class S3Object(models.Model):
    file = models.FileField(upload_to='ultrasond_images/')
    # metadata = models.JSONField(blank=True, null=True)