from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from patient.models import *
from planning.models import *
from production.models import *
from planning.serializers import *


class PatientStockManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientStockManagement
        exclude = ("updated_at",)


class DeliverySerializer(serializers.Serializer):
    hospital_id = serializers.UUIDField(required=True)
    date = serializers.DateField(required=True)


class PatientsProductionSerializer(serializers.Serializer):
    patients = serializers.ListField(required=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)

    def validate(self, data):
        """
        validation for start date and end date
        """
        if not data['patients']:
            raise serializers.ValidationError({"patients": _("patients list is empty")})

        if data['from_date'] > data['to_date']:
            raise serializers.ValidationError({"to date": _("to date should be greater than from date.")})
        return data


class ReportListSerializer(serializers.Serializer):
    hospital_id = serializers.UUIDField(required=True)
    from_date = serializers.DateField(required=True)
    to_date = serializers.DateField(required=True)

    def validate(self, data):
        """
        validation for start date and end date
        """
        if data['from_date'] > data['to_date']:
            raise serializers.ValidationError({"to date": _("to date should be greater than from date.")})
        return data


class ProductionReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        fields = ("created_at",)


class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Production
        exclude = ("created_at", "updated_at",)

    # def validate(self, data):
    #     """
    #     validation for start date and end date
    #     """
    #     # if self.context['request'].method == "POST":
    #     if data['from_date'] > data['to_date']:
    #         raise serializers.ValidationError({"to date": _("to date should be greater than from date.")})
    #     return data


class PlanningProductionSerializer(serializers.ModelSerializer):
    posology_plannings = StandardModeIntakeSerializer(many=True)
    each_posology_plannings = EachPosologySerializer(many=True)
    from_to_posology_plannings = FromToPosologySerializer(many=True)
    medicine = serializers.SerializerMethodField()

    class Meta:
        model = Planning
        fields = '__all__'

    def get_medicine(self, obj):
        medicine_data = obj.medicine_planning.medicine
        return {"medicine_name": medicine_data.medicine_name,
                "national_medication_code": medicine_data.national_medication_code,
                "units_per_box": medicine_data.units_per_box,
                "type": medicine_data.type}


class ProductionCreatePlanningSerializer(serializers.ModelSerializer):
    plannings = serializers.SerializerMethodField()
    planning_count = serializers.SerializerMethodField()
    absence_reasons = serializers.SerializerMethodField()
    medicine_data = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicinePlanning
        exclude = ("created_at", "updated_at")

    def get_planning_count(self, obj):
        return obj.plannings.all().count()

    def get_absence_reasons(self, obj):
        data = []
        for reason in obj.patient.absence_reasons.all():
            reason_dict = {"id": reason.id, "reason": reason.reason, "release_date": reason.release_date,
                           "return_date": reason.return_date, "no_return_date": reason.no_return_date}
            data.append(reason_dict)
        return data

    def get_medicine_data(self, obj):
        medicine_data = obj.medicine
        return {"id": medicine_data.id,
                "medicine_name": medicine_data.medicine_name,
                "national_medication_code": medicine_data.national_medication_code,
                "units_per_box": medicine_data.units_per_box,
                "type": medicine_data.type,
                "non_packable_treatment": medicine_data.non_packable_treatment}

    def get_plannings(self, obj):
        return PlanningProductionSerializer(Planning.objects.filter(medicine_planning=obj).exclude
                                            (is_active=False), many=True).data
        # return PlanningProductionSerializer(Planning.objects.filter(medicine_planning=obj, is_active=True),
        #                                     many=True).data

    def get_patient_name(self, obj):
        return obj.patient.full_name


class PlanningGetProductionSerializer(serializers.ModelSerializer):
    posology_plannings = StandardModeIntakeSerializer(many=True)
    each_posology_plannings = EachPosologySerializer(many=True)
    from_to_posology_plannings = FromToPosologySerializer(many=True)
    productions = ProductionSerializer(many=True)
    medicine = serializers.SerializerMethodField()

    class Meta:
        model = Planning
        # fields = '__all__'
        exclude = ('created_at', 'updated_at')

    def get_medicine(self, obj):
        medicine_data = obj.medicine_planning.medicine
        return {"medicine_name": medicine_data.medicine_name,
                "national_medication_code": medicine_data.national_medication_code,
                "units_per_box": medicine_data.units_per_box,
                "type": medicine_data.type}


class ProductionPlanningSerializer(serializers.ModelSerializer):
    plannings = serializers.SerializerMethodField()
    planning_count = serializers.SerializerMethodField()
    absence_reasons = serializers.SerializerMethodField()
    medicine_data = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicinePlanning
        exclude = ("created_at", "updated_at")

    def get_planning_count(self, obj):
        return obj.plannings.all().count()

    def get_absence_reasons(self, obj):
        data = []
        for reason in obj.patient.absence_reasons.all():
            reason_dict = {"id": reason.id, "reason": reason.reason, "release_date": reason.release_date,
                           "return_date": reason.return_date, "no_return_date": reason.no_return_date}
            data.append(reason_dict)
        return data

    def get_medicine_data(self, obj):
        medicine_data = obj.medicine
        return {"id": medicine_data.id,
                "medicine_name": medicine_data.medicine_name,
                "national_medication_code": medicine_data.national_medication_code,
                "units_per_box": medicine_data.units_per_box,
                "type": medicine_data.type,
                "non_packable_treatment": medicine_data.non_packable_treatment}

    def get_plannings(self, obj):
        return PlanningGetProductionSerializer(Planning.objects.filter(medicine_planning=obj),
                                               # .exclude(is_validated=False),
                                               many=True).data

    def get_patient_name(self, obj):
        return obj.patient.full_name


class ProductionPlanningGetSerializer(serializers.ModelSerializer):
    posology_plannings = StandardModeIntakeSerializer(many=True)
    each_posology_plannings = EachPosologySerializer(many=True)
    from_to_posology_plannings = FromToPosologySerializer(many=True)
    productions = ProductionSerializer(many=True)

    class Meta:
        model = Planning
        # fields = '__all__'
        exclude = ('created_at', 'updated_at')


class ProductionReportSerializer(serializers.ModelSerializer):
    plannings = serializers.SerializerMethodField()
    medicine_data = serializers.SerializerMethodField()
    patient_data = serializers.SerializerMethodField()

    class Meta:
        model = MedicinePlanning
        exclude = ("created_at", "updated_at")

    def get_medicine_data(self, obj):
        medicine_data = obj.medicine
        return {"id": medicine_data.id,
                "medicine_name": medicine_data.medicine_name,
                "national_medication_code": medicine_data.national_medication_code, }

    def get_plannings(self, obj):
        return ProductionPlanningGetSerializer(Planning.objects.filter(medicine_planning=obj, ).exclude(is_active=False)
                                               .exclude(is_validated=False), many=True).data

    def get_patient_data(self, obj):
        patient = obj.patient
        return {"id": patient.id,
                "name": patient.full_name,
                "doctor_name": patient.doctor_name,
                "pharmacy_holder": patient.blister_responsible,
                "address": patient.address,
                "hospital": patient.hospital.hospital_name,
                "module": patient.assign_centre_module.module_name
                }


class ProductionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionRecord
        exclude = ("created_at", "updated_at")