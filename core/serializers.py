from rest_framework import serializers
from rest_framework import serializers
from .models import FoodRequest,User,Donation,FoodRiskAssessment,ImpactLog


class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        exclude = ['donor']

class FoodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodRequest
        fields = "__all__"
        read_only_fields = ["ngo", "status", "requested_at"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
        )
        return user

class FoodRiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodRiskAssessment
        fields = "__all__"


class ImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImpactLog
        fields = "__all__"
