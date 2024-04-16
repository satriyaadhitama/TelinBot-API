from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth, ExtractMonth
from http import HTTPMethod


from .models import FactNewCustomerRegion, FactTopCDN, FactTopTraffic, FactTrafficCDN
from .serializers import (
    NewCustomerRegionSerializer,
    TopCDNSerializer,
    TopTrafficSerializer,
    TrafficCDNSerializer,
)


class TopTrafficViewSet(viewsets.ModelViewSet):
    queryset = FactTopTraffic.objects.all().order_by("date")
    serializer_class = TopTrafficSerializer
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=[HTTPMethod.GET])
    def bandwidth_summary(self, request):
        year = request.GET.get("year")
        if year:
            try:
                year = int(year)
                yearly_bandwidth = (
                    self.queryset.filter(date__year=year)
                    .annotate(month=TruncMonth("date"))
                    .annotate(month=ExtractMonth("month") - 1)
                    .values("month")
                    .annotate(bandwidth=Sum("bandwidth"))
                    .order_by("month")
                )
                return Response(yearly_bandwidth, status=status.HTTP_200_OK)
            except ValueError:
                return Response(
                    {"error": "Invalid year format"}, status=status.HTTP_400_BAD_REQUEST
                )


class TrafficCDNViewSet(viewsets.ModelViewSet):
    queryset = FactTrafficCDN.objects.all().order_by("dim_month")
    serializer_class = TrafficCDNSerializer
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=[HTTPMethod.GET])
    def top_trafic_cdn(self, request):
        category = request.GET.get("category")
        length = request.GET.get("length")
        if category:
            query = (
                self.queryset.annotate(name=F(category))
                .values("name")
                .annotate(total_usage=Sum("usage_value"))
                .order_by("-total_usage")
            )
            if length:
                query = query[: int(length)]
            query_lenght = self.queryset.count()
            data = {"total_queries": query_lenght, "data": query}
            return Response(data, status=status.HTTP_200_OK)
