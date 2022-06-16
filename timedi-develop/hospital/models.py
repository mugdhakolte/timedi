"""
Models for hospital module.
"""
import uuid

from django.db import models
from simple_history.models import HistoricalRecords

from timedi_auth.models import TimeStampMixin, Account, User
from hospital.choices import *


class Hospital(TimeStampMixin):
    """Class representing Hospital."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    hospital_name = models.CharField(max_length=50)
    # hospital_id = models.CharField(max_length=20)
    hospital_image = models.TextField(blank=True, null=True)
    hospital_address = models.CharField(max_length=50, null=True, blank=True)
    contact_person = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=30, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='hospitals')
    account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                related_name='hospitals')
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4))

    # def save_without_historical_record(self, *args, **kwargs):
    #     self.skip_history_when_saving = True
    #     try:
    #         ret = self.save(*args, **kwargs)
    #     finally:
    #         del self.skip_history_when_saving
    #     return ret

    class Meta:
        """Meta class for hospital table"""
        db_table = 'hospital'
        ordering = ['-updated_at', ]

    def __str__(self):
        return '{}'.format(self.hospital_name)

    def __repr__(self):
        return str(self)

    @property
    def active_patients(self):
        return self.patients.filter(status="active").count()

    @property
    def total_patients(self):
        return self.patients.all().count()


class ProductionSetting(TimeStampMixin):
    """Class representing Production Settings."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    produce_treatment_if_needed = models.BooleanField(default=False)
    produce_treatment_in_variable_dosage = models.BooleanField(default=False)
    produce_external_treatment = models.BooleanField(default=False)
    hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE,
                                    related_name='production_settings')

    class Meta:
        """Meta class for production_settings table"""
        db_table = 'production_settings'


class StockManagement(TimeStampMixin):
    """Class representing StockManagement."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    cn_number = models.IntegerField()
    medicine_name = models.CharField(max_length=30)
    stock_value = models.IntegerField()
    boxes = models.IntegerField()
    patients = models.CharField(max_length=50)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE,
                                    related_name='stock_managements')

    class Meta:
        """Meta class for stock_management table"""
        db_table = 'stock_management'


class HospitalStockManagement(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    stock_management_setting = models.CharField(max_length=50, choices=STOCK_MANAGEMENT_SETTING, blank=True)
    manage_stock_of_external_medicines = models.BooleanField(default=False)
    manage_stock = models.BooleanField(default=False)
    can_produce = models.BooleanField(default=False)
    share_information_to_ti = models.BooleanField(default=False)
    import_external_medicines_invoiced = models.BooleanField(default=False)
    do_not_import_codes = models.BooleanField(default=False)
    codes_from = models.IntegerField()
    codes_to = models.IntegerField()
    hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE, related_name="hospital_stock_management")

    class Meta:
        """Meta class for stock_management table"""
        db_table = 'hospital_stock_management'
