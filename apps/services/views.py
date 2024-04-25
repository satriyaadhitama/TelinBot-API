from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status
from django.db.models import Sum, F, CharField, FloatField, Value, OuterRef, Subquery
from django.db.models.functions import TruncMonth, ExtractMonth, Cast
from http import HTTPMethod

from utils.date import get_prev_month


from .models import FactNewCustomerRegion, FactTopCDN, FactTopTraffic, FactTrafficCDN
from .serializers import (
    NewCustomerRegionSerializer,
    TopCDNSerializer,
    TopTrafficSerializer,
    TrafficCDNSerializer,
)


class NewCustomerRegionViewSet(viewsets.ModelViewSet):
    queryset = FactNewCustomerRegion.objects.all().order_by("date")
    serializer_class = NewCustomerRegionSerializer

    @action(detail=False, methods=[HTTPMethod.GET])
    def revenue(self, request):
        year = request.GET.get("year")
        month = request.GET.get("month")
        type = request.GET.get("type")

        prev_year, prev_month = get_prev_month(int(year), int(month))

        last_month = str(prev_year) + (
            "0" + str(prev_month) if prev_month < 10 else str(prev_month)
        )
        current_month = year + ("0" + month if int(prev_month) < 10 else month)

        # Calculate last month's data
        lm_query = FactNewCustomerRegion.objects.filter(
            date_key=int(last_month),
            currency="IDR",
            subgroup1="Revenue",
            type=type,
        ).aggregate(lm=Sum("amount") * -1)
        last_month_revenue = lm_query["lm"] if lm_query["lm"] is not None else 0

        # Calculate this month's data
        current_month_query = FactNewCustomerRegion.objects.filter(
            date_key=int(current_month),
            currency="IDR",
            subgroup1="Revenue",
            type=type,
        )

        current_month_data = current_month_query.aggregate(
            revenue=Sum("amount") * -1, total_budget=Sum("budget")
        )
        revenue = (
            current_month_data["revenue"]
            if current_month_data["revenue"] is not None
            else 0
        )
        total_budget = (
            current_month_data["total_budget"]
            if current_month_data["total_budget"] is not None
            else 0
        )

        # Calculate achievement and growth
        achievement = (revenue / total_budget * 100) if total_budget != 0 else 0
        growth = (
            ((revenue - last_month_revenue) / last_month_revenue * 100)
            if last_month_revenue != 0
            else 0
        )

        # Convert revenue to billions for display
        revenue_in_billions = revenue / 1_000_000_000

        # Results
        results = {
            "revenue": revenue_in_billions,
            "achievement": achievement,
            "growth": growth,
        }

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=[HTTPMethod.GET])
    def gross_profit(self, request):
        year = request.GET.get("year")
        month = request.GET.get("month")
        type = request.GET.get("type")

        prev_year, prev_month = get_prev_month(int(year), int(month))

        last_month = str(prev_year) + (
            "0" + str(prev_month) if prev_month < 10 else str(prev_month)
        )
        current_month = year + ("0" + month if int(month) < 10 else month)

        # Define common filter parameters to avoid repetition
        common_filters = {
            "currency": "IDR",
            "type": type,
        }

        # Helper function to handle None from aggregates
        def get_aggregated_amount(queryset, field):
            result = queryset.aggregate(total=Sum(field))["total"]
            return result if result is not None else 0

        # Calculate Revenue and Cost of Sales for Last Month and Current Month
        rev_lm = -1 * get_aggregated_amount(
            FactNewCustomerRegion.objects.filter(
                **common_filters, subgroup1="Revenue", date_key=last_month
            ),
            "amount",
        )

        cos_lm = get_aggregated_amount(
            FactNewCustomerRegion.objects.filter(
                **common_filters, subgroup1="Direct Cost", date_key=last_month
            ),
            "amount",
        )

        rev = -1 * get_aggregated_amount(
            FactNewCustomerRegion.objects.filter(
                **common_filters, subgroup1="Revenue", date_key=current_month
            ),
            "amount",
        )

        cos = get_aggregated_amount(
            FactNewCustomerRegion.objects.filter(
                **common_filters, subgroup1="Direct Cost", date_key=current_month
            ),
            "amount",
        )

        # Calculate Budget Revenue and Budget Cost of Sales for Current Month
        budget_rev = get_aggregated_amount(
            FactNewCustomerRegion.objects.filter(
                **common_filters, subgroup1="Revenue", date_key=current_month
            ),
            "budget",
        )

        budget_cos = get_aggregated_amount(
            FactNewCustomerRegion.objects.filter(
                **common_filters, subgroup1="Direct Cost", date_key=current_month
            ),
            "budget",
        )

        # Calculating Gross Profit and Growth in Gross Profit
        gp = rev - cos
        gp_lm = rev_lm - cos_lm
        gr_gp = ((gp - gp_lm) / gp_lm if gp_lm != 0 else 0) * 100

        budget_gp = budget_rev - budget_cos
        ach_gp = (gp / budget_gp if budget_gp != 0 else 0) * 100

        # Results
        results = {
            "gross_profit": gp / 1_000_000_000,
            "margin": (gp / rev * 100 if rev != 0 else 0),
            "achievement": ach_gp,
            "growth": gr_gp,
        }

        return Response(results, status=status.HTTP_200_OK)


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
    def top_traffic_cdn(self, request):
        category = request.GET.get("category")
        length = request.GET.get("length")
        year = request.GET.get("year")
        month = request.GET.get("month")
        type = request.GET.get("type")

        month = "0" + str(month) if int(month) < 10 else str(month)
        dim_month = str(year) + str(month)

        query = self.queryset.filter(dim_month=dim_month, type=type)
        query_length = query.count()

        query = (
            query.annotate(name=F(category))
            .values("name")
            .annotate(total=Sum("usage_value"))
            .order_by("-total")
        )

        if length:
            query = query[: int(length)]

        data = {"total_queries": query_length, "data": query}
        return Response(data, status=status.HTTP_200_OK)


class TopCDNViewSet(viewsets.ModelViewSet):
    queryset = FactTopCDN.objects.all().order_by("date_key")
    serializer_class = TopCDNSerializer
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=[HTTPMethod.GET])
    def cdn_revenue(self, request):
        category = request.GET.get("category")
        length = request.GET.get("length")
        year = request.GET.get("year")
        month = request.GET.get("month")
        type = request.GET.get("type")

        month = "0" + str(month) if int(month) < 10 else str(month)
        dim_month = str(year) + str(month)
        print(dim_month)

        query = self.queryset.filter(
            date_key=dim_month, type=type, subgroup1="Revenue"
        ).exclude(amount=0)
        query_length = query.count()

        query = (
            query.annotate(name=F(category))
            .values("name")
            .annotate(total=Sum("amount"))
            .order_by("total")
        )

        if length:
            query = query[: int(length)]

        data = {"total_queries": query_length, "data": query}
        return Response(data, status=status.HTTP_200_OK)
