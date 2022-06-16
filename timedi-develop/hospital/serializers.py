"""
Serializers for hospital module.
"""
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework import fields

from hospital.models import (Hospital, ProductionSetting, Days, Intake_Time, Moments, HospitalStockManagement)
from patient.models import (IntermediateProduction, AssignCentreModule, Application, Patient)


class PatientListSerialier(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "full_name"]


class AssignCentreModuleSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    assign_centre_module_type = serializers.CharField(default="hospital")

    class Meta:
        model = AssignCentreModule
        fields = ["id", 'module_name', 'hospital', 'assign_centre_module_type', 'patients_count']
        extra_kwargs = {
            "assign_centre_module_type": {"write_only": True},
            "hospital": {"write_only": True},
            'patients_count': {"read_only": True}
        }


class ApplicationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    application_type = serializers.CharField(default="hospital")

    class Meta:
        model = Application
        fields = "__all__"
        extra_kwargs = {
            "hospital": {"write_only": True},
            "patient": {"write_only": True}
        }


class ProductionSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionSetting
        exclude = ("created_at", "updated_at")


class IntermediateProductionSerializer(serializers.ModelSerializer):
    days = fields.MultipleChoiceField(choices=Days)
    intake_moments = fields.MultipleChoiceField(choices=Moments, required=False)
    floors = serializers.ListField(required=False)
    medicines = serializers.ListField(required=False)
    time = fields.MultipleChoiceField(choices=Intake_Time)
    production_type = serializers.CharField(default="hospital")

    class Meta:
        model = IntermediateProduction
        exclude = ("created_at", "updated_at", "patient",)


class HospitalStockManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalStockManagement
        exclude = ("created_at", "updated_at",)


class HospitalCreateSerializer(serializers.ModelSerializer):
    applications = ApplicationSerializer(many=True, required=False)
    assign_centre_modules = AssignCentreModuleSerializer(many=True, required=False)
    patient_assign_modules = serializers.ListField(required=False, )

    class Meta:
        model = Hospital
        exclude = ("created_at", "updated_at", "account", "user")

    def create(self, validated_data):
        applications_validated_data = validated_data.pop('applications', [])
        if len(applications_validated_data) > 5:
            raise serializers.ValidationError({"applications": _("Each Hospital must have only 5 Applications")})
        centre_modules_validated_data = validated_data.pop('assign_centre_modules', [])
        validated_data['account_id'] = self.context['request'].user.account_id
        validated_data['user_id'] = self.context['request'].user.id
        hospital = Hospital.objects.create(**validated_data)
        applications_serializer = self.fields['applications']
        for app in applications_validated_data:
            app['hospital'] = hospital
        application = applications_serializer.create(applications_validated_data)

        centre_module_serializer = self.fields['assign_centre_modules']
        for centre_module in centre_modules_validated_data:
            centre_module["hospital"] = hospital
        centre_modules = centre_module_serializer.create(centre_modules_validated_data)
        return hospital

    def update(self, instance, validated_data):
        applications = validated_data.pop('applications', [])
        centre_modules = validated_data.pop('assign_centre_modules', [])
        patient_centre_modules = validated_data.pop("patient_assign_modules", [])
        if len(applications) > 5:
            raise serializers.ValidationError({"applications": _("Each Hospital must have only 5 Applications")})
        super(HospitalCreateSerializer, self).update(instance, validated_data)
        instance.save()
        keep_apps = []
        keep_modules = []
        for application in applications:
            if "id" in application.keys() and Application.objects.filter(id=application["id"]).exists():
                app = Application.objects.get(id=application["id"])
                app.application_name = application.get('application_name', app.application_name)
                app.application_id = application.get('application_id', app.application_id)
                app.save()
                keep_apps.append(app.id)
            else:
                app = Application.objects.create(**application, hospital=instance)
                keep_apps.append(app.id)

        for application in instance.applications.all():
            if application.id not in keep_apps:
                application.delete()

        for module in centre_modules:
            if "id" in module.keys() and AssignCentreModule.objects.filter(id=module["id"]).exists():
                assign_module = AssignCentreModule.objects.get(id=module["id"])
                assign_module.module_name = module.get('module_name', assign_module.module_name)
                assign_module.save()
                keep_modules.append(assign_module.id)
            else:
                assign_module = AssignCentreModule.objects.create(**module, hospital=instance)
                keep_modules.append(assign_module.id)
        for module in instance.assign_centre_modules.all():
            if module.id not in keep_modules:
                try:
                    module.delete()
                except IntegrityError as e:
                    raise serializers.ValidationError(
                        {"assign_centre_module":
                             _("Cannot delete centre module because it is referenced to a patient.")})

        for patient_centre_module in patient_centre_modules:
            assign_centre_module = patient_centre_module['assign_centre_module']
            for patient_id in patient_centre_module["patient"]:
                patient = Patient.objects.get(id=patient_id)
                patient.assign_centre_module_id = assign_centre_module
                patient.save()
                # patient_data = {"id": patient_id, "assign_centre_module": assign_centre_module}
                # serializer = PatientAssignModuleSerialier(patient_id, data=patient_data, partial=True)
                # serializer.is_valid(raise_exception=True)
                # serializer.save()
        return instance


class HospitalRetrieveSerializer(serializers.ModelSerializer):
    assign_centre_modules = AssignCentreModuleSerializer(many=True)
    applications = ApplicationSerializer(many=True)
    hospital_stock_management = HospitalStockManagementSerializer(many=False)
    intermediate_productions = IntermediateProductionSerializer(many=True)
    production_settings = ProductionSettingsSerializer(many=False)
    patient_assign_modules = serializers.SerializerMethodField()
    patients = PatientListSerialier(many=True)

    class Meta:
        model = Hospital
        exclude = ("created_at", "updated_at", "account", "user")

    def get_patient_assign_modules(self, obj):
        patient_assign_module = []
        for module in obj.assign_centre_modules.all():
            patient_module_data = {
                "patient": [{"id": patient.pk, "name": patient.full_name} for patient in module.patients.all()],
                "assign_centre_module": {"id": module.pk, "module_name": module.module_name}}
            patient_assign_module.append(patient_module_data)
        return patient_assign_module


class HospitalListSerializer(serializers.ModelSerializer):
    assign_centre_modules = AssignCentreModuleSerializer(many=True)
    total_modules = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Hospital
        fields = ["hospital_name", "id", "contact_person", "phone_number",
                  "active_patients", "total_patients", "total_modules", "assign_centre_modules"]

    def get_total_modules(self, obj):
        return obj.assign_centre_modules.all().count()


class HospitalAssignCentreModuleListSerializer(serializers.ModelSerializer):
    assign_centre_modules = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        fields = ["hospital_name", "id", "assign_centre_modules"]

    def get_assign_centre_modules(self, obj):
        return [{"module_name": module.module_name, "id": module.id} for module in obj.assign_centre_modules.all()]
