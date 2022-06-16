from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from therapeutic_booklets.models import (TherapeuticBookMedicine, Medicine, TherapeuticBook, AdditionalCodes,
                                         OfficialMedicine)


class AdditionalCodesSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = AdditionalCodes
        fields = "__all__"


class TherapeuticBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = TherapeuticBook
        fields = "__all__"


class MedicineSerializer(serializers.ModelSerializer):
    additionalcodes = AdditionalCodesSerializer(many=True, required=False)

    class Meta:
        model = Medicine
        exclude = ("country_code",)

    def validate(self, validated_data):

        if self.context['request'].method == "POST":
            additionalcodes_validated_data = validated_data.get('additionalcodes', [])
            if len(additionalcodes_validated_data) > 5:
                raise serializers.ValidationError({"additionalcodes":
                                                       _("Each Hospital must have only 5 Additional Codes")})
            response = []
            additionalcodes_list = []
            for additionalcode in additionalcodes_validated_data:
                if additionalcode["additionalcode"] == validated_data["national_medication_code"]:
                    result = [_("This additionalcode code {} and NC code {} must be different")
                                  .format(additionalcode["additionalcode"], validated_data["national_medication_code"])]
                    response.append(result)
                elif additionalcode["additionalcode"] in additionalcodes_list:
                    result = [_("The additional {} must be different")
                                  .format(additionalcode["additionalcode"])]
                    response.append(result)
                elif Medicine.objects.filter(national_medication_code=additionalcode["additionalcode"]).exists() or \
                        AdditionalCodes.objects.filter(additionalcode=additionalcode["additionalcode"]).exists():
                    result = [
                        _("This additionalcode {} code is already exists").format(additionalcode["additionalcode"])]
                    response.append(result)
                additionalcodes_list.append(additionalcode["additionalcode"])
            if response.__len__() > 0:
                raise serializers.ValidationError({"additionalcode": response})
        return validated_data

    def create(self, validated_data):
        additionalcodes_validated_data = validated_data.pop('additionalcodes', [])
        try:
            if Medicine.objects.filter(national_medication_code=validated_data["national_medication_code"],
                                       country_code=self.context['request'].user.account.country_code).exists():
                raise serializers.ValidationError({"national_medication_code": [_("This NC code is already exists")]})
            therapeutic_book = TherapeuticBook.objects.create(account_id=self.context['request'].user.account_id)
            validated_data["country_code"] = self.context['request'].user.account.country_code
        except:
            if Medicine.objects.filter(national_medication_code=validated_data["national_medication_code"],
                                       country_code=self.context['request'].user.account.country_code).exists():
                raise serializers.ValidationError({"national_medication_code": [_("This NC code is already exists")]})
            therapeutic_book = TherapeuticBook.objects.create(account_id=self.context.user.account_id)
            validated_data["country_code"] = self.context['request'].user.account.country_code
        medicine = Medicine.objects.create(**validated_data)
        for additionalcode in additionalcodes_validated_data:
            additionalcode['medicine'] = medicine
            AdditionalCodes.objects.create(**additionalcode)
        TherapeuticBookMedicine.objects.create(medicine=medicine, therapeuticbook=therapeutic_book)
        return medicine

    def update(self, instance, validated_data):
        validated_data["national_medication_code"] = instance.national_medication_code
        additionalcodes = validated_data.pop('additionalcodes', [])

        response = []
        additionalcodes_with_id = []
        additionalcodes_without_id = []
        additionalcodes_ids = []
        for additionalcode in additionalcodes:
            if additionalcode["additionalcode"] in additionalcodes_ids:
                result = [_("The additional {} must be different")
                              .format(additionalcode["additionalcode"])]
                response.append(result)
            elif "id" in additionalcode.keys():
                additionalcodes_with_id.append(additionalcode)
            else:
                additionalcodes_without_id.append(additionalcode)
            additionalcodes_ids.append(additionalcode["additionalcode"])
        if response.__len__() > 0:
            raise serializers.ValidationError({"additionalcode": response})

        response_with_id = []
        for additionalcode in additionalcodes_with_id:
            obj = AdditionalCodes.objects.get(id=additionalcode["id"])
            if additionalcode["additionalcode"] == validated_data["national_medication_code"]:
                result = [_("This additionalcode code {} and NC code {} must be different")
                              .format(additionalcode["additionalcode"], validated_data["national_medication_code"])]
                response_with_id.append(result)
            elif additionalcode["additionalcode"] != obj.additionalcode:
                if Medicine.objects.filter(national_medication_code=additionalcode["additionalcode"]).exists() or \
                        AdditionalCodes.objects.filter(additionalcode=additionalcode["additionalcode"]).exists():
                    result = [
                        _("This additionalcode {} code is already exists").format(additionalcode["additionalcode"])]
                    response_with_id.append(result)
        if response_with_id.__len__() > 0:
            raise serializers.ValidationError({"additionalcode": response_with_id})

        response_without_id = []
        for additionalcode in additionalcodes_without_id:
            if additionalcode["additionalcode"] == validated_data["national_medication_code"]:
                result = [_("This additionalcode code {} and NC code {} must be different")
                              .format(additionalcode["additionalcode"], validated_data["national_medication_code"])]
                response_without_id.append(result)

            elif Medicine.objects.filter(national_medication_code=additionalcode["additionalcode"]).exists() or \
                    AdditionalCodes.objects.filter(additionalcode=additionalcode["additionalcode"]).exists():
                result = [_("This additionalcode {} code is already exists")
                              .format(additionalcode["additionalcode"])]
                response_without_id.append(result)
        if response_without_id.__len__() > 0:
            raise serializers.ValidationError({"additionalcode": response_without_id})

        if len(additionalcodes) > 5:
            raise serializers.ValidationError({"additionalcodes":
                                                   _("Each Hospital must have only 5 Additional Codes")})
        super(MedicineSerializer, self).update(instance, validated_data)
        instance.save()

        keep_additionalcodes = []
        for additionalcode in additionalcodes:
            if "id" in additionalcode.keys() and AdditionalCodes.objects.filter(id=additionalcode["id"]).exists():
                obj = AdditionalCodes.objects.get(id=additionalcode["id"])
                obj.additionalcode = additionalcode.get('additionalcode', obj.additionalcode)
                obj.pills = additionalcode.get('pills', obj.pills)
                obj.save()
                keep_additionalcodes.append(obj.id)
            else:
                obj = AdditionalCodes.objects.create(**additionalcode, medicine=instance)
                keep_additionalcodes.append(obj.id)

        for additionalcode in instance.additionalcodes.all():
            if additionalcode.id not in keep_additionalcodes:
                additionalcode.delete()
        return instance


class MedicineListSerializer(serializers.ModelSerializer):
    patient_count = serializers.SerializerMethodField()

    class Meta:
        model = Medicine
        fields = "__all__"

    def get_patient_count(self, obj):
        return obj.medicine_plannings.all().count()


class OfficialMedicineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfficialMedicine
        fields = "__all__"


class OfficialMedicineCreateSerializer(serializers.Serializer):
    official_medicines = serializers.ListField()


class ReportGenerationSerializer(serializers.ModelSerializer):
    medicine = MedicineListSerializer(read_only=True)

    class Meta:
        model = TherapeuticBookMedicine
        fields = ("medicine",)


class TherapeuticBookMedicineSerializer(serializers.ModelSerializer):
    medicine = MedicineListSerializer(read_only=True)

    class Meta:
        model = TherapeuticBookMedicine
        fields = ("id", "alias", "is_blistable", "medicine")
