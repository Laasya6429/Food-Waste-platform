from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import FoodRequest, User, Donation, FoodRiskAssessment, ImpactLog, Rating


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token


class UserSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'address', 'latitude', 'longitude', 'average_rating']
        read_only_fields = ['id', 'average_rating']
    
    def get_average_rating(self, obj):
        ratings = Rating.objects.filter(rated_user=obj)
        if ratings.exists():
            return round(sum(r.rating for r in ratings) / ratings.count(), 2)
        return None


class DonationSerializer(serializers.ModelSerializer):
    donor = UserSerializer(read_only=True)
    risk_assessment = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    
    class Meta:
        model = Donation
        fields = '__all__'
        read_only_fields = ['donor', 'status', 'created_at']
    
    def get_risk_assessment(self, obj):
        try:
            risk = obj.risk
            return {
                'risk_level': risk.risk_level,
                'reason': risk.reason
            }
        except FoodRiskAssessment.DoesNotExist:
            return None
    
    def get_distance_km(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'NGO':
            if request.user.latitude and request.user.longitude and obj.donor.latitude and obj.donor.longitude:
                from .utils import calculate_distance
                return calculate_distance(
                    request.user.latitude,
                    request.user.longitude,
                    obj.donor.latitude,
                    obj.donor.longitude
                )
        return None
    
    def create(self, validated_data):
        validated_data['donor'] = self.context['request'].user
        donation = super().create(validated_data)
        # Assess risk and notify NGOs
        from .services import assess_food_risk, find_nearby_ngos, notify_ngos
        assess_food_risk(donation)
        nearby_ngos = find_nearby_ngos(donation)
        notify_ngos(nearby_ngos, donation)
        return donation

class FoodRequestSerializer(serializers.ModelSerializer):
    ngo = UserSerializer(read_only=True)
    donation_detail = DonationSerializer(source='donation', read_only=True)
    
    class Meta:
        model = FoodRequest
        fields = ['id', 'donation', 'donation_detail', 'ngo', 'pickup_time', 'status', 'requested_at']
        read_only_fields = ["ngo", "status", "requested_at"]
    
    def create(self, validated_data):
        validated_data['ngo'] = self.context['request'].user
        food_request = super().create(validated_data)
        # Update donation status
        donation = food_request.donation
        donation.status = 'REQUESTED'
        donation.save()
        return food_request
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Replace donation ID with full donation detail
        if 'donation_detail' in representation:
            representation['donation'] = representation.pop('donation_detail')
        return representation

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


class RatingSerializer(serializers.ModelSerializer):
    rated_by = UserSerializer(read_only=True)
    rated_user = UserSerializer(read_only=True)
    
    class Meta:
        model = Rating
        fields = "__all__"
        read_only_fields = ['rated_by', 'created_at']
    
    def create(self, validated_data):
        validated_data['rated_by'] = self.context['request'].user
        return super().create(validated_data)
