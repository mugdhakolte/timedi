# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework import status
#
# from api.serializers.modelserializers import *
# from api.permissions import *
#
#
# class DoctorViewSet(viewsets.ModelViewSet):
#     queryset = Doctor.objects.all()
#     serializer_class = DoctorSerializer
#
#
# class StoreViewSet(viewsets.ModelViewSet):
#     queryset = Store.objects.all()
#     serializer_class = StoreSerializer
#
#
# class MedicalProfileViewSet(viewsets.ModelViewSet):
#     queryset = MedicalProfile.objects.all()
#     serializer_class = MedicalProfileSerializer
#
#
# class TherapeuticBookViewSet(viewsets.ModelViewSet):
#     queryset = TherapeuticBook.objects.all()
#     serializer_class = TherapeuticBookSerializer
#
#
# class MedicineViewSet(viewsets.ModelViewSet):
#     queryset = Medicine.objects.all()
#     serializer_class = MedicineSerializer
#
#
# class TherapeuticBookMedicineViewSet(viewsets.ModelViewSet):
#     queryset = TherapeuticBookMedicine.objects.all()
#     serializer_class = TherapeuticBookMedicineSerializer
#
#
# class StockManagementViewSet(viewsets.ModelViewSet):
#     queryset = StockManagement.objects.all()
#     serializer_class = StockManagementSerializer
#
#
# class PlanningViewSet(viewsets.ModelViewSet):
#     queryset = Planning.objects.all()
#     serializer_class = PlanningSerializer
#
#
# class OutputViewSet(viewsets.ModelViewSet):
#     queryset = Output.objects.all()
#     serializer_class = OutputSerializer
#
#
# class StandardPlanningViewSet(viewsets.ModelViewSet):
#     queryset = StandardPlanning.objects.all()
#     serializer_class = StandardPlanningSerializer
#
#
# class SpecificPlanningViewSet(viewsets.ModelViewSet):
#     queryset = SpecificPlanning.objects.all()
#     serializer_class = SpecificPlanningSerializer
#
#
# class EachPosolgyPlanningViewSet(viewsets.ModelViewSet):
#     queryset = EachPosolgyPlanning.objects.all()
#     serializer_class = EachPosolgyPlanningSerializer
