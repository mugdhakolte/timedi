from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from planning.serializers import *
from timedi_auth.utils import CustomJSONRenderer
from timedi_auth.permissions import CheckPermission


class MedicinePlanningViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Return the given medicines of patient.

        list:
            Return a list of all patient's medicine.

        create:
            Create a new Medicine planning.

        destroy:
            Delete a medicine planning.

        update:
            Update a medicine planning.

        partial_update:
            Update a medicine planning.
    """
    queryset = MedicinePlanning.objects.all()
    serializer_class = MedicinePlanningSerializer
    permission_classes = [CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_planning", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient']

    def create(self, request, *args, **kwargs):
        medicine_list = request.data['medicine']
        serializer_data = []
        error_data = []
        for medicine in medicine_list:
            try:
                obj = MedicinePlanning.objects.get(patient=request.data['patient'], medicine=medicine)
                error_data.append({"id": medicine, "message": _("Medicine already present for this patient.")})
            except MedicinePlanning.DoesNotExist:
                obj = None

        if len(error_data) == 0:
            for medicine in medicine_list:
                planning_data = {
                    "medicine": medicine, "patient": request.data['patient']
                }
                serializer = self.get_serializer(data=planning_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                serializer_data.append(serializer.data)
            return Response(serializer_data, status=status.HTTP_201_CREATED)
        else:
            return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


class PlanningViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Return the given planning.

        list:
            Return a list of all plannings.

        create:
            Create a new planning.

        destroy:
            Delete a planning.

        update:
            Update a planning.

        partial_update:
            Update a planning.
        """
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer
    permission_classes = [CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_planning", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['medicine_planning']

    def get_serializer(self, *args, **kwargs):
        posology_serializers = {"standard_posology": StandardModeSerializer,
                                "specific_posology": StandardModeSerializer,
                                "cycle_posology": CyclePosologySerializer,
                                "each_posology": EachPosologyPlanningSerializer,
                                "from_to_posology": FromToPosologyPlanningSerializer}
        try:
            serializer_class = posology_serializers[kwargs["data"].get("posology_type")]
        except:
            serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class PatientStockManagementViewSet(mixins.ListModelMixin,
                                    mixins.CreateModelMixin,
                                    viewsets.GenericViewSet):
    queryset = PatientStockManagement.objects.all()
    serializer_class = PatientStockManagementSerializer
    permission_classes = [CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_planning", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['medicine_planning']

    def get_serializer_class(self):
        if self.action == "list":
            return PatientStockManagementListSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = serializer.data
        medicine_planning = request.query_params.get('medicine_planning')
        if medicine_planning:
            data.append({"stock": MedicinePlanning.objects.get(id=medicine_planning).stock})
        return Response(data)
