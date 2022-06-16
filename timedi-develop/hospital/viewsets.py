import operator
from functools import reduce

from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from timedi_auth.models import Account, User
from timedi_auth.permissions import CheckPermission
from timedi_auth.utils import CustomJSONRenderer
from hospital.serializers import *


class HospitalListViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
       list:
           Return a list of all hospital.

    """
    queryset = Hospital.objects.all()
    serializer_class = HospitalListSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    http_method_names = ['get']
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_hospital", ]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Hospital.objects.all()
        elif self.request.user.role.name == "admin":
            return Hospital.objects.filter(account__id=self.request.user.account_id)
        else:
            return Hospital.objects.filter(account__id=self.request.user.account_id, user__id=self.request.user.id)

    @action(methods=["GET"], detail=False, url_path='modules', url_name='modules')
    def get_modules(self, request, *args, **kwargs):
        search_terms = self.request.query_params.get('hospitals')
        if search_terms:
            hospital_list = search_terms.split(',')
            return Response(HospitalAssignCentreModuleListSerializer(Hospital.objects.filter(reduce(operator.or_, (Q(id=term)
                            for term in hospital_list))), many=True).data, status=status.HTTP_200_OK)


class HospitalViewSet(mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
       retrieve:
           Return the given hospital.

       create:
           Create a new hospital.

       destroy:
           Delete a hospital.

       update:
           Update a hospital.

       partial_update:
           Update a hospital.
       """
    queryset = Hospital.objects.all()
    serializer_class = HospitalCreateSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_hospital", ]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Hospital.objects.all()
        elif self.request.user.role.name == "admin":
            return Hospital.objects.filter(account__id=self.request.user.account_id)
        else:
            return Hospital.objects.filter(account__id=self.request.user.account_id, user__id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HospitalRetrieveSerializer
        return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        if instance:
            related_users = User.objects.filter(assigned_hospital=instance.hospital_name,account=instance.account_id)
            for user in related_users:
                user.assigned_hospital = None
                user.save()
        data = {"message": _("Hospital deleted successfully.")}
        return Response(data, status=status.HTTP_204_NO_CONTENT)

   
class ProductionSettingViewset(viewsets.ModelViewSet):
    """
       retrieve:
           Return the given production setting for a hospital.

       list:
           Return a list of all production setting for a hospital.

       create:
           Create a new production setting for a hospital.

       destroy:
           Delete a production setting for a hospital.

       update:
           Update a production setting for a hospital.

       partial_update:
           Update a production setting for a hospital.
    """
    queryset = ProductionSetting.objects.all()
    serializer_class = ProductionSettingsSerializer
    permission_classes = [CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_hospital", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hospital']


class HospitalStockManagementViewset(viewsets.ModelViewSet):
    """
       retrieve:
           Return the given stock management setting for a hospital.

       list:
           Return a list of all stock management setting for a hospital.

       create:
           Create a new stock management setting for a hospital.

       destroy:
           Delete a stock management setting for a hospital.

       update:
           Update a stock management setting for a hospital.

       partial_update:
           Update a stock management setting for a hospital.
       """
    queryset = HospitalStockManagement.objects.all()
    serializer_class = HospitalStockManagementSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_hospital", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hospital']


class IntermediateProductionViewSet(viewsets.ModelViewSet):
    """
      retrieve:
          Return the given intermediate production for a hospital.

      list:
          Return a list of all intermediate production for a hospital.

      create:
          Create a new intermediate production for a hospital.

      destroy:
          Delete a intermediate production a hospital.

      update:
          Update a intermediate production for a hospital.

      partial_update:
          Update a intermediate production for a hospital.
    """
    queryset = IntermediateProduction.objects.all()
    serializer_class = IntermediateProductionSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_hospital", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['hospital']
