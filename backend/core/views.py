from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Q, Sum, Count, Avg
from django.db.models.functions import TruncDate

from .models import Donation, FoodRequest, ImpactLog, Rating
from .serializers import (
    DonationSerializer, 
    FoodRequestSerializer, 
    RegisterSerializer,
    ImpactSerializer,
    RatingSerializer
)
from .permissions import IsDonor, IsNGO
from .services import calculate_impact


class DonationViewSet(ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DONOR':
            return Donation.objects.filter(donor=user)
        elif user.role == 'NGO':
            # NGOs can see available donations
            return Donation.objects.filter(status='AVAILABLE').exclude(expiry_time__lt=timezone.now())
        return Donation.objects.none()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsDonor()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        donation = self.get_object()

        if donation.status != "AVAILABLE":
            raise ValidationError(
                "Donation cannot be modified after it has been requested."
            )

        serializer.save()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FoodRequestViewSet(ModelViewSet):
    serializer_class = FoodRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'NGO':
            return FoodRequest.objects.filter(ngo=user)
        elif user.role == 'DONOR':
            # Donors can see requests for their donations
            return FoodRequest.objects.filter(donation__donor=user)
        return FoodRequest.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNGO()]
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Donor approves a food request"""
        food_request = self.get_object()
        
        if food_request.donation.donor != request.user:
            raise ValidationError("Only the donor can approve requests.")
        
        if food_request.status != "PENDING":
            raise ValidationError("Request is not pending.")
        
        food_request.status = "APPROVED"
        food_request.save()
        
        return Response(
            {"message": "Request approved successfully"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def complete_pickup(self, request, pk=None):
        """NGO marks pickup as completed"""
        food_request = self.get_object()
        donation = food_request.donation

        if food_request.ngo != request.user:
            raise ValidationError("Only the requesting NGO can complete pickup.")

        if food_request.status == "COMPLETED":
            raise ValidationError("Pickup already completed.")

        if food_request.status != "APPROVED":
            raise ValidationError("Pickup must be approved before completion.")

        food_request.status = "COMPLETED"
        food_request.save()

        donation.status = "PICKED_UP"
        donation.save()

        calculate_impact(donation)

        return Response(
            {"message": "Pickup completed successfully"},
            status=status.HTTP_200_OK
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImpactStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_impact = ImpactLog.objects.aggregate(
            total_meals=Sum('meals_saved'),
            total_food_kg=Sum('food_saved_kg'),
            total_co2_kg=Sum('co2_saved_kg')
        )
        
        donations_count = Donation.objects.filter(status='PICKED_UP').count()
        
        return Response({
            'total_meals_saved': total_impact['total_meals'] or 0,
            'total_food_saved_kg': total_impact['total_food_kg'] or 0,
            'total_co2_saved_kg': total_impact['total_co2_kg'] or 0,
            'total_donations': donations_count
        })


class HeatmapDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get donations grouped by location
        donations = Donation.objects.filter(
            donor__latitude__isnull=False,
            donor__longitude__isnull=False
        ).values('donor__latitude', 'donor__longitude').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity_kg')
        )
        
        heatmap_data = [
            {
                'latitude': float(item['donor__latitude']),
                'longitude': float(item['donor__longitude']),
                'count': item['count'],
                'total_quantity_kg': item['total_quantity']
            }
            for item in donations
        ]
        
        return Response(heatmap_data)


class RatingViewSet(ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        rated_user_id = self.request.query_params.get('rated_user')
        
        if rated_user_id:
            return Rating.objects.filter(rated_user_id=rated_user_id)
        return Rating.objects.filter(rated_user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

