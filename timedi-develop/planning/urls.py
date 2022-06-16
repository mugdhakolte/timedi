from rest_framework.routers import DefaultRouter

from planning.viewsets import PlanningViewSet, MedicinePlanningViewSet, PatientStockManagementViewSet

router = DefaultRouter()

router.register('planning', PlanningViewSet, basename='planning')
router.register('medicine-planning', MedicinePlanningViewSet, basename='medicine_planning')
router.register('patient-stock', PatientStockManagementViewSet, basename='patient_stock_management')

urlpatterns = router.urls
