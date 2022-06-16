from abc import ABC

from rest_framework import serializers

from planning.models import MedicinePlanning, Planning
from planning.serializers import *


class PlanningPharmacistSerializer(serializers.ModelSerializer):
    posology_plannings = StandardModeIntakeSerializer(many=True)
    each_posology_plannings = EachPosologySerializer(many=True)
    from_to_posology_plannings = FromToPosologySerializer(many=True)
    medicine = serializers.SerializerMethodField()
    productions = serializers.SerializerMethodField()

    class Meta:
        model = Planning
        exclude = ("created_at", "updated_at")

    def get_medicine(self, obj):
        medicine_data = obj.medicine_planning.medicine
        return {"medicine_name": medicine_data.medicine_name,
                "national_medication_code": medicine_data.national_medication_code,
                "units_per_box": medicine_data.units_per_box, "type": medicine_data.type}

    def get_productions(self, obj):
        produced_data = [{"id": data.id,
                          "from_date": data.from_date,
                          "to_date": data.to_date,
                          "planning": data.planning.id} for data in obj.productions.all()]
        return produced_data


class PharmacistControlSerializer(serializers.ModelSerializer):
    # plannings = serializers.SerializerMethodField()
    plannings = serializers.SerializerMethodField()
    planning_count = serializers.SerializerMethodField()
    absence_reasons = serializers.SerializerMethodField()
    medicine_data = serializers.SerializerMethodField()

    class Meta:
        model = MedicinePlanning
        exclude = ("created_at", "updated_at")

    def get_plannings(self, obj):
        return PlanningPharmacistSerializer(Planning.objects.filter(medicine_planning=obj).exclude(
            is_validated=True), many=True).data

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

    # def get_plannings(self, obj):
    #     return obj.plannings.all()


class ValidatePlanningSerializer(serializers.Serializer):
    patients = serializers.ListField()

    # class Meta:
    #     model = Planning
    #     exclude = ("created_at", "updated_at")

    # def create(self, validated_data):
