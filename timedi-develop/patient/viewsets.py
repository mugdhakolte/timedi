from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from patient.serializers import *
from timedi_auth.utils import CustomJSONRenderer
from timedi_auth.permissions import CheckPermission


class PatientListViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
            list:
               Return a list of all patient.
       """
    queryset = Patient.objects.all()
    serializer_class = PatientListSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    http_method_names = ['get']
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_patient", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hospital', 'assign_centre_module']

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Patient.objects.all()
        elif self.request.user.role.name == "admin":
            return Patient.objects.filter(account__id=self.request.user.account_id)
        else:
            return Patient.objects.filter(account__id=self.request.user.account_id, user__id=self.request.user.id)


class PharmacistPatientListViewSet(mixins.ListModelMixin,
                                   viewsets.GenericViewSet):
    """
            list:
               Return a list of all patient with assigned posology and posology not validated..
       """
    queryset = AssignCentreModule.objects.all()
    serializer_class = PharmacistPatientListSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    http_method_names = ['get']
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_patient", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hospital']

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return AssignCentreModule.objects.all()
        elif self.request.user.role.name == "admin":
            return AssignCentreModule.objects.filter(hospital__account__id=self.request.user.account_id, )
        else:
            return AssignCentreModule.objects.filter(hospital__account__id=self.request.user.account_id,
                                                     hospital__user__id=self.request.user.id)


class ProductionPatientListViewSet(mixins.ListModelMixin,
                                   viewsets.GenericViewSet):
    """
            list:
               Return a list of all patient with assigned posology.
   """
    queryset = AssignCentreModule.objects.all()
    serializer_class = ProductionPatientListSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    http_method_names = ['get']
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_patient", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hospital']

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return AssignCentreModule.objects.all()
        elif self.request.user.role.name == "admin":
            return AssignCentreModule.objects.filter(hospital__account__id=self.request.user.account_id, )
        else:
            return AssignCentreModule.objects.filter(hospital__account__id=self.request.user.account_id,
                                                     hospital__user__id=self.request.user.id)


class HistoryPatientListViewSet(mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
            retrieve:
   Return the given hospital related data for history.
   """
    queryset = Hospital.objects.all()
    serializer_class = HistoryPatientListSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    http_method_names = ['get']
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_patient", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Hospital.objects.all()
        elif self.request.user.role.name == "admin":
            return Hospital.objects.filter(account__id=self.request.user.account_id)
        else:
            return Hospital.objects.filter(account__id=self.request.user.account_id, user__id=self.request.user.id)


class PatientViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
        retrieve:
            Return the given patient.

        create:
            Create a new Patient.

        destroy:
            Delete a patient.

        update:
            Update a patient.

        partial_update:
            Update a patient.
    """
    queryset = Patient.objects.all()
    serializer_class = PatientCreateSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_patient", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hospital', ]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Patient.objects.all()
        elif self.request.user.role.name == "admin":
            return Patient.objects.filter(account__id=self.request.user.account_id)
        else:
            return Patient.objects.filter(account__id=self.request.user.account_id, user__id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PatientRetrieveSerializer
        return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = {"message": _("Patient deleted successfully.")}
        return Response(data, status=status.HTTP_204_NO_CONTENT)


class AbsenceReasontViewSet(viewsets.ModelViewSet):
    queryset = AbsenceReason.objects.all()
    serializer_class = AbsenceReasonSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_patient", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient']


class PatientIntermediateProductionViewSet(viewsets.ModelViewSet):
    queryset = IntermediateProduction.objects.all()
    serializer_class = IntermediateProductionPatientSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    # http_method_names = ['get']
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_patient", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient']


class PatientAssignModuleViewSet(mixins.CreateModelMixin,
                                 mixins.ListModelMixin,
                                 mixins.UpdateModelMixin,
                                 viewsets.GenericViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientAssignModuleSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_patient", ]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Patient.objects.all()
        elif self.request.user.role.name == "admin":
            return Patient.objects.filter(account__id=self.request.user.account_id)
        else:
            return Patient.objects.filter(account__id=self.request.user.account_id, user__id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'list':
            return PatientAssignModuleListSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        patient_centre_module = request.data.get("patient_assign_module", None)
        assign_centre_module = patient_centre_module['assign_centre_module']

        for patient_id in patient_centre_module["patient"]:
            instance = Patient.objects.get(id=patient_id)
            patient_data = {"id": patient_id, 'assign_centre_module': assign_centre_module}
            serializer = self.get_serializer(instance, data=patient_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        return Response({"message": _("Modules updated successfully.")}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"message": _("Module updated successfully.")}, status=status.HTTP_200_OK)
