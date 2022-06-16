"""
Models for TherapeuticBookMedicine module.
"""
import uuid

from django.db import models
from django.core.validators import RegexValidator
from simple_history.models import HistoricalRecords


from timedi_auth.models import TimeStampMixin, Account


class Medicine(TimeStampMixin):
    """Class representing Medicine"""
    # alphanumeric = RegexValidator(r'^[0-9a-zA-Z\s]*$', 'Only space and alphanumeric value is allowed.')
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    medicine_name = models.CharField(max_length=250)
    national_medication_code = models.CharField(max_length=50)
    country_code = models.CharField(max_length=30)
    strength = models.DecimalField(decimal_places=2, max_digits=50, null=True, blank=True)
    units_per_box = models.IntegerField()
    type = models.CharField(max_length=50)
    laboratories = models.CharField(max_length=250)
    non_packable_treatment = models.BooleanField(default=False)
    price = models.DecimalField(decimal_places=2, max_digits=50, null=True, blank=True)
    is_official = models.BooleanField(default=False)
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4))

    # fields from medicine.json
    description = models.CharField(max_length=250, blank=True, null=True)
    dosage_form_name = models.CharField(max_length=250, blank=True, null=True)
    composition_repetition_code = models.CharField(max_length=250, blank=True, null=True)
    price_without_vat = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)
    pharmaceutical_data_value_name = models.CharField(max_length=250, blank=True, null=True)
    vmp_group_code = models.CharField(max_length=250, blank=True, null=True)
    active_principle_name = models.CharField(max_length=250, blank=True, null=True)
    group_name = models.CharField(max_length=250, blank=True, null=True)
    administration_method_code = models.CharField(max_length=250, blank=True, null=True)
    availability_date = models.DateField(blank=True, null=True)
    pharmaceutical_data_value_code = models.CharField(max_length=250, blank=True, null=True)
    salt_code = models.CharField(max_length=250, blank=True, null=True)
    composition_unit = models.CharField(max_length=250, blank=True, null=True)
    active_principle_code = models.CharField(max_length=250, blank=True, null=True)
    drop_out_date = models.DateField(blank=True, null=True)
    color_code = models.CharField(max_length=250, blank=True, null=True)
    group_code = models.CharField(max_length=250, blank=True, null=True)
    vmp_group_name = models.CharField(max_length=250, blank=True, null=True)
    container = models.CharField(max_length=250, blank=True, null=True)
    atc_code = models.CharField(max_length=250, blank=True, null=True)
    salt_name = models.CharField(max_length=250, blank=True, null=True)
    commercialization_date = models.DateField(blank=True, null=True)
    dosage_form_code = models.CharField(max_length=250, blank=True, null=True)
    color_name = models.CharField(max_length=250, blank=True, null=True)
    laboratory_code = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        """Meta class for medicine table"""
        db_table = 'medicine'
        ordering = ['-updated_at', ]
        unique_together = ('country_code', 'national_medication_code',)

    def __str__(self):
        return "{}".format(self.medicine_name)

    def __repr__(self):
        return str(self)


class TherapeuticBook(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                related_name='therapeuticbooks')

    class Meta:
        """Meta class for therapeutic table"""
        db_table = 'therapeutic_book'

    def __str__(self):
        return "{}".format(self.account)

    def __repr__(self):
        return str(self)


class TherapeuticBookMedicine(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    alias = models.CharField(max_length=30, null=True, blank=True)
    is_blistable = models.BooleanField(default=False)
    medicine = models.OneToOneField(Medicine, on_delete=models.CASCADE, related_name="therapeuticbooksmedicines")
    therapeuticbook = models.ForeignKey(TherapeuticBook, on_delete=models.CASCADE,
                                        related_name="therapeuticbooksmedicines")

    class Meta:
        """Meta class for therapeutic_book_medicine table"""
        db_table = 'therapeutic_book_medicine'

    def __str__(self):
        return "{} {}".format(self.medicine, self.therapeuticbook)

    def __repr__(self):
        return str(self)


class AdditionalCodes(TimeStampMixin):
    """Class representing AdditionalCodes"""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    additionalcode = models.CharField(max_length=50,)
    pills = models.CharField(max_length=50, null=True, blank=True)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, blank=True,
                                 null=True, related_name="additionalcodes")

    class Meta:
        """Meta class for AdditionalCodes"""
        db_table = 'additional_codes'


class OfficialMedicine(TimeStampMixin):
    """Class representing Medicine"""
    # alphanumeric = RegexValidator(r'^[0-9a-zA-Z\s]*$', 'Only space and alphanumeric value is allowed.')
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    medicine_name = models.CharField(max_length=250)
    national_medication_code = models.CharField(max_length=50)
    country_code = models.CharField(max_length=30)
    strength = models.DecimalField(decimal_places=2, max_digits=50, null=True, blank=True)
    units_per_box = models.IntegerField()
    type = models.CharField(max_length=50)
    laboratories = models.CharField(max_length=250)
    non_packable_treatment = models.BooleanField(default=False)
    price = models.DecimalField(decimal_places=2, max_digits=50, null=True, blank=True)
    is_added_to_catalogue = models.BooleanField(default=False)

    # fields from medicine.json
    description = models.CharField(max_length=250, blank=True, null=True)
    dosage_form_name = models.CharField(max_length=250, blank=True, null=True)
    composition_repetition_code = models.CharField(max_length=250, blank=True, null=True)
    price_without_vat = models.DecimalField(decimal_places=2, max_digits=50, default=0.00)
    pharmaceutical_data_value_name = models.CharField(max_length=250, blank=True, null=True)
    vmp_group_code = models.CharField(max_length=250, blank=True, null=True)
    active_principle_name = models.CharField(max_length=250, blank=True, null=True)
    group_name = models.CharField(max_length=250, blank=True, null=True)
    administration_method_code = models.CharField(max_length=250, blank=True, null=True)
    availability_date = models.DateField(blank=True, null=True)
    pharmaceutical_data_value_code = models.CharField(max_length=250, blank=True, null=True)
    salt_code = models.CharField(max_length=250, blank=True, null=True)
    composition_unit = models.CharField(max_length=250, blank=True, null=True)
    active_principle_code = models.CharField(max_length=250, blank=True, null=True)
    drop_out_date = models.DateField(blank=True, null=True)
    color_code = models.CharField(max_length=250, blank=True, null=True)
    group_code = models.CharField(max_length=250, blank=True, null=True)
    vmp_group_name = models.CharField(max_length=250, blank=True, null=True)
    container = models.CharField(max_length=250, blank=True, null=True)
    atc_code = models.CharField(max_length=250, blank=True, null=True)
    salt_name = models.CharField(max_length=250, blank=True, null=True)
    commercialization_date = models.DateField(blank=True, null=True)
    dosage_form_code = models.CharField(max_length=250, blank=True, null=True)
    color_name = models.CharField(max_length=250, blank=True, null=True)
    laboratory_code = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        """Meta class for medicine table"""
        db_table = 'official_medicine'
        ordering = ['-updated_at', ]
        unique_together = ('country_code', 'national_medication_code',)

    def __str__(self):
        return "{}".format(self.medicine_name)

    def __repr__(self):
        return str(self)
