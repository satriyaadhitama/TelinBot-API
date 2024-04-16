from .models import FactNewCustomerRegion, FactTopCDN, FactTopTraffic, FactTrafficCDN
from rest_framework import serializers


class NewCustomerRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactNewCustomerRegion
        fields = "__all__"


class TopCDNSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactTopCDN
        fields = "__all__"


class TopTrafficSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactTopTraffic
        fields = "__all__"


class TrafficCDNSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactTrafficCDN
        fields = "__all__"
