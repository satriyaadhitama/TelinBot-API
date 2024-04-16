from django.urls import path
from .views import TopTrafficViewSet, TrafficCDNViewSet

top_traffic_yearly_list = TopTrafficViewSet.as_view({"get": "bandwidth_summary"})
traffic_cdn_list = TrafficCDNViewSet.as_view({"get": "top_trafic_cdn"})

urlpatterns = [
    path("services/top-traffic/", top_traffic_yearly_list, name="yearly-bandwidth"),
    path("services/traffic-cdn/", traffic_cdn_list, name="traffic-cdn-summary"),
]
