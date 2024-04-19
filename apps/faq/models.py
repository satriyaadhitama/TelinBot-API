from django.db import models


# Create your models here.
class FrequentlyAskedQuestion(models.Model):
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=2000)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
