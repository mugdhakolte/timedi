from rest_framework.routers import DefaultRouter

from history.viewsets import *

router = DefaultRouter()

router.register('history', HistoryDashboardViewSet, basename='history')

urlpatterns = router.urls
