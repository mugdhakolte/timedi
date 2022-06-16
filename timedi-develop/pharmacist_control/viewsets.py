import operator
from functools import reduce

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from timedi_auth.utils import CustomJSONRenderer
from timedi_auth.permissions import CheckPermission
from pharmacist_control.serializers import *


class PharmacistControlViewSet(viewsets.ModelViewSet):
    """
            retrieve:
                Return the given medicine Planning of patient.

            list:
                Return a list of selected patient's medicine plannings.

            create:
                Validate selected posology.

            destroy:
                Delete a medicine planning.

            update:
                Update selected posology.

            partial_update:
                Update selected posology.
        """
    queryset = MedicinePlanning.objects.all()
    serializer_class = PharmacistControlSerializer
    permission_classes = [CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_pharmacist_control", ]

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['patient']
    @staticmethod
    def sorting(queryset, search_data):
        return [q for p_id in search_data for q in queryset.filter(patient__id=p_id)]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            search_terms = self.request.query_params.get('patient')
            if search_terms:
                search_data = search_terms.split(',')
                return self.sorting(MedicinePlanning.objects.exclude(plannings__isnull=True).filter(
                    reduce(operator.or_, (Q(patient__id=term) for term in search_data))), search_data)
            return MedicinePlanning.objects.all().exclude(plannings__isnull=True)
        else:
            search_terms = self.request.query_params.get('patient')
            if search_terms:
                search_data = search_terms.split(',')
                return self.sorting(MedicinePlanning.objects.exclude(plannings__isnull=True).filter(
                    reduce(operator.or_, (Q(patient__id=term) for term in search_data)),
                    medicine__therapeuticbooksmedicines__therapeuticbook__account_id=self.request.user.account_id),
                    search_data)
            return MedicinePlanning.objects.exclude(plannings__isnull=True).filter(
                medicine__therapeuticbooksmedicines__therapeuticbook__account_id=self.request.user.account_id)

    def get_serializer_class(self):
        if self.action == "create":
            return ValidatePlanningSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        patients_id = request.data['patients']
        Planning.objects.filter(medicine_planning__patient_id__in=patients_id).update(is_validated=True)
        return Response({"message": _("Posologies validated successfully.")})
