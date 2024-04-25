from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from http import HTTPMethod
from .models import Finance
from .serializers import FinanceSerializer

# Create your views here.


class FinanceViewSet(viewsets.ModelViewSet):
    queryset = Finance.objects.all().order_by("year")
    serializer_class = FinanceSerializer

    @action(detail=False, methods=[HTTPMethod.GET])
    def list(self, request):
        year = request.GET.get("year")
        queryset = self.get_queryset()
        if year:
            queryset = queryset.filter(year=int(year))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

