import operator
from functools import reduce

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from therapeutic_booklets.serializers import *
from timedi_auth.utils import CustomJSONRenderer
from timedi_auth.permissions import CheckPermission
from therapeutic_booklets.utils import (xls_to_response, generate_pdf)


class OfficialMedicineViewSet(mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    """
        list:
              Return a list of all official medicine.

        create:
            Accept List of medicines to add in catalogue.
       """
    queryset = OfficialMedicine.objects.all()
    serializer_class = OfficialMedicineListSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_therapeutic_booklet", ]

    def get_queryset(self):

        if self.request.user.role.name == "super_admin":
            if self.request.query_params.get('search'):
                search_terms = self.request.query_params.get('search')
                if search_terms:
                    search_list = search_terms.split(',')
                    return OfficialMedicine.objects. \
                        filter(reduce(operator.or_, (Q(medicine_name__istartswith=term)
                                                     for term in search_list)))
            return OfficialMedicine.objects.all()
        else:
            if self.request.query_params.get('search'):
                search_terms = self.request.query_params.get('search')
                if search_terms:
                    search_list = search_terms.split(',')
                    return OfficialMedicine.objects. \
                        filter(reduce(operator.or_, (Q(medicine_name__istartswith=term)
                                                     for term in search_list)))
            return OfficialMedicine.objects.all()


class OfficialMedicineCreateViewSet(mixins.CreateModelMixin,
                                    viewsets.GenericViewSet):
    """
    create:
        Accept List of medicines to add in catalogue.
    """
    queryset = OfficialMedicine.objects.all()
    serializer_class = OfficialMedicineCreateSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_therapeutic_booklet", ]

    def create(self, request, *args, **kwargs):
        # Planning.objects.filter(medicine_planning__patient_id__in=patients_id).update(is_validated=True)
        response_data = []
        qs = OfficialMedicine.objects.filter(
            reduce(operator.or_, (Q(pk=m_id) for m_id in request.data["official_medicines"])))
        official_medicine_data = OfficialMedicineListSerializer(qs, many=True)
        for data in official_medicine_data.data:
            data["is_official"] = True
            serializer = MedicineSerializer(data=data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            response_data.append(serializer.data)
        qs.update(is_added_to_catalogue=True)
        return Response(response_data, status=status.HTTP_200_OK)


class MedicineListViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """
    list:
           Return a list of all medicine.
    """

    queryset = Medicine.objects.all()
    serializer_class = MedicineListSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_therapeutic_booklet", ]

    def get_queryset(self):

        if self.request.user.role.name == "super_admin":
            if self.request.query_params.get('search'):
                search_terms = self.request.query_params.get('search')
                if search_terms:
                    search_list = search_terms.split(',')
                    return Medicine.objects. \
                        filter(reduce(operator.or_, (Q(medicine_name__istartswith=term)
                                                     for term in search_list)))
            return Medicine.objects.all()
        else:
            if self.request.query_params.get('search'):
                search_terms = self.request.query_params.get('search')
                if search_terms:
                    search_list = search_terms.split(',')
                    return Medicine.objects. \
                        filter(reduce(operator.or_, (Q(medicine_name__istartswith=term)
                                                     for term in search_list)),
                               therapeuticbooksmedicines__therapeuticbook__account_id=self.request.user.account_id)
            return Medicine.objects.filter(
                therapeuticbooksmedicines__therapeuticbook__account_id=self.request.user.account_id)


class TherapeuticBookletsMedicineViewSet(mixins.RetrieveModelMixin,
                                         mixins.CreateModelMixin,
                                         mixins.UpdateModelMixin,
                                         mixins.DestroyModelMixin,
                                         viewsets.GenericViewSet):
    """
       retrieve:
           Return the given medicine.

       create:
           Create a new medicine.

       destroy:
           Delete a medicine.

       update:
           Update a medicine.

       partial_update:
           Update a medicine.

       report:
            generates report for medicine in excel and pdf format.
    """

    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_therapeutic_booklet", ]
    filter_backends = [DjangoFilterBackend]

    @action(methods=["POST"], detail=False, url_name='report')
    def report(self, request, *args, **kwargs):
        report_type = request.data.get("report_type", None)
        if not report_type:
            return Response({"report_type": _("This field is required.")}, status=status.HTTP_400_BAD_REQUEST)
        if self.request.user.role.name == "super_admin":
            medicines_list = Medicine.objects.all()
        elif self.request.user.role.name == "admin":
            medicines_list = Medicine.objects.filter(
                therapeuticbooksmedicines__therapeuticbook__account_id=self.request.user.account_id)
        else:
            medicines_list = Medicine.objects.filter(
                therapeuticbooksmedicines__therapeuticbook__account_id=self.request.user.account_id)
        medicines_list = MedicineListSerializer(medicines_list, many=True)
        if medicines_list.data:
            if report_type == 'excel':
                response = xls_to_response(medicines_list, self.request.user.account_id)
            elif report_type == 'pdf':
                response = generate_pdf("pdf.html", medicines_list, self.request.user.account_id)
            else:
                response = Response({"message": _("Please select correct file format")},
                                    status=status.HTTP_400_BAD_REQUEST)
            return response
        else:
            return Response({"message": _("Data is not present to generate report")},
                            status=status.HTTP_400_BAD_REQUEST)
