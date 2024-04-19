from rest_framework import serializers
from .models import FrequentlyAskedQuestion


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentlyAskedQuestion
        fields = ["id", "question", "answer", "is_active"]
