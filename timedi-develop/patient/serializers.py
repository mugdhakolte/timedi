"""
Serializers for hospital module.
"""

from django.utils.translation import ugettext_lazy as _
from rest_framework import fields
from rest_framework import serializers
from django.db.models import Q

from patient.models import (Patient, IntermediateProduction, AssignCentreModule, Application, AbsenceReason, Days,
                            Intake_Time, Moments, )
from hospital.models import Hospital
from hospital.serializers import (AssignCentreModuleSerializer, PatientListSerialier)


class PatientHospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'


class IntermediateProductionPatientSerializer(serializers.ModelSerializer):
    days = fields.MultipleChoiceField(choices=Days)
    intake_moments = fields.MultipleChoiceField(choices=Moments, required=False)
    floors = serializers.ListField(required=False)
    medicines = serializers.ListField(required=False)
    time = fields.MultipleChoiceField(choices=Intake_Time)
    production_type = serializers.CharField(default="patient")

    class Meta:
        model = IntermediateProduction
        exclude = ("created_at", "updated_at", "hospital",)


class AssignCentreModuleSerializerPatient(serializers.ModelSerializer):
    assign_centre_module_type = serializers.CharField(default="patient")

    class Meta:
        model = AssignCentreModule
        exclude = ("created_at", "updated_at", "hospital")
        extra_kwargs = {
            "id": {"required": False},
        }


class ApplicationSerializerPatient(serializers.ModelSerializer):
    application_type = serializers.CharField(default="patient")

    class Meta:
        model = Application
        fields = "__all__"
        extra_kwargs = {
            "id": {"required": False},
            "hospital": {"write_only": True},
            "patient": {"write_only": True}
        }


class AbsenceReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbsenceReason
        fields = '__all__'

    def create(self, validated_data):
        try:
            patient = Patient.objects.get(id=validated_data.get('patient').id)
            production_to_date = sorted(
                [production.to_date for medicine_planning in patient.medicine_plannings.all() for planning in
                 medicine_planning.plannings.all() for production in planning.productions.all()])[-1]
            if validated_data.get("release_date") <= production_to_date:
                raise serializers.ValidationError(
                    {"release_date": [_("Production already created till {}".format(production_to_date))]})


            else:
                absence_reason = AbsenceReason.objects.create(**validated_data)
                return absence_reason

        except IndexError:
            absence_reason = AbsenceReason.objects.create(**validated_data)
            return absence_reason


class PatientCreateSerializer(serializers.ModelSerializer):
    applications = ApplicationSerializerPatient(many=True, required=False)

    class Meta:
        model = Patient
        exclude = ("created_at", "updated_at", "account", "user")

    def create(self, validated_data):
        applications_validated_data = validated_data.pop('applications', [])
        if len(applications_validated_data) > 5:
            raise serializers.ValidationError({"applications": _("Each Hospital must have only 5 Applications")})
        validated_data['account_id'] = self.context['request'].user.account_id
        validated_data['user_id'] = self.context['request'].user.id
        patient = Patient.objects.create(**validated_data)
        applications_serializer = self.fields['applications']
        for app in applications_validated_data:
            app['patient'] = patient
        application = applications_serializer.create(applications_validated_data)
        return patient

    def update(self, instance, validated_data):
        applications = validated_data.pop('applications', [])
        if len(applications) > 5:
            raise serializers.ValidationError({"applications": _("Each Hospital must have only 5 Applications")})
        super(PatientCreateSerializer, self).update(instance, validated_data)
        instance.save()
        keep_apps = []
        for application in applications:
            if "id" in application.keys() and Application.objects.filter(id=application["id"]).exists():
                app = Application.objects.get(id=application["id"])
                app.application_name = application.get('application_name', app.application_name)
                app.application_id = application.get('application_id', app.application_id)
                app.save()
                keep_apps.append(app.id)
            else:
                app = Application.objects.create(**application, patient=instance)
                keep_apps.append(app.id)

        for application in instance.applications.all():
            if application.id not in keep_apps:
                application.delete()
        return instance


class PatientRetrieveSerializer(serializers.ModelSerializer):
    applications = ApplicationSerializerPatient(many=True)

    class Meta:
        model = Patient
        exclude = ("created_at", "updated_at", "account", "user")


class PatientListSerializer(serializers.ModelSerializer):
    hospital_name = serializers.SerializerMethodField()
    module_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ("id", "first_name", "last_name", "label_printing", "status",
                  "room_number", "hospital_name", "module_name",)

    def get_hospital_name(self, obj):
        return obj.hospital.hospital_name

    def get_module_name(self, obj):
        return obj.assign_centre_module.module_name


class PatientAssignModuleListSerializer(serializers.ModelSerializer):
    assign_centre_module = serializers.SerializerMethodField()
    hospital = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["id", "full_name", "assign_centre_module", "hospital", ]

    def get_hospital(self, obj):
        hospital = {"hospital_name": obj.hospital.hospital_name, "id": obj.hospital.id}
        return hospital

    def get_assign_centre_module(self, obj):
        if obj.assign_centre_module:
            module = {"module_name": obj.assign_centre_module.module_name, "id": obj.assign_centre_module.id}
            return module
        return None


class PatientAssignModuleSerializer(serializers.ModelSerializer):
    patient_assign_modules = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = ["id", "first_name", "assign_centre_module", "hospital", "patient_assign_modules"]
        extra_kwargs = {
            "validators": []
        }

    def get_patient_assign_modules(self, obj):
        return None


# Serializer for pharmacist dashboard patient listing
class PharmacistPatientListSerializer(serializers.ModelSerializer):
    patients = serializers.SerializerMethodField()

    class Meta:
        model = AssignCentreModule
        fields = ['id', "module_name", "patients"]

    def get_patients(self, obj):
        patient_data = obj.patients.filter(medicine_plannings__plannings__isnull=False).filter(
            medicine_plannings__plannings__is_validated=False)

        result = [{"id": i.id, "full_name": i.full_name} for n, i in enumerate(patient_data) if
                  i not in patient_data[n + 1:]]

        return result


# Serializer for production dashboard patient listing
class ProductionPatientListSerializer(serializers.ModelSerializer):
    patients = serializers.SerializerMethodField()

    class Meta:
        model = AssignCentreModule
        fields = ['id', "module_name", "patients"]

    def get_patients(self, obj):
        # patient_data = []
        # for patient in obj.patients.filter(medicine_plannings__plannings__isnull=False):
        #     patient_obj = {"id": patient.id, "full_name": patient.full_name}
        #     patient_data.append(patient_obj)
        # return patient_data
        patient_data = obj.patients.filter(medicine_plannings__plannings__isnull=False)
        result = [{"id": i.id, "full_name": i.full_name} for n, i in enumerate(patient_data) if
                  i not in patient_data[n + 1:]]

        return result

class HistoryAssignCentreModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignCentreModule
        fields = ["module_name"]

# Serializer for treatment History dashboard patient, floor, medicine, listing
class HistoryPatientListSerializer(serializers.ModelSerializer):
    assign_centre_modules = HistoryAssignCentreModuleSerializer(many=True)
    patients = serializers.SerializerMethodField()
    medicine = serializers.SerializerMethodField()
    patients_data = serializers.SerializerMethodField()

    class Meta:
        model = Hospital
        exclude = ("created_at", "updated_at", "account", "user", "hospital_image", "hospital_address",
                   "contact_person", "postal_code", "phone_number", "is_active")

    def get_medicine(self,obj):
       medicine_list = [{"id": med_obj.medicine.id, "medicine_name": med_obj.medicine.medicine_name}
                for data in obj.patients.filter(medicine_plannings__plannings__isnull=False)
                        for med_obj in data.medicine_plannings.all()]
       return {d['id']: d for d in reversed(medicine_list)}.values()

    def get_patients(self, obj):
        patient_data = obj.patients.filter(medicine_plannings__plannings__isnull=False)
        result = [{"id": i.id, "full_name": i.full_name} for n, i in enumerate(patient_data) if
                  i not in patient_data[n + 1:]]
        return result

    def get_patients_data(self, obj):
        patient_assign_module = []
        for module in obj.assign_centre_modules.all():
            patient_list = []
            for patient in module.patients.all():
                med_list = []
                if patient.medicine_plannings.all():
                    for med_obj in patient.medicine_plannings.all():
                        if med_obj.plannings.all():
                            med_list.append({"id": med_obj.medicine.id, "medicine_name": med_obj.medicine.medicine_name})
                    if med_list:
                        patient_list.append({"id": patient.pk, "name": patient.full_name, "medicines": med_list})
            patient_module_data = {
                "assign_centre_module": {"id": module.pk, "module_name": module.module_name},
                 "patient": patient_list}
            patient_assign_module.append(patient_module_data)
        return patient_assign_module
