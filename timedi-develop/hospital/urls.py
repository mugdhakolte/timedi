from rest_framework.routers import DefaultRouter

from hospital.viewsets import (HospitalViewSet, HospitalListViewSet, ProductionSettingViewset,
                               IntermediateProductionViewSet, HospitalStockManagementViewset)

router = DefaultRouter()

router.register('hospital/production-setting', ProductionSettingViewset, basename='hospital-production-setting')
router.register('hospital/stock-management', HospitalStockManagementViewset, basename='hospital-stock-management')
router.register('hospital/intermediate-productions', IntermediateProductionViewSet,
                basename='hospital-intermediate-productions')
router.register('hospital', HospitalViewSet, basename='hospital')
router.register('hospitals', HospitalListViewSet, basename='hospitals')

urlpatterns = router.urls
