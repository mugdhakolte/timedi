from rest_framework import serializers

from patient.models import *
from planning.serializers import *
from history.utils import get_action
from planning.models import MedicinePlanning


class HistorySerializer(serializers.ModelSerializer):
    def __init__(self, model, *args, fields='__all__', **kwargs):
        self.Meta.model = model
        self.Meta.fields = fields
        super().__init__()

    class Meta:
        pass


class HistoryIntakeMomentSerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField()

    class Meta:
        model = IntakeMoment
        fields = ["id", "intake_time", "dosage_amount", "posology_planning", "history"]

    def get_history(self, obj):
        model = obj.history.__dict__['model']
        fields = '__all__'
        serializer = HistorySerializer(model, obj.history.all().order_by('-history_date'), fields=fields, many=True)
        serializer.is_valid()
        return serializer.data


class HistoryStandardModeIntakeSerializer(serializers.ModelSerializer):
    intake_moments = HistoryIntakeMomentSerializer(many=True)
    history = serializers.SerializerMethodField()

    class Meta:
        model = PosologyPlanning
        # fields = ["id", "day", "planning", "intake_moments"]
        exclude = ("created_at", "updated_at",)

    def get_history(self, obj):
        model = obj.history.__dict__['model']
        fields = '__all__'
        serializer = HistorySerializer(model, obj.history.all().order_by('-history_date'), fields=fields, many=True)
        serializer.is_valid()
        return serializer.data


class HistoryEachPosologySerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField()

    class Meta:
        model = EachPosologyPlanning
        fields = ["id", "each_posology_days", "each_x_days", "odd_days", "even_days", "planning", "dosage_amount",
                  "intake_time", "history"]

    def get_history(self, obj):
        model = obj.history.__dict__['model']
        fields = '__all__'
        serializer = HistorySerializer(model, obj.history.all().order_by('-history_date'), fields=fields, many=True)
        serializer.is_valid()
        return serializer.data


class HistoryFromToPosologySerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField()

    class Meta:
        model = FromToPosologyPlanning
        fields = ["id", "starts_at", "ends_at", "month_lapse", "planning", "dosage_amount", "intake_time", "history"]

    def get_history(self, obj):
        model = obj.history.__dict__['model']
        fields = '__all__'
        serializer = HistorySerializer(model, obj.history.all().order_by('-history_date'), fields=fields, many=True)
        serializer.is_valid()
        return serializer.data


class HistoryPlanningSerializer(serializers.ModelSerializer):
    posology_plannings = serializers.SerializerMethodField()
    each_posology_plannings = HistoryEachPosologySerializer(many=True)
    from_to_posology_plannings = HistoryFromToPosologySerializer(many=True)
    history = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    medicine_name = serializers.SerializerMethodField()
    non_packable_treatment = serializers.SerializerMethodField()
    national_medication_code = serializers.SerializerMethodField()

    class Meta:
        model = Planning
        exclude = ("created_at", "updated_at")

    def get_posology_plannings(self, obj):
        qs = obj.posology_plannings.all()
        order = [day[0] for day in DAYS]
        return HistoryStandardModeIntakeSerializer(sorted(qs, key=lambda x: order.index(x.day)), many=True).data

    def get_history(self, obj):
        model = obj.history.__dict__['model']
        fields = '__all__'
        serializer = HistorySerializer(model, obj.history.all().order_by('-history_date'), fields=fields, many=True)
        serializer.is_valid()
        return serializer.data

    def get_medicine_name(self, obj):
        return obj.medicine_planning.medicine.medicine_name

    def get_patient_name(self, obj):
        return obj.medicine_planning.patient.full_name

    def get_national_medication_code(self, obj):
        return obj.medicine_planning.medicine.national_medication_code

    def get_non_packable_treatment(self, obj):
        return obj.medicine_planning.medicine.non_packable_treatment


class PlanningHistorySerializer(serializers.ModelSerializer):
    history_data = serializers.SerializerMethodField()

    class Meta:
        model = Planning
        exclude = ("created_at", "updated_at")

    def get_history_data(self, obj):
        data = []
        if obj.posology_type in ("specific_posology", "cycle_posology", "standard_posology"):
            for his_obj in obj.history.all().order_by("-history_date"):
                if not his_obj.next_record:
                    posology_data = {}
                    for posoloy_planning in obj.posology_plannings.all():
                        for posoloy_planning_his_obj in posoloy_planning.history.filter(
                                history_date__gte=his_obj.history_date):
                            for intake_moment in posoloy_planning.intake_moments.all():
                                for intake_moment_obj in intake_moment.history.filter(
                                        history_date__gte=posoloy_planning_his_obj.history_date):
                                    posology_data["intake_time"] = intake_moment_obj.intake_time
                                    posology_data["dosage_amount"] = str(intake_moment_obj.dosage_amount)
                                    posology_data["date"] = str(his_obj.history_date.date())
                                    posology_data["type"] = obj.posology_type
                                    posology_data["action"] = get_action(his_obj.history_type, his_obj.is_active)
                            posology_data["day"] = posoloy_planning_his_obj.day
                            data.append(posology_data)
                else:
                    posology_data = {}
                    for posoloy_planning in obj.posology_plannings.all():
                        for posoloy_planning_his_obj in posoloy_planning.history.filter(
                                history_date__gte=his_obj.history_date,
                                history_date__lte=his_obj.next_record.history_date):
                            for intake_moment in posoloy_planning.intake_moments.all():
                                if posoloy_planning_his_obj.next_record:
                                    for intake_moment_obj in intake_moment.history.filter(
                                            history_date__gte=posoloy_planning_his_obj.history_date,
                                            history_date__lte=posoloy_planning_his_obj.next_record.history_date):
                                        posology_data["intake_time"] = intake_moment_obj.intake_time
                                        posology_data["dosage_amount"] = str(intake_moment_obj.dosage_amount)
                                        posology_data["date"] = str(his_obj.history_date.date())
                                        posology_data["type"] = obj.posology_type
                                        posology_data["action"] = get_action(his_obj.history_type, his_obj.is_active)
                                else:
                                    for intake_moment_obj in intake_moment.history.filter(
                                            history_date__gte=posoloy_planning_his_obj.history_date):
                                        posology_data["intake_time"] = intake_moment_obj.intake_time
                                        posology_data["dosage_amount"] = str(intake_moment_obj.dosage_amount)
                                        posology_data["date"] = str(his_obj.history_date.date())
                                        posology_data["type"] = obj.posology_type
                                        posology_data["action"] = get_action(his_obj.history_type, his_obj.is_active)

                            posology_data["day"] = posoloy_planning_his_obj.day
                            data.append(posology_data)

        elif obj.posology_type == "from_to_posology":
            for his_obj in obj.history.all().order_by("-history_date"):
                if not his_obj.next_record:
                    from_to_posology_data = {}
                    for from_to_posology_planning in obj.from_to_posology_plannings.all():
                        for from_to_posology_planning_his_obj in from_to_posology_planning.history. \
                                filter(history_date__gte=his_obj.history_date):
                            from_to_posology_data["intake_time"] = ','.join(
                                from_to_posology_planning_his_obj.intake_time)
                            from_to_posology_data["dosage_amount"] = str(
                                from_to_posology_planning_his_obj.dosage_amount)
                            from_to_posology_data["date"] = str(his_obj.history_date.date())
                            from_to_posology_data["type"] = obj.posology_type
                            from_to_posology_data["day"] = "-"
                            from_to_posology_data["action"] = get_action(his_obj.history_type, his_obj.is_active)
                            data.append(from_to_posology_data)
                else:
                    from_to_posology_data = {}
                    for from_to_posology_planning in obj.from_to_posology_plannings.all():
                        for from_to_posology_planning_his_obj in from_to_posology_planning.history. \
                                filter(history_date__gte=his_obj.history_date,
                                       history_date__lte=his_obj.next_record.history_date):
                            from_to_posology_data["intake_time"] = ','.join(
                                from_to_posology_planning_his_obj.intake_time)
                            from_to_posology_data["dosage_amount"] = from_to_posology_planning_his_obj.dosage_amount
                            from_to_posology_data["date"] = str(his_obj.history_date.date())
                            from_to_posology_data["type"] = obj.posology_type
                            from_to_posology_data["day"] = "-"
                            from_to_posology_data["action"] = get_action(his_obj.history_type, his_obj.is_active)

        elif obj.posology_type == "each_posology":
            for his_obj in obj.history.all().order_by("-history_date"):
                if not his_obj.next_record:
                    each_posology_data = {}
                    for each_posology_planning in obj.each_posology_plannings.all():
                        for each_posology_planning_his_obj in each_posology_planning.history. \
                                filter(history_date__gte=his_obj.history_date):
                            each_posology_data["intake_time"] = ','.join(each_posology_planning_his_obj.intake_time)
                            each_posology_data["dosage_amount"] = str(each_posology_planning_his_obj.dosage_amount)
                            each_posology_data["date"] = str(his_obj.history_date.date())
                            each_posology_data["type"] = obj.posology_type
                            each_posology_data["day"] = "-"
                            each_posology_data["action"] = get_action(his_obj.history_type, his_obj.is_active)
                            data.append(each_posology_data)
                else:
                    each_posology_data = {}
                    for each_posology_planning in obj.each_posology_plannings.all():
                        for each_posology_planning_his_obj in each_posology_planning.history. \
                                filter(history_date__gte=his_obj.history_date,
                                       history_date__lte=his_obj.next_record.history_date):
                            each_posology_data["intake_time"] = ','.join(each_posology_planning_his_obj.intake_time)
                            each_posology_data["dosage_amount"] = str(each_posology_planning_his_obj.dosage_amount)
                            each_posology_data["date"] = str(his_obj.history_date.date())
                            each_posology_data["type"] = obj.posology_type
                            each_posology_data["day"] = "-"
                            each_posology_data["action"] = get_action(his_obj.history_type, his_obj.is_active)
                            data.append(each_posology_data)
        return data


class PlanningDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planning
        exclude = ("created_at", "updated_at")


# class HistoryPlanningSerializer(serializers.ModelSerializer):
#     # posology_plannings = serializers.SerializerMethodField()
#     # each_posology_plannings = EachPosologySerializer(many=True)
#     # from_to_posology_plannings = FromToPosologySerializer(many=True)
#     medicine = serializers.SerializerMethodField()
#     history = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Planning
#         exclude = ("created_at", "updated_at")
#
#     def get_medicine(self, obj):
#         medicine_data = obj.medicine_planning.medicine
#         return {"medicine_name": medicine_data.medicine_name,
#                 "national_medication_code": medicine_data.national_medication_code,
#                 "units_per_box": medicine_data.units_per_box, "type": medicine_data.type}
#
#     # def get_posology_plannings(self, obj):
#     #     qs = obj.posology_plannings.all()
#     #     order = [day[0] for day in DAYS]
#     #     return StandardModeIntakeSerializer(sorted(qs, key=lambda x: order.index(x.day)), many=True).data
#
#     # model = obj.history.__dict__['model']
#     # fields = '__all__'
#     # serializer = HistorySerializer(model, obj.history.all().order_by('-history_date'), fields=fields, many=True)
#     # serializer.is_valid()
#
#     def get_history(self, obj):
#         data = []
#         if obj.posology_type in ("specific_posology", "cycle_posology", "standard_posology"):
#             for his_obj in obj.history.all().order_by("-history_date"):
#                 planning_data = {"start_date": his_obj.start_date, "end_date": his_obj.end_date,
#                                                 "if_needed": his_obj.if_needed, "comment": his_obj.comment,
#                                                 "posology_type": his_obj.posology_type,
#                                                 "posology_plannings": [],
#                                                 "history_date": his_obj.history_date,
#                                                 "history_type": his_obj.history_type}
#                 if not his_obj.next_record:
#                     posology_data = {}
#                     for posoloy_planning in obj.posology_plannings.all():
#                         for posoloy_planning_his_obj in posoloy_planning.history.filter(
#                                 history_date__gte=his_obj.history_date):
#                             for intake_moment in posoloy_planning.intake_moments.all():
#                                 posology_data["intake_moments"] = []
#                                 for intake_moment_obj in intake_moment.history.filter(
#                                         history_date__gte=posoloy_planning_his_obj.history_date):
#                                     intake_dict = {
#                                                     "intake_time":intake_moment_obj.intake_time,
#                                                     "dosage_amount":intake_moment_obj.dosage_amount,
#                                                     "type":intake_moment_obj.history_type,
#                                                     "date":intake_moment_obj.history_date,
#                                                    }
#                                     posology_data["intake_moments"].append(intake_dict)
#                                     posology_data["date"] = his_obj.history_date.date()
#                                     posology_data["type"] = obj.posology_type
#                             posology_data["day"] = posoloy_planning_his_obj.day
#                             planning_data["posology_plannings"].append(posology_data)
#
#                 else:
#                     posology_data = {}
#                     for posoloy_planning in obj.posology_plannings.all():
#                         for posoloy_planning_his_obj in posoloy_planning.history.filter(
#                                 history_date__gte=his_obj.history_date,
#                                 history_date__lte=his_obj.next_record.history_date):
#                             for intake_moment in posoloy_planning.intake_moments.all():
#                                 posology_data["intake_moments"] = []
#                                 for intake_moment_obj in intake_moment.history.filter(
#                                         history_date__gte=posoloy_planning_his_obj.history_date):
#                                     intake_dict = {
#                                         "intake_time": intake_moment_obj.intake_time,
#                                         "dosage_amount": intake_moment_obj.dosage_amount,
#                                         "type": intake_moment_obj.history_type,
#                                         "date": intake_moment_obj.history_date,
#                                     }
#                                     posology_data["intake_moments"].append(intake_dict)
#                                     posology_data["date"] = his_obj.history_date.date()
#                                     posology_data["type"] = obj.posology_type
#                             posology_data["day"] = posoloy_planning_his_obj.day
#                             planning_data["posology_plannings"].append(posology_data)
#                 data.append(planning_data)
#
#         elif obj.posology_type == "from_to_posology":
#             for his_obj in obj.history.all().order_by("-history_date"):
#                 from_to_posology_history_data = {"start_date": his_obj.start_date, "end_date": his_obj.end_date,
#                                                  "if_needed": his_obj.if_needed, "comment": his_obj.comment,
#                                                  "posology_type": his_obj.posology_type,
#                                                  "from_to_posology_plannings": [],
#                                                  "history_date": his_obj.history_date,
#                                                  "history_type": his_obj.history_type}
#                 if not his_obj.next_record:
#                     from_to_posology_data = {}
#                     for from_to_posology_planning in obj.from_to_posology_plannings.all():
#                         for from_to_posology_planning_his_obj in from_to_posology_planning.history. \
#                                 filter(history_date__gte=his_obj.history_date):
#                             from_to_posology_data["intake_time"] = from_to_posology_planning_his_obj.intake_time
#                             from_to_posology_data["dosage_amount"] = from_to_posology_planning_his_obj.dosage_amount
#                             from_to_posology_data["month_lapse"] = from_to_posology_planning_his_obj.month_lapse
#                             from_to_posology_data["starts_at"] = from_to_posology_planning_his_obj.starts_at
#                             from_to_posology_data["ends_at"] = from_to_posology_planning_his_obj.ends_at
#                             from_to_posology_data["history_date"] = str(his_obj.history_date.date())
#                             from_to_posology_data["history_type"] = from_to_posology_planning_his_obj.history_type
#                             from_to_posology_history_data["from_to_posology_plannings"].append(from_to_posology_data)
#                 else:
#                     from_to_posology_data = {}
#                     for from_to_posology_planning in obj.from_to_posology_plannings.all():
#                         for from_to_posology_planning_his_obj in from_to_posology_planning.history. \
#                                 filter(history_date__gte=his_obj.history_date,
#                                        history_date__lte=his_obj.next_record.history_date):
#                             from_to_posology_data["intake_time"] = from_to_posology_planning_his_obj.intake_time
#                             from_to_posology_data["dosage_amount"] = from_to_posology_planning_his_obj.dosage_amount
#                             from_to_posology_data["month_lapse"] = from_to_posology_planning_his_obj.month_lapse
#                             from_to_posology_data["starts_at"] = from_to_posology_planning_his_obj.starts_at
#                             from_to_posology_data["ends_at"] = from_to_posology_planning_his_obj.ends_at
#                             from_to_posology_data["history_date"] = str(his_obj.history_date.date())
#                             from_to_posology_data["history_type"] = from_to_posology_planning_his_obj.history_type
#                             from_to_posology_history_data["from_to_posology_plannings"].append(from_to_posology_data)
#                 data.append(from_to_posology_history_data)
#
#         elif obj.posology_type == "each_posology":
#             for his_obj in obj.history.all().order_by("-history_date"):
#                 each_posology_history_data = {"start_date": his_obj.start_date, "end_date": his_obj.end_date,
#                                                  "if_needed": his_obj.if_needed, "comment": his_obj.comment,
#                                                  "posology_type": his_obj.posology_type,
#                                                  "each_posology_plannings": [],
#                                                  "history_date": his_obj.history_date,
#                                                  "history_type": his_obj.history_type}
#                 if not his_obj.next_record:
#                     each_posology_data = {}
#                     for from_to_posology_planning in obj.each_posology_plannings.all():
#                         for from_to_posology_planning_his_obj in from_to_posology_planning.history. \
#                                 filter(history_date__gte=his_obj.history_date):
#                             each_posology_data["intake_time"] = from_to_posology_planning_his_obj.intake_time
#                             each_posology_data["dosage_amount"] = from_to_posology_planning_his_obj.dosage_amount
#                             each_posology_data["each_x_days"] = from_to_posology_planning_his_obj.each_x_days
#                             each_posology_data["each_posology_days"] = from_to_posology_planning_his_obj.each_posology_days
#                             each_posology_data["odd_days"] = from_to_posology_planning_his_obj.odd_days
#                             each_posology_data["even_days"] = from_to_posology_planning_his_obj.even_days
#                             each_posology_data["history_date"] = str(his_obj.history_date.date())
#                             each_posology_data["history_type"] = from_to_posology_planning_his_obj.history_type
#                             each_posology_history_data["each_posology_plannings"].append(each_posology_data)
#                 else:
#                     each_posology_data = {}
#                     for from_to_posology_planning in obj.each_posology_plannings.all():
#                         for from_to_posology_planning_his_obj in from_to_posology_planning.history. \
#                                 filter(history_date__gte=his_obj.history_date,
#                                        history_date__lte=his_obj.next_record.history_date):
#                             each_posology_data["intake_time"] = from_to_posology_planning_his_obj.intake_time
#                             each_posology_data["dosage_amount"] = from_to_posology_planning_his_obj.dosage_amount
#                             each_posology_data["each_x_days"] = from_to_posology_planning_his_obj.each_x_days
#                             each_posology_data["each_posology_days"] = from_to_posology_planning_his_obj.each_posology_days
#                             each_posology_data["odd_days"] = from_to_posology_planning_his_obj.odd_days
#                             each_posology_data["even_days"] = from_to_posology_planning_his_obj.even_days
#                             each_posology_data["history_date"] = str(his_obj.history_date.date())
#                             each_posology_data["history_type"] = from_to_posology_planning_his_obj.history_type
#                             each_posology_history_data["each_posology_plannings"].append(each_posology_data)
#                 data.append(each_posology_history_data)
#         return data
#
#
# class HistoryMedicinePlanningSerializer(serializers.ModelSerializer):
#     plannings = HistoryPlanningSerializer(many=True, read_only=True)
#     planning_count = serializers.SerializerMethodField()
#     absence_reasons = serializers.SerializerMethodField()
#     medicine_data = serializers.SerializerMethodField()
#
#     class Meta:
#         model = MedicinePlanning
#         exclude = ("created_at", "updated_at")
#
#     def get_planning_count(self, obj):
#         return obj.plannings.all().count()
#
#     def get_absence_reasons(self, obj):
#         data = []
#         for reason in obj.patient.absence_reasons.all():
#             reason_dict = {"id": reason.id, "reason": reason.reason, "release_date": reason.release_date,
#                            "return_date": reason.return_date, "no_return_date": reason.no_return_date}
#             data.append(reason_dict)
#         return data
#
#     def get_medicine_data(self, obj):
#         medicine_data = obj.medicine
#         return {"id": medicine_data.id,
#                 "medicine_name": medicine_data.medicine_name,
#                 "national_medication_code": medicine_data.national_medication_code,
#                 "units_per_box": medicine_data.units_per_box,
#                 "type": medicine_data.type,
#                 "non_packable_treatment": medicine_data.non_packable_treatment}

class PlanningHistoryTreatmentSerializer(serializers.ModelSerializer):
    posology_plannings = StandardModeIntakeSerializer(many=True)
    each_posology_plannings = EachPosologySerializer(many=True)
    from_to_posology_plannings = FromToPosologySerializer(many=True)
    productions = serializers.SerializerMethodField()
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

    def get_productions(self, obj):
        produced_data = [{"id": data.id,
                          "from_date": data.from_date,
                          "to_date": data.to_date,
                          "planning": data.planning.id} for data in obj.productions.all()]
        return produced_data

class HistoryTreatmentPlanningSerializer(serializers.ModelSerializer):
    plannings = serializers.SerializerMethodField()
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

    def get_plannings(self, obj):
        from_date = self.context.get("from_date")
        to_date = self.context.get("to_date")
        return PlanningHistoryTreatmentSerializer(
            Planning.objects.filter(start_date__gte=from_date, start_date__lte=to_date,
                                    medicine_planning=obj).exclude
            (is_active=False), many=True).data

