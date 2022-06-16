from rest_framework.routers import DefaultRouter
from pharmacist_control.viewsets import PharmacistControlViewSet

router = DefaultRouter()

router.register('pharmacist-control', PharmacistControlViewSet, basename="pharmacist_control")

urlpatterns = router.urls
