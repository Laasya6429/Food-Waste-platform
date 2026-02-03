from rest_framework.routers import DefaultRouter
from .views import DonationViewSet, FoodRequestViewSet

router = DefaultRouter()
router.register("donations", DonationViewSet)
router.register("requests", FoodRequestViewSet)

urlpatterns = router.urls
