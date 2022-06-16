import uuid
import operator
from functools import reduce

from django.db.models import Q
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend

from invoicing.models import *
from patient.serializers import *
from invoicing.serializers import *
from invoicing.utils import generate_pdf
from therapeutic_booklets.models import *
from timedi_auth.utils import CustomJSONRenderer
from timedi_auth.permissions import CheckPermission


class InvoiceListViewSet(mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
           list:
              Return the given invoice.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceListSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_invoice", ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_valid', 'patient_name', ]

    def get_queryset(self):

        if self.request.GET.get('start_date') and self.request.GET.get('end_date'):
            return Invoice.objects.filter(account__id=self.request.user.account_id,
                                          invoice_datetime__date__gte=self.request.GET.get('start_date'),
                                          invoice_datetime__date__lte=self.request.GET.get('end_date'))

        if self.request.user.role.name == "super_admin":
            return Invoice.objects.all()
        return Invoice.objects.filter(account__id=self.request.user.account_id)


class InvoiceViewSet(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """
        create:
            Create a new invoice.

        validate_patient:
            validate patient as per selected option.

        validate_medicine:
            validate patient as per selected option.

        relate_medicines:
            list out all medicines of given patient.

    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_invoice", ]

    @staticmethod
    def patient_validation(request, patient, invoice):
        invoice_integration_dict = {
            "integration_id": uuid.uuid4(),
            "user": request.user.id
        }
        try:
            store = Store.objects.get(name=invoice.store_name)
            invoice_integration_dict["store"] = store.id
        except ObjectDoesNotExist:
            store = None
            invoice_integration_dict["store"] = store
        integration_serializer = InvoiceIntegrationSerializer(data=invoice_integration_dict)
        integration_serializer.is_valid(raise_exception=True)
        invoice_integration = integration_serializer.create(integration_serializer.validated_data)
        invoice_patient_dict = {
            "invoice_integration": invoice_integration.id,
            "patient": patient.id,
            "invoice_patient_id": invoice.patient_id
        }
        invoice_patient_serializer = InvoiceRelatedPatientSerializer(data=invoice_patient_dict)
        invoice_patient_serializer.is_valid(raise_exception=True)
        invoice_patient = invoice_patient_serializer.create(invoice_patient_serializer.validated_data)
        items_valid_check = [item.is_valid for item in invoice.items.all()]
        check = all(items_valid_check)
        if check:
            for item in [item for item in invoice.items.all()]:
                invoice_medicines = InvoiceRelatedMedicine.objects.filter(invoice_medicine_id=item.product_code)
                medicine_planning = MedicinePlanning.objects.filter(
                    medicine=invoice_medicines.first().medicine.id,
                    patient=invoice_patient.first().patient.id).first()
                if not medicine_planning:
                    medicine_planning = MedicinePlanningSerializer(
                        data={"medicine": invoice_medicines.first().medicine.id,
                              "patient": invoice_patient.first().patient.id})
                    medicine_planning.is_valid(raise_exception=True)
                    medicine_planning.save()
                if item.quantity < 0:
                    stock_movement = {"invoice": invoice.id,
                                      "medicine_planning": medicine_planning.id,
                                      "user": request.user.id, "type": "out",
                                      "description": "invoice",
                                      "quantity": item.quantity}
                else:
                    stock_movement = {"invoice": invoice.id, "medicine_planning": medicine_planning.id,
                                      "user": request.user.id, "type": "in",
                                      "description": "invoice",
                                      "quantity": item.quantity, "patient": invoice_patient.first().id}
                inv_serializer = InvoiceStockMovementSerializer(data=stock_movement)
                inv_serializer.is_valid(raise_exception=True)
                inv_serializer.save()
            invoice.is_valid = True
            invoice.save()

    @staticmethod
    def medicine_validation(request, medicine, invoice_item):
        invoice_integration_dict = {
            "integration_id": uuid.uuid4(),
            "user": request.user.id
        }
        try:
            store = Store.objects.get(name=invoice_item.invoice.store_name)
            invoice_integration_dict["store"] = store.id
        except ObjectDoesNotExist:
            store = None
            invoice_integration_dict["store"] = store
        integration_serializer = InvoiceIntegrationSerializer(data=invoice_integration_dict)
        integration_serializer.is_valid(raise_exception=True)
        invoice_integration = integration_serializer.create(integration_serializer.validated_data)
        invoicerelatedmedicinedict = {
            "invoice_integration": invoice_integration.id,
            "medicine": medicine.id,
            "invoice_medicine_id": invoice_item.product_code,
            # "patient":
            "invoice": invoice_item.invoice.id
        }
        medicine_invoice_serializer = InvoiceRelatedMedicineSerializer(data=invoicerelatedmedicinedict)
        medicine_invoice_serializer.is_valid(raise_exception=True)
        invoice_medicine = medicine_invoice_serializer.create(
            medicine_invoice_serializer.validated_data)
        invoice_item.is_valid = True
        invoice_item.save()
        if all([inv.is_valid for inv in invoice_item.invoice.items.all()]):
            for item in invoice_item.invoice.items.all():
                patient = InvoiceRelatedPatient.objects.filter(
                    invoice_patient_id=invoice_item.invoice.patient_id).first().patient
                if not patient:
                    return Response({"message": _("Please validate patient first")}, status=status.HTTP_200_OK)
                invoice_medicines = InvoiceRelatedMedicine.objects.filter(invoice_medicine_id=item.product_code)
                medicine_planning = MedicinePlanning.objects.filter(
                    medicine=medicine.id, patient=patient.id).first()
                if not medicine_planning:
                    medicine_planning = MedicinePlanningSerializer(
                        data={"medicine": invoice_medicines.first().medicine.id,
                              "patient": patient.id})
                    medicine_planning.is_valid(raise_exception=True)
                    medicine_planning.save()
                    medicine_planning = medicine_planning.data
                if item.quantity < 0:
                    stock_movement = {"invoice": invoice_item.invoice.id,
                                      "medicine_planning": medicine_planning.id,
                                      "user": request.user.id, "type": "out",
                                      "description": "invoice",
                                      "quantity": item.quantity}
                else:
                    stock_movement = {"invoice": invoice_item.invoice.id, "medicine_planning": medicine_planning.id,
                                      "user": request.user.id, "type": "in",
                                      "description": "invoice",
                                      "quantity": item.quantity}
                inv_serializer = InvoiceStockMovementSerializer(data=stock_movement)
                inv_serializer.is_valid(raise_exception=True)
                inv_serializer.save()
            invoice = invoice_item.invoice
            invoice.is_valid = True
            invoice.save()

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Invoice.objects.all()
        return Invoice.objects.filter(account__id=self.request.user.account_id)

    @action(methods=["GET"], detail=False, url_path='relate-medicines', url_name='relate_medicines')
    def relate_medicines(self, request, *args, **kwargs):
        invoice_item_id = self.request.query_params.get('invoice_item_id')
        invoice_item_obj = InvoiceItem.objects.get(id=invoice_item_id)
        medicine_list = []
        patient = InvoiceRelatedPatient.objects.filter(invoice_patient_id=invoice_item_obj.invoice.patient_id).first()
        if patient:
            for medicine_planning in patient.patient.medicine_plannings.all():
                medicine_list.append(
                    {"id": medicine_planning.medicine.id, "medicine_name": medicine_planning.medicine.medicine_name,
                     "patient_id": medicine_planning.patient.id})
            return Response(medicine_list, status=status.HTTP_200_OK)
        else:
            return Response({"message": _("Please validate patient first")},
                            status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path='validate-patient', url_name='validate_patient')
    def validate_patient(self, request, *args, **kwargs):
        type = request.data.get("select_type")
        if type == "add_patient":
            serializer = PatientValidationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['account_id'] = request.user.account_id
                serializer.validated_data['user_id'] = request.user.id
                patient = serializer.create(serializer.validated_data)
                invoice = Invoice.objects.get(id=request.data.get("invoice"))
                self.patient_validation(request, patient, invoice)
                return Response({"message": _("Added patient successfully")},
                                status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif type == "link_patient":
            patient = Patient.objects.get(id=request.data.get("patient"))
            invoice = Invoice.objects.get(id=request.data.get("invoice"))
            self.patient_validation(request, patient, invoice)
            return Response({"message": _("Linked patient successfully")},
                            status=status.HTTP_200_OK)
        else:
            return Response({"message": _("Please enter valid type for validating patient")},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path='validate-medicine', url_name='validate_medicine')
    def validate_medicine(self, request, *args, **kwargs):
        type = request.data.get("select_type")
        if type == "skip_medicine":
            # medicine = Medicine.objects.get(id=request.data.get("medicine"))
            invoice_item = InvoiceItem.objects.get(id=request.data.get("invoice_item"))
            # if invoice_item.product_code == medicine.national_medication_code:
            invoice_item.is_skipped = True
            invoice_item.is_valid = True
            invoice_item.save()
            if all([inv.is_valid for inv in invoice_item.invoice.items.all()]):
                invoice = invoice_item.invoice
                invoice.is_valid = True
                invoice.save()
            return Response({"message": _("Skipped Medicine successfully")},
                            status=status.HTTP_200_OK)
        elif type == "add_medicine":
            is_official = request.data.get("is_official")
            if is_official == 'True':
                invoice_item = InvoiceItem.objects.get(id=request.data.get("invoice_item"))
                official_medicine = OfficialMedicine.objects.get(country_code=self.request.user.account.country_code,
                                                                 national_medication_code=request.data.get(
                                                                     "national_medication_code"))
                official_medicine_serializer = OfficialMedicineSerializer(official_medicine)
                data = official_medicine_serializer.data
                data['is_official'] = True
                data['country_code'] = self.request.user.account.country_code
                serializer = MedicineSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                medicine = serializer.create(serializer.validated_data)
                official_medicine.is_added_to_catalogue = True
                official_medicine.save()
                # try:
                #     therapeutic_book = TherapeuticBook.objects.get(account_id=self.request.user.account_id)
                # except ObjectDoesNotExist:
                therapeutic_book = TherapeuticBook.objects.create(account_id=self.request.user.account_id)
                TherapeuticBookMedicine.objects.create(medicine=medicine, therapeuticbook=therapeutic_book)
                self.medicine_validation(request, medicine, invoice_item)
                return Response({"message": _("Added Medicine successfully")},
                                status=status.HTTP_200_OK)
            else:
                invoice_item = InvoiceItem.objects.get(id=request.data.get("invoice_item"))
                serializer = MedicineValidationSerializer(data=request.data)
                if serializer.is_valid():
                    try:
                        medicine = Medicine.objects.get(country_code=self.request.user.account.country_code,
                                                        therapeuticbooksmedicines__therapeuticbook__account_id=
                                                        self.request.user.account_id,
                                                        national_medication_code=serializer.data.get(
                                                            "national_medication_code"))
                        self.medicine_validation(request, medicine, invoice_item)
                    except ObjectDoesNotExist:
                        try:
                            official_medicine = OfficialMedicine.objects.get(
                                national_medication_code=serializer.data.get("national_medication_code"),
                                country_code=self.request.user.account.country_code)
                            official_medicine_serializer = OfficialMedicineSerializer(official_medicine)
                            data = official_medicine_serializer.data
                            data['is_official'] = True
                            data['country_code'] = self.request.user.account.country_code
                            serializer = MedicineSerializer(data=data)
                            serializer.is_valid(raise_exception=True)
                            medicine = serializer.create(serializer.validated_data)
                            official_medicine.is_added_to_catalogue = True
                            official_medicine.save()
                            # try:
                            #     therapeutic_book = TherapeuticBook.objects.get(account_id=self.request.user.account_id)
                            # except ObjectDoesNotExist:
                            therapeutic_book = TherapeuticBook.objects.create(
                                account_id=self.request.user.account_id)
                            TherapeuticBookMedicine.objects.create(medicine=medicine, therapeuticbook=therapeutic_book)
                            self.medicine_validation(request, medicine, invoice_item)
                        except ObjectDoesNotExist:
                            data = serializer.data
                            data['country_code'] = self.request.user.account.country_code
                            custom_medicine = serializer.create(validated_data=data)
                            # try:
                            #     therapeutic_book = TherapeuticBook.objects.get(account_id=self.request.user.account_id)
                            # except ObjectDoesNotExist:
                            therapeutic_book = TherapeuticBook.objects.create(
                                account_id=self.request.user.account_id)
                            TherapeuticBookMedicine.objects.create(medicine=custom_medicine,
                                                                   therapeuticbook=therapeutic_book)
                            self.medicine_validation(request, custom_medicine, invoice_item)
                    return Response({"message": _("Added Medicine successfully")},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif type == "relate_medicine":
            invoice_item = InvoiceItem.objects.get(id=request.data.get("invoice_item"))
            medicine = Medicine.objects.get(id=request.data.get("medicine"))
            link_type = self.request.data.get("link_type")
            invoice_integration_dict = {
                "integration_id": uuid.uuid4(),
                "user": request.user.id
            }
            try:
                store = Store.objects.get(name=invoice_item.invoice.store_name)
                invoice_integration_dict["store"] = store.id
            except ObjectDoesNotExist:
                store = None
                invoice_integration_dict["store"] = store
            integration_serializer = InvoiceIntegrationSerializer(data=invoice_integration_dict)
            integration_serializer.is_valid(raise_exception=True)
            invoice_integration = integration_serializer.create(integration_serializer.validated_data)
            if link_type == "this_patient_only":
                patient = Patient.objects.get(id=request.data.get("patient"))
                invoicerelatedmedicinedict = {
                    "invoice_integration": invoice_integration.id,
                    "medicine": medicine.id,
                    "invoice_medicine_id": invoice_item.product_code,
                    "patient": patient.id,
                    "invoice": invoice_item.invoice.id
                }
                medicine_invoice_serializer = InvoiceRelatedMedicineSerializer(data=invoicerelatedmedicinedict)
                medicine_invoice_serializer.is_valid(raise_exception=True)
                invoice_medicine = medicine_invoice_serializer.create(
                    medicine_invoice_serializer.validated_data)
                invoice_item.is_valid = True
                invoice_item.save()
                if all([inv.is_valid for inv in invoice_item.invoice.items.all()]):
                    invoice = invoice_item.invoice
                    invoice.is_valid = True
                    invoice.save()
                return Response({"message": _("Relation created for medicine successfully")},
                                status=status.HTTP_200_OK)
            elif link_type == "this_patient_always":
                patient = Patient.objects.get(id=request.data.get("patient"))
                invoicerelatedmedicinedict = {
                    "invoice_integration": invoice_integration.id,
                    "medicine": medicine.id,
                    "invoice_medicine_id": invoice_item.product_code,
                    "patient": patient.id,
                    "invoice": invoice_item.invoice.id
                }
                medicine_invoice_serializer = InvoiceRelatedMedicineSerializer(data=invoicerelatedmedicinedict)
                medicine_invoice_serializer.is_valid(raise_exception=True)
                invoice_medicine = medicine_invoice_serializer.create(
                    medicine_invoice_serializer.validated_data)
                invoice_item.is_valid = True
                invoice_item.save()
                if all([inv.is_valid for inv in invoice_item.invoice.items.all()]):
                    invoice = invoice_item.invoice
                    invoice.is_valid = True
                    invoice.save()
                return Response({"message": _("Relation created for medicine successfully")},
                                status=status.HTTP_200_OK)
            elif link_type == "all_patients_always":
                invoicerelatedmedicinedict = {
                    "invoice_integration": invoice_integration.id,
                    "medicine": medicine.id,
                    "invoice_medicine_id": invoice_item.product_code
                    # "patient":
                    # "invoice": invoice_item.invoice.id
                }
                medicine_invoice_serializer = InvoiceRelatedMedicineSerializer(data=invoicerelatedmedicinedict)
                medicine_invoice_serializer.is_valid(raise_exception=True)
                invoice_medicine = medicine_invoice_serializer.create(
                    medicine_invoice_serializer.validated_data)
                invoice_item.is_valid = True
                invoice_item.save()
                if all([inv.is_valid for inv in invoice_item.invoice.items.all()]):
                    invoice = invoice_item.invoice
                    invoice.is_valid = True
                    invoice.save()
                return Response({"message": _("Relation created for medicine successfully")},
                                status=status.HTTP_200_OK)
            else:
                return Response({"message": _("Please enter valid link type for validating medicine")},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": _("Please enter valid select type for validating medicine")},
                            status=status.HTTP_400_BAD_REQUEST)


class InvoiceMedicineViewSet(mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """
        retrieve:
            Retrieve recognised and unrecognised medicine from invoice .

    """
    queryset = Invoice.objects.all()
    serializer_class = MedicineInvoiceSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_invoice", ]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Invoice.objects.all()
        return Invoice.objects.filter(account__id=self.request.user.account_id)


class HospitalPatientDetailViewSet(mixins.ListModelMixin,
                                   viewsets.GenericViewSet):
    """
        retrieve:
            Retrieve recognised and unrecognised medicine from .

    """
    queryset = Hospital.objects.all()
    serializer_class = HospitalDetailSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_invoice", ]

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['hospital_name', 'patient_name', ]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            return Hospital.objects.all()
        return Hospital.objects.filter(account__id=self.request.user.account_id)

    def list(self, request, *args, **kwargs):
        # hospital_name = request.query_params.get("hospital_name")
        queryset = Hospital.objects.filter(is_active=True, account__id=self.request.user.account_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SimulatorDashboardViewSet(mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
        retrieve:
            Retrieve list of patients .

    """
    queryset = Hospital.objects.all()
    serializer_class = SimulatorDashboardSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_invoice", ]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            if self.request.query_params.get('hospital'):
                search_terms = self.request.query_params.get('hospital')
                if search_terms:
                    hospital_list = search_terms.split(',')
                    return Hospital.objects.filter(reduce(operator.or_, (Q(id=term)
                                                                         for term in hospital_list)))
            return Hospital.objects.all()
        if self.request.query_params.get('hospital'):
            search_terms = self.request.query_params.get('hospital')
            if search_terms:
                hospital_list = search_terms.split(',')
                return Hospital.objects.filter(reduce(operator.or_, (Q(id=term) for term in hospital_list)),
                                               account__id=self.request.user.account_id)
        return Hospital.objects.filter(account__id=self.request.user.account_id)

    def list(self, request, *args, **kwargs):
        if datetime.strptime(request.query_params.get('from'), '%Y-%m-%d').date() > \
                datetime.strptime(request.query_params.get('to'), '%Y-%m-%d').date():
            return Response({"message": _("to date should be greater than from date.")},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["GET"], detail=False, url_path='report-by-patient', url_name='report_by_patient')
    def report_by_patient(self, request, *args, **kwargs):
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if datetime.strptime(request.query_params.get('from'), '%Y-%m-%d').date() > \
                datetime.strptime(request.query_params.get('to'), '%Y-%m-%d').date():
            return Response({"message": _("to date should be greater than from date.")},
                            status=status.HTTP_400_BAD_REQUEST)
        response = SimulatorDashboardSerializer(self.get_queryset(), many=True, context={"request": request}).data
        result = generate_pdf("simulator_report_by_patient.html", response, from_date, to_date)
        return result

    @action(methods=["GET"], detail=False, url_path='report-by-medicine', url_name='report_by_medicine  ')
    def report_by_medicine(self, request, *args, **kwargs):
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        if datetime.strptime(request.query_params.get('from'), '%Y-%m-%d').date() > \
                datetime.strptime(request.query_params.get('to'), '%Y-%m-%d').date():
            return Response({"message": _("to date should be greater than from date.")},
                            status=status.HTTP_400_BAD_REQUEST)
        response = SimulatorDashboardSerializer(self.get_queryset(), many=True, context={"request": request}).data
        medicine_data = [detail for res in response if res for module in res['assign_centre_modules'] if module
                         for patient in module['patients'] if patient for detail in patient['details'] if detail]
        result = generate_pdf("simulator_report_by_medicine.html", response, from_date, to_date)
        return result


class InvoiceStockMovementViewSet(mixins.ListModelMixin,
                                  viewsets.GenericViewSet):
    """
        retrieve:
            Retrieve list of patient's Stock Movement.

    """
    queryset = PatientStockManagement.objects.all()
    serializer_class = InvoiceStockMovementSerializer
    permission_classes = [IsAuthenticated, CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_invoice", ]

    def get_queryset(self):
        from_date = self.request.query_params.get("from")
        to_date = self.request.query_params.get("to")
        if self.request.query_params.get('patient'):
            search_terms = self.request.query_params.get('patient')
            if search_terms:
                patient_list = search_terms.split(',')
                return PatientStockManagement.objects.filter(reduce(operator.or_, (
                    Q(medicine_planning__patient__id=term, description="invoice",
                      invoice__invoice_datetime__gte=from_date,
                      invoice__invoice_datetime__lte=to_date) for term in patient_list)))
        return PatientStockManagement.objects.filter(description="invoice",
                                                     invoice__invoice_datetime__gte=from_date,
                                                     invoice__invoice_datetime__lte=to_date
                                                     )

    @action(methods=["GET"], detail=False, url_path='stock-movement-report', url_name='stock_movement_report')
    def stock_movement_report(self, request, *args, **kwargs):
        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        search_terms = self.request.query_params.get('patient')
        patient_list = search_terms.split(',')
        history_list = []
        for patient in patient_list:
            qs = PatientStockManagement.objects.filter(medicine_planning__patient__id=patient, description="invoice",
                                                       invoice__invoice_datetime__gte=from_date,
                                                       invoice__invoice_datetime__lte=to_date)
            response = InvoiceStockMovementSerializer(qs, many=True, context={"request": request}).data
            data = {"history_data": response,
                    "hospital_name": Patient.objects.get(
                        id=patient).hospital.hospital_name,
                    "patient_name": Patient.objects.get(id=patient).full_name}
            history_list.append(data)
        result = generate_pdf("invoice_history_report.html", history_list, from_date, to_date)
        return result
