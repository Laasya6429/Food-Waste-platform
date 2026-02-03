from rest_framework.viewsets import ModelViewSet
from .serializers import DonationSerializer
from .permissions import IsDonor
from rest_framework.viewsets import ModelViewSet
from .models import FoodRequest, Donation
from .serializers import FoodRequestSerializer
from .permissions import IsNGO
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


from .models import Donation, FoodRequest
from .serializers import DonationSerializer, FoodRequestSerializer
from .permissions import IsDonor, IsNGO
from .services import assess_food_risk, find_nearby_ngos, notify_ngos

from .services import calculate_impact

from .serializers import RegisterSerializer

from .services import (
    find_nearby_ngos,
    assess_food_risk,
    notify_ngos,
)


class DonationViewSet(ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = [IsAuthenticated, IsDonor]

    def get_queryset(self):
        return Donation.objects.filter(donor=self.request.user)

    def perform_update(self, serializer):
        donation = self.get_object()

        if donation.status != "AVAILABLE":
            raise ValidationError(
                "Donation cannot be modified after it has been requested."
            )

        serializer.save()


class FoodRequestViewSet(ModelViewSet):
    serializer_class = FoodRequestSerializer
    permission_classes = [IsAuthenticated, IsNGO]

    def get_queryset(self):
        return FoodRequest.objects.filter(ngo=self.request.user)

    @action(detail=True, methods=["post"])
    def complete_pickup(self, request, pk=None):
        food_request = self.get_object()
        donation = food_request.donation

        # ❌ Pickup already done
        if food_request.status == "COMPLETED":
            raise ValidationError("Pickup already completed.")

        # ❌ Admin approval missing  👈 THIS IS THE LINE YOU ASKED ABOUT
        if food_request.status != "APPROVED":
            raise ValidationError("Pickup not approved by admin yet.")

        # ✅ Mark pickup completed
        food_request.status = "COMPLETED"
        food_request.save()

        donation.status = "PICKED_UP"
        donation.save()

        # ✅ Calculate impact automatically
        calculate_impact(donation)

        return Response(
            {"message": "Pickup completed successfully"},
            status=status.HTTP_200_OK
        )




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
    

