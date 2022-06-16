import uuid

from django.db import models
from simple_history.models import HistoricalRecords

from patient.models import Patient
from therapeutic_booklets.models import Medicine
from timedi_auth.models import TimeStampMixin, Account, User


class Invoice(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="invoices")
    store_id = models.IntegerField(blank=True, null=True)
    store_name = models.CharField(max_length=100, null=True, blank=True)
    hospital_id = models.IntegerField()
    hospital_name = models.CharField(max_length=100, )
    patient_id = models.IntegerField()
    patient_name = models.CharField(max_length=100, )
    invoice_number = models.CharField(max_length=50)
    invoice_datetime = models.DateTimeField()
    integration_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    is_valid = models.BooleanField(default=False)
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4))

    class Meta:
        db_table = 'invoice'
        unique_together = ("integration_id", "invoice_number")
        ordering = ['-updated_at', ]

    def __str__(self):
        return '{}, {}, {}'.format(self.patient_name, self.hospital_name, self.is_valid)


class InvoiceItem(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    product_code = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    is_skipped = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)

    class Meta:
        db_table = 'invoice_item'
        unique_together = ("invoice", "product_code")
        ordering = ['-updated_at', ]

    def __str__(self):
        return '{}, {}'.format(self.invoice, self.product_code)


class Store(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="stores")

    class Meta:
        db_table = 'store'
        ordering = ['-updated_at', ]

    def __str__(self):
        return '{}, {}'.format(self.name, self.address)


class InvoiceIntegration(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    integration_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="invoice_integrations")
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name="invoice_integrations")
    name = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=25, null=True, blank=True)

    class Meta:
        db_table = 'invoice_integration'
        ordering = ['-updated_at', ]

    def __str__(self):
        return '{}, {}, {}'.format(self.name, self.user, self.store)


class InvoiceRelatedMedicine(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    invoice_integration = models.ForeignKey(InvoiceIntegration, on_delete=models.CASCADE,
                                            related_name="invoice_related_medicines")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name="invoice_related_medicines")
    invoice_medicine_id = models.CharField(max_length=50, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, related_name="invoice_related_medicines")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, related_name="invoice_related_medicines")

    class Meta:
        db_table = 'invoice_related_medicine'
        ordering = ['-updated_at', ]

    def __str__(self):
        return '{}, {}, {}'.format(self.medicine, self.patient, self.invoice)


class InvoiceRelatedPatient(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    invoice_integration = models.ForeignKey(InvoiceIntegration, on_delete=models.CASCADE,
                                            related_name="invoice_related_patients")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="invoice_related_patients")
    invoice_patient_id = models.IntegerField()

    class Meta:
        db_table = 'invoice_related_patient'
        unique_together = ("invoice_integration", "patient")
        ordering = ['-updated_at', ]

    def __str__(self):
        return '{}, {}'.format(self.patient, self.invoice_patient_id)
