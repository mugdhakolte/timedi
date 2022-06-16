"""
Serializers for invoicig module.
"""
from datetime import *
import operator
from functools import reduce
import math
import base64

from django.db.models import Q
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework.validators import UniqueTogetherValidator

from invoicing.models import *
from invoicing.utils import stock_calculation
from patient.models import Patient, AssignCentreModule
from hospital.models import Hospital
from therapeutic_booklets.models import Medicine, OfficialMedicine
from production.serializers import (Planning, MedicinePlanning, StandardModeIntakeSerializer,
                                    EachPosologySerializer, FromToPosologySerializer, PatientStockManagement,
                                    MedicinePlanningSerializer)
from production.utils import BarcodeDrawing


class InvoiceListSerializer(serializers.ModelSerializer):
    number_of_medicine = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    is_issue_in_patient = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ("id", "is_valid", "hospital_name", "patient_name",
                  "date", "number_of_medicine", "is_issue_in_patient")

    def get_date(self, obj):
        return obj.invoice_datetime.date()

    def get_number_of_medicine(self, obj):
        return obj.items.all().count()

    def get_is_issue_in_patient(self, obj):
        invoice_patients = InvoiceRelatedPatient.objects.filter(invoice_patient_id=obj.patient_id)
        if len(invoice_patients) > 0:
            return False
        else:
            return True


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ("product_code", "quantity",)


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        exclude = ("created_at", "updated_at", "account")

    def create(self, validated_data):
        items_validated_data = validated_data.pop('items', [])
        validated_data['account_id'] = self.context['request'].user.account_id
        validated_data['is_valid'] = False
        invoice = Invoice.objects.create(**validated_data)
        items_serializer = self.fields['items']
        for item in items_validated_data:
            item['invoice'] = invoice
        items = items_serializer.create(items_validated_data)

        for item in items:
            invoice_medicines = InvoiceRelatedMedicine.objects.filter(invoice_medicine_id=item.product_code)
            if invoice_medicines:
                invoice_integration_dict = {
                    "integration_id": uuid.uuid4(),
                    "user": self.context['request'].user.id
                }
                try:
                    store = Store.objects.get(name=item.invoice.store_name)
                    invoice_integration_dict["store"] = store.id
                except ObjectDoesNotExist:
                    store = None
                    invoice_integration_dict["store"] = store
                integration_serializer = InvoiceIntegrationSerializer(data=invoice_integration_dict)
                integration_serializer.is_valid(raise_exception=True)
                invoice_integration = integration_serializer.create(integration_serializer.validated_data)
                invoicerelatedmedicinedict = {
                    "invoice_integration": invoice_integration.id,
                    "medicine": invoice_medicines.first().medicine.id,
                    "invoice_medicine_id": item.product_code,
                    # "patient":
                    "invoice": item.invoice.id
                }
                medicine_invoice_serializer = InvoiceRelatedMedicineSerializer(data=invoicerelatedmedicinedict)
                medicine_invoice_serializer.is_valid(raise_exception=True)
                invoice_medicine = medicine_invoice_serializer.create(
                    medicine_invoice_serializer.validated_data)
                item.is_valid = True
                item.save()

        invoice_patient = InvoiceRelatedPatient.objects.filter(invoice_patient_id=invoice.patient_id)
        if invoice_patient:
            invoice_integration_dict = {
                "integration_id": uuid.uuid4(),
                "user": self.context['request'].user.id
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
                "patient": invoice_patient.first().patient.id,
                "invoice_patient_id": invoice.patient_id
            }
            invoice_patient_serializer = InvoiceRelatedPatientSerializer(data=invoice_patient_dict)
            invoice_patient_serializer.is_valid(raise_exception=True)
            invoice_patient = invoice_patient_serializer.create(invoice_patient_serializer.validated_data)
            items_valid_check = [item.is_valid for item in invoice.items.all()]
            check = all(items_valid_check)
            if check:
                for item in invoice.items.all():
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
                                          "user": self.context['request'].user.id, "type": "out",
                                          "description": "invoice",
                                          "quantity": item.quantity}
                    else:
                        stock_movement = {"invoice": invoice.id, "medicine_planning": medicine_planning.id,
                                          "user": self.context['request'].user.id, "type": "in",
                                          "description": "invoice",
                                          "quantity": item.quantity, "patient": invoice_patient.first().id}
                    inv_serializer = InvoiceStockMovementSerializer(data=stock_movement)
                    inv_serializer.is_valid(raise_exception=True)
                    inv_serializer.save()
                invoice.is_valid = True
                invoice.save()
        return invoice


class MedicineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ("id", "medicine_name", "units_per_box", "national_medication_code")


class MedicineInvoiceSerializer(serializers.ModelSerializer):
    medicine_details = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        exclude = ("created_at", "updated_at", "account")

    def get_medicine_details(self, obj):
        data = []
        for item in obj.items.all():
            try:
                recognized_data = MedicineListSerializer(Medicine.objects.get(
                    therapeuticbooksmedicines__therapeuticbook__account=obj.account,
                    country_code=obj.account.country_code,
                    national_medication_code=item.product_code)).data
                recognized_data['id'] = item.id
                recognized_data["is_recognized"] = True
                if item.is_skipped:
                    recognized_data["is_skipped"] = True
                else:
                    recognized_data["is_skipped"] = False
                data.append(recognized_data)
            except ObjectDoesNotExist:
                unrecognized_data = InvoiceItemSerializer(item).data
                try:
                    official_data = MedicineListSerializer(OfficialMedicine.objects.
                                                           get(national_medication_code=item.product_code,
                                                               country_code=obj.account.country_code)).data
                    unrecognized_data['id'] = item.id
                    unrecognized_data["is_official_medicine"] = True
                    if item.is_skipped:
                        unrecognized_data["is_skipped"] = True
                        unrecognized_data["is_recognized"] = True
                    else:
                        unrecognized_data["is_skipped"] = False
                        unrecognized_data["is_recognized"] = False
                    if item.is_valid:
                        unrecognized_data["is_recognized"] = True
                except ObjectDoesNotExist:
                    unrecognized_data['id'] = item.id
                    unrecognized_data["is_official_medicine"] = False
                    if item.is_skipped:
                        unrecognized_data["is_skipped"] = True
                        unrecognized_data["is_recognized"] = True
                    else:
                        unrecognized_data["is_skipped"] = False
                        unrecognized_data["is_recognized"] = False
                    if item.is_valid:
                        unrecognized_data["is_recognized"] = True
                data.append(unrecognized_data)
        return data


class PatientDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ("id", "full_name")


class HospitalDetailSerializer(serializers.ModelSerializer):
    patients = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = ("id", "hospital_name", "patients")

    def get_patients(self, obj):
        data = []
        for patient in obj.patients.all():
            # if self.context["request"].query_params.get('patient_name').lower() in patient.full_name.lower():
            #     data.append(PatientDetailSerializer(patient).data)
            data.append(PatientDetailSerializer(patient).data)
        return data


class PatientValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ("created_at", "updated_at", "account", "user")


class MedicineValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = ("id", "medicine_name", "units_per_box", "national_medication_code",
                  "strength", "laboratories", "type", "non_packable_treatment")


class InvoiceIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceIntegration
        fields = "__all__"


class InvoiceRelatedPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceRelatedPatient
        fields = "__all__"


class InvoiceRelatedMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceRelatedMedicine
        fields = "__all__"


class OfficialMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficialMedicine
        fields = "__all__"


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = "__all__"


class PlanningProductionSerializer(serializers.ModelSerializer):
    posology_plannings = StandardModeIntakeSerializer(many=True)
    each_posology_plannings = EachPosologySerializer(many=True)
    from_to_posology_plannings = FromToPosologySerializer(many=True)

    # medicine = serializers.SerializerMethodField()

    class Meta:
        model = Planning
        fields = '__all__'

    # def get_medicine(self, obj):
    #     medicine_data = obj.medicine_planning.medicine
    #     return {"medicine_name": medicine_data.medicine_name,
    #             "national_medication_code": medicine_data.national_medication_code,
    #             "units_per_box": medicine_data.units_per_box, "type": medicine_data.type}


class ProductionCreatePlanningSerializer(serializers.ModelSerializer):
    plannings = serializers.SerializerMethodField()
    # planning_count = serializers.SerializerMethodField()
    absence_reasons = serializers.SerializerMethodField()
    medicine_name = serializers.SerializerMethodField()
    national_medication_code = serializers.SerializerMethodField()
    units_per_box = serializers.SerializerMethodField()
    barcode = serializers.SerializerMethodField()

    # patient_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicinePlanning
        exclude = ("created_at", "updated_at")

    # def get_planning_count(self, obj):
    #     return obj.plannings.all().count()

    def get_absence_reasons(self, obj):
        data = []
        for reason in obj.patient.absence_reasons.all():
            reason_dict = {"id": reason.id, "reason": reason.reason, "release_date": reason.release_date,
                           "return_date": reason.return_date, "no_return_date": reason.no_return_date}
            data.append(reason_dict)
        return data

    def get_medicine_name(self, obj):
        return obj.medicine.medicine_name

    def get_national_medication_code(self, obj):
        return obj.medicine.national_medication_code

    def get_units_per_box(self, obj):
        return obj.medicine.units_per_box

    def get_plannings(self, obj):
        if_needed = self.context["request"].query_params.get('if_needed')
        special_dose = self.context["request"].query_params.get('special')
        if if_needed and special_dose:
            return PlanningProductionSerializer(
                Planning.objects.filter(medicine_planning=obj, if_needed=if_needed, special_dose=special_dose).exclude
                (is_active=False), many=True).data
        elif if_needed:
            return PlanningProductionSerializer(
                Planning.objects.filter(medicine_planning=obj, if_needed=if_needed).exclude(is_active=False),
                many=True).data
        elif special_dose:
            return PlanningProductionSerializer(
                Planning.objects.filter(medicine_planning=obj, special_dose=special_dose).exclude(is_active=False),
                many=True).data
        return PlanningProductionSerializer(
            Planning.objects.filter(medicine_planning=obj).exclude(is_active=False), many=True).data

    def get_barcode(self, obj):

        barcode_string = obj.medicine.national_medication_code
        barcode = BarcodeDrawing("{}".format(barcode_string))
        binaryStuff = barcode.asString('png')
        base64EncodedStr = base64.b64encode(binaryStuff).decode('utf-8')
        return base64EncodedStr


class AssignCentreModuleSerializer(serializers.ModelSerializer):
    patients = serializers.SerializerMethodField()

    class Meta:
        model = AssignCentreModule
        fields = ("id", "module_name", "patients")

    def get_patients(self, obj):

        patients_data = []
        for patient in obj.patients.all():
            packable = self.context["request"].query_params.get('packable')
            non_packable = self.context["request"].query_params.get('non_packable')
            if packable and non_packable:
                result = ProductionCreatePlanningSerializer(patient.medicine_plannings.all(), many=True,
                                                            context={'request': self.context['request']}).data
            elif packable:
                result = ProductionCreatePlanningSerializer(patient.medicine_plannings.filter(
                    medicine__non_packable_treatment=packable), many=True,
                    context={'request': self.context['request']}).data
            elif non_packable:
                result = ProductionCreatePlanningSerializer(patient.medicine_plannings.filter(
                    medicine__non_packable_treatment=non_packable), many=True,
                    context={'request': self.context['request']}).data
            else:
                result = ProductionCreatePlanningSerializer(patient.medicine_plannings.all(), many=True,
                                                            context={'request': self.context['request']}).data

            stock_details = stock_calculation(self, result,
                                              datetime.strptime(self.context["request"].
                                                                query_params.get('from'), '%Y-%m-%d').date(),
                                              datetime.strptime(self.context["request"].
                                                                query_params.get('to'), '%Y-%m-%d').date())
            if stock_details:
                data = {"id": patient.id, "last_name": patient.last_name, "first_name": patient.first_name,
                        "full_name": patient.full_name,
                        "label_printing": patient.label_printing, "status": patient.status,
                        "room_number": patient.room_number, "details": stock_details,
                        "module_name": patient.assign_centre_module.module_name,
                        "hospital_name": patient.hospital.hospital_name}
                patients_data.append(data)
        return patients_data


class SimulatorDashboardSerializer(serializers.ModelSerializer):
    assign_centre_modules = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = ("id", "assign_centre_modules", "hospital_name")

    def get_assign_centre_modules(self, obj):
        if self.context['request'].query_params.get('module'):
            search_terms = self.context['request'].query_params.get('module')
            module_list = search_terms.split(',')
            return AssignCentreModuleSerializer(
                obj.assign_centre_modules.filter(reduce(operator.or_, (Q(id=term) for term in module_list))), many=True,
                context={'request': self.context['request']}).data

        return AssignCentreModuleSerializer(obj.assign_centre_modules.all(), many=True,
                                            context={'request': self.context['request']}).data


class InvoiceStockMovementSerializer(serializers.ModelSerializer):
    medicine_name = serializers.SerializerMethodField()
    national_medication_code = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    box_quantity = serializers.SerializerMethodField()

    class Meta:
        model = PatientStockManagement
        fields = "__all__"

    def get_medicine_name(self, obj):
        return obj.medicine_planning.medicine.medicine_name

    def get_national_medication_code(self, obj):
        return obj.medicine_planning.medicine.national_medication_code

    def get_user_name(self, obj):
        return obj.user.full_name

    def get_box_quantity(self, obj):
        if obj.medicine_planning.medicine.units_per_box:
            return math.ceil(obj.quantity / int(obj.medicine_planning.medicine.units_per_box))
        return ""
