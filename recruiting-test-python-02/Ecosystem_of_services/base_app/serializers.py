from . import models
from rest_framework.serializers import ModelSerializer

class InvestorSerializer(ModelSerializer):
    class Meta:
        model = models.Investor
        fields = '__all__'

