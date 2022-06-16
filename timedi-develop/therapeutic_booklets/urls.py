from rest_framework.routers import DefaultRouter
from therapeutic_booklets.viewsets import (TherapeuticBookletsMedicineViewSet, MedicineListViewSet,
                                           OfficialMedicineViewSet, OfficialMedicineCreateViewSet)

router = DefaultRouter()

router.register('medicine', TherapeuticBookletsMedicineViewSet, basename='medicine')
router.register('medicines', MedicineListViewSet, basename="medicines")
router.register('official-medicines', OfficialMedicineViewSet, basename="official_medicines")
router.register('add-to-booklet', OfficialMedicineCreateViewSet, basename="add_to_booklet_medicines")
urlpatterns = router.urls
