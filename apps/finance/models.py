from django.db import models


# Create your models here.
class Finance(models.Model):
    Q_CHOICES = (
        (1, "Q1"),
        (2, "Q2"),
        (3, "Q3"),
        (4, "Q4"),
    )

    year = models.IntegerField()
    q = models.IntegerField(choices=Q_CHOICES)
    file = models.FileField(null=True, upload_to="documents/finance/")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
