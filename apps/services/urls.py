from django.urls import path
from .views import (
    TopTrafficViewSet,
    TrafficCDNViewSet,
    NewCustomerRegionViewSet,
    TopCDNViewSet,
)

top_traffic_yearly_list = TopTrafficViewSet.as_view({"get": "bandwidth_summary"})
traffic_cdn_list = TrafficCDNViewSet.as_view({"get": "top_traffic_cdn"})
revenue = NewCustomerRegionViewSet.as_view({"get": "revenue"})
gross_profit = NewCustomerRegionViewSet.as_view({"get": "gross_profit"})
cdn_revenue = TopCDNViewSet.as_view({"get": "cdn_revenue"})

urlpatterns = [
    path("services/top-traffic/", top_traffic_yearly_list, name="yearly-bandwidth"),
    path("services/traffic-cdn/", traffic_cdn_list, name="traffic-cdn-summary"),
    path("services/top-cdn/", cdn_revenue, name="top-cdn"),
    path("services/new-cust-region/revenue/", revenue, name="revenue"),
    path("services/new-cust-region/gross-profit/", gross_profit, name="gross-profit"),
]
