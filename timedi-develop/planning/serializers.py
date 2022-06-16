from rest_framework import fields
from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer

from planning.models import *
from planning.choices import DAYS


class IntakeMomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntakeMoment
        fields = ["id", "intake_time", "dosage_amount", "posology_planning"]
        extra_kwargs = {
            "id": {"required": False},
            "posology_planning": {"required": False,
                                  "write_only": True}
        }


class StandardModeIntakeSerializer(WritableNestedModelSerializer):
    intake_moments = IntakeMomentSerializer(many=True)
    planning = serializers.UUIDField(required=False, write_only=True)

    class Meta:
        model = PosologyPlanning
        # fields = ["id", "day", "planning", "intake_moments"]
        exclude = ("created_at", "updated_at",)
        extra_kwargs = {
            "id": {"required": False},
            # "planning": {"required": False,
            #              "write_only": True}
        }

    def get_validators(self):
        """
        Determine the set of validators to use when instantiating serializer.
        """
        # If the validators have been declared explicitly then use that.
        validators = getattr(getattr(self, 'Meta', None), 'validators', None)
        if validators is not None:
            return validators[:]
        # Otherwise use the default set of validators.
        return (
            # self.get_unique_together_validators() +
            self.get_unique_for_date_validators()
        )


class StandardModeSerializer(WritableNestedModelSerializer):
    posology_plannings = StandardModeIntakeSerializer(many=True)

    class Meta:
        model = Planning
        exclude = ("created_at", "updated_at",)

    def validate(self, data):
        """
        validation for start date and end date
        """
        # if self.context['request'].method == "POST":
        #     if data['start_date'] < datetime.date.today():
        #         raise serializers.ValidationError({"start_date": "start date should be greater than today."})

        # if self.context['request'].method == "PUT":
        #     if data['start_date'] < self.instance.start_date and data['start_date'] < datetime.date.today():
        #         raise serializers.ValidationError({"start_date": "start date should be greater than today."})

        if data["end_date"] and data['start_date'] > data['end_date']:
            raise serializers.ValidationError({"end_date": "End date should be greater than start date."})
        return data


class CycleModeIntakeSerializer(WritableNestedModelSerializer):
    planning = serializers.UUIDField(required=False, write_only=True)
    intake_moments = IntakeMomentSerializer(many=True)

    class Meta:
        model = PosologyPlanning
        fields = ["id", "day", "planning", "intake_moments", ]
        extra_kwargs = {
            "id": {"required": False},
        }

    def get_validators(self):
        """
        Determine the set of validators to use when instantiating serializer.
        """
        # If the validators have been declared explicitly then use that.
        validators = getattr(getattr(self, 'Meta', None), 'validators', None)
        if validators is not None:
            return validators[:]
        # Otherwise use the default set of validators.
        return (
            # self.get_unique_together_validators() +
            self.get_unique_for_date_validators()
        )


class CyclePosologySerializer(WritableNestedModelSerializer):
    posology_plannings = CycleModeIntakeSerializer(many=True)

    class Meta:
        model = Planning
        fields = ["id", "start_date", "end_date", "if_needed", "special_dose", "comment",
                  "medicine_planning", "posology_type", "is_validated", "posology_plannings", "active_period",
                  "inactive_period"]

        extra_kwargs = {
            "id": {"required": False},
            "active_period": {"required": True},
            "inactive_period": {"required": True}
        }

    def validate(self, data):
        """
        validation for start date and end date
        """
        # if self.context['request'].method == "POST":
        #     if data['start_date'] < datetime.date.today():
        #         raise serializers.ValidationError({"start_date": "start date should be greater than today."})

        # if self.context['request'].method == "PUT":
        #     if data['start_date'] < self.instance.start_date and data['start_date'] < datetime.date.today():
        #         raise serializers.ValidationError({"start_date": "start date should be greater than today."})

        if data["end_date"] and data['start_date'] > data['end_date']:
            raise serializers.ValidationError({"end_date": "End date should be greater than start date."})
        return data


class EachPosologySerializer(serializers.ModelSerializer):
    intake_time = fields.MultipleChoiceField(choices=INTAKE_TIME)
    planning = serializers.UUIDField(required=False, write_only=True)

    class Meta:
        model = EachPosologyPlanning
        fields = ["id", "each_posology_days", "each_x_days", "odd_days", "even_days", "planning", "dosage_amount",
                  "intake_time"]
        extra_kwargs = {
            "id": {"required": False},
        }


class EachPosologyPlanningSerializer(WritableNestedModelSerializer):
    each_posology_plannings = EachPosologySerializer(many=True)

    def validate(self, data):
        """
        validation for start date and end date
        """
        # if self.context['request'].method == "POST":
        #     if data['start_date'] < datetime.date.today():
        #         raise serializers.ValidationError({"start_date": "start date should be greater than today."})

        # if self.context['request'].method == "PUT":
        #     if data['start_date'] < self.instance.start_date and data['start_date'] < datetime.date.today():
        #         raise serializers.ValidationError({"start_date": "start date should be greater than today."})

        if data["end_date"] and data['start_date'] > data['end_date']:
            raise serializers.ValidationError({"end_date": "End date should be greater than start date."})
        return data

    class Meta:
        model = Planning
        fields = ["start_date", "end_date", "if_needed", "special_dose", "comment",
                  "medicine_planning", "is_validated", "posology_type", "each_posology_plannings"]


class FromToPosologySerializer(serializers.ModelSerializer):
    intake_time = fields.MultipleChoiceField(choices=INTAKE_TIME)
    planning = serializers.UUIDField(required=False, write_only=True)

    class Meta:
        model = FromToPosologyPlanning
        fields = ["id", "starts_at", "ends_at", "month_lapse", "planning", "dosage_amount", "intake_time"]
        extra_kwargs = {
            "id": {"required": False},
        }


class FromToPosologyPlanningSerializer(WritableNestedModelSerializer):
    from_to_posology_plannings = FromToPosologySerializer(many=True, )

    def validate(self, data):
        """
        validation for start date and end date
        """
        # if self.context['request'].method == "POST":
        #     if data['start_date'] < datetime.date.today():
        #         raise serializers.ValidationError({"start_date": "start date should be greater than today."})

        # if self.context['request'].method == "PUT":
        #     if data['start_date'] < self.instance.start_date and data['start_date'] < datetime.date.today():
        #         raise serializers.ValidationError({"start_date": "start date should be greater than today."})

        if data["end_date"] and data['start_date'] > data['end_date']:
            raise serializers.ValidationError({"end_date": "End date should be greater than start date."})
        return data

    class Meta:
        model = Planning
        fields = ["start_date", "end_date", "if_needed", "special_dose", "comment",
                  "medicine_planning", "is_validated", "posology_type", "from_to_posology_plannings"]


class PlanningSerializer(serializers.ModelSerializer):
    posology_plannings = serializers.SerializerMethodField()
    each_posology_plannings = EachPosologySerializer(many=True)
    from_to_posology_plannings = FromToPosologySerializer(many=True)
    medicine = serializers.SerializerMethodField()
    productions = serializers.SerializerMethodField()

    class Meta:
        model = Planning
        exclude = ("created_at", "updated_at")

    # def get_medicine_name
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

    def get_posology_plannings(self, obj):
        qs = obj.posology_plannings.all()
        order = [day[0] for day in DAYS]
        return StandardModeIntakeSerializer(sorted(qs, key=lambda x: order.index(x.day)), many=True).data


class MedicinePlanningSerializer(serializers.ModelSerializer):
    plannings = PlanningSerializer(many=True, read_only=True)
    planning_count = serializers.SerializerMethodField()
    absence_reasons = serializers.SerializerMethodField()
    medicine_data = serializers.SerializerMethodField()

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


class PatientStockManagementSerializer(serializers.ModelSerializer):
    user = serializers.UUIDField(required=False)
    type = serializers.CharField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = PatientStockManagement
        exclude = ("updated_at",)

    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user.id
        quantity = validated_data['quantity']
        validated_data['type'] = 'in'
        validated_data['description'] = 'manual'
        if quantity < 0:
            validated_data['type'] = 'out'
            validated_data['description'] = 'manual'
        stock = PatientStockManagement.objects.create(**validated_data)
        return stock


class PatientStockManagementListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = PatientStockManagement
        exclude = ("updated_at",)

    def get_user(self, obj):
        if obj.user:
            return "{}".format(obj.user.full_name)
        else:
            return "Null"
