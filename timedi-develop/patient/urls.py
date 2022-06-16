from rest_framework.routers import DefaultRouter
from patient.viewsets import (PatientListViewSet, PatientViewSet, AbsenceReasontViewSet,
                              PatientIntermediateProductionViewSet, PatientAssignModuleViewSet,
                              PharmacistPatientListViewSet, ProductionPatientListViewSet,
                              HistoryPatientListViewSet)

router = DefaultRouter()

router.register('patient/absence-reason', AbsenceReasontViewSet, basename='patient_absence_reason')
router.register('patient/intermediate-productions', PatientIntermediateProductionViewSet,
                basename='patient-intermediate-productions')
router.register("patients/pharmacist", PharmacistPatientListViewSet, basename='pharmacist_control_patients')
router.register("patients/production", ProductionPatientListViewSet, basename='production_patients')
router.register("patients/history", HistoryPatientListViewSet, basename='history_patients')
router.register('patients', PatientListViewSet, basename='patients')
router.register('patient', PatientViewSet, basename='patient')
router.register('patient-assign-module', PatientAssignModuleViewSet, basename='patient_assign_module')


urlpatterns = router.urls
