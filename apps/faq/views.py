from rest_framework import permissions, viewsets, status
from .models import FrequentlyAskedQuestion
from .serializers import FAQSerializer


# Create your views here.
class FAQViewSet(viewsets.ModelViewSet):
    queryset = FrequentlyAskedQuestion.objects.all().order_by("id")
    serializer_class = FAQSerializer
