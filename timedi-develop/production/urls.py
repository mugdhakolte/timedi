from rest_framework.routers import DefaultRouter

from production.viewsets import ProductionViewSet,ProductionPlanningViewSet

router = DefaultRouter()

router.register('production', ProductionViewSet, basename='production')
router.register('production-planning', ProductionPlanningViewSet, basename='production_planning')
urlpatterns = router.urls
