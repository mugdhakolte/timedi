import datetime
import uuid

from django.db import models
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords

from multiselectfield import MultiSelectField

from timedi_auth.models import TimeStampMixin
from patient.models import Patient, User
from therapeutic_booklets.models import Medicine
from planning.choices import POSOLOGY_TYPE, INTAKE_TIME, DAYS, PATIENT_STOCK_TYPE, PATIENT_STOCK_DESC
from invoicing.models import Invoice


class MedicinePlanning(TimeStampMixin):
    """Class representing Medicine Planning."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medicine_plannings")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name="medicine_plannings")
    stock = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4), inherit=True)

    class Meta:
        """Meta class for Medicine Planning table"""
        db_table = 'medicine_planning'
        ordering = ("-updated_at",)

    def __str__(self):
        return "{}, {}".format(self.patient, self.medicine)


class PatientStockManagement(TimeStampMixin):
    type = models.CharField(max_length=5, choices=PATIENT_STOCK_TYPE)
    description = models.CharField(max_length=25, choices=PATIENT_STOCK_DESC)
    quantity = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    medicine_planning = models.ForeignKey(MedicinePlanning, on_delete=models.CASCADE,
                                          related_name="patient_stock_managements")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="patient_stock_managements")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, related_name="patient_stock_managements")

    class Meta:
        db_table = 'patient_stock_management'
        ordering = ("-created_at",)

    def __str__(self):
        return "{}, {}, {}, {}".format(self.medicine_planning, self.type, self.description, self.quantity)

    def save(self, *args, **kwargs):
        if (self.type == 'out' and self.description == 'production') or \
                (self.type == 'out' and self.description == 'invoice'):
            medicine_planning = MedicinePlanning.objects.get(id=self.medicine_planning.id)
            medicine_planning.stock = medicine_planning.stock - self.quantity
            medicine_planning.save()
            super(PatientStockManagement, self).save(*args, **kwargs)
        else:
            medicine_planning = MedicinePlanning.objects.get(id=self.medicine_planning.id)
            medicine_planning.stock = medicine_planning.stock + self.quantity
            medicine_planning.save()
            super(PatientStockManagement, self).save(*args, **kwargs)


class Planning(TimeStampMixin):
    """Class representing Planning."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    if_needed = models.BooleanField(default=False)
    special_dose = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)
    medicine_planning = models.ForeignKey(MedicinePlanning, on_delete=models.CASCADE, related_name="plannings")
    posology_type = models.CharField(max_length=50, choices=POSOLOGY_TYPE, default="standard_posology")

    # cycle posology
    active_period = models.IntegerField(null=True, blank=True)
    inactive_period = models.IntegerField(null=True, blank=True)

    # is_validated field for pharmacist control.
    is_validated = models.BooleanField(default=False)

    # is_produced field for  production module
    is_produced = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4), inherit=True)

    class Meta:
        """Meta class for planning table"""
        db_table = 'planning'
        ordering = ("-updated_at",)

    def __str__(self):
        return "{}, {}".format(self.medicine_planning, self.posology_type, )

    def clean(self):
        # if self.start_date < datetime.date.today():
        #     raise ValidationError({"start_date": "start date should be greater that today."},
        #                           code=400)

        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date should be greater than start date."}, code=400)


class PosologyPlanning(TimeStampMixin):
    """
    Class representing Standard, Specific, Cycle posology according the posology type.
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    day = models.CharField(max_length=20, null=True, blank=True, choices=DAYS)
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name="posology_plannings")
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4), inherit=True)

    class Meta:
        """Meta class for posology table"""
        db_table = 'posology_planning'
        unique_together = (('planning', 'day'),)
        ordering = ("-updated_at",)

    def __str__(self):
        return "{}".format(self.planning, )


class IntakeMoment(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    intake_time = models.CharField(max_length=10, choices=INTAKE_TIME)
    dosage_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    posology_planning = models.ForeignKey(PosologyPlanning, on_delete=models.CASCADE,
                                          related_name="intake_moments")
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4), inherit=True)

    class Meta:
        """Meta class for Intake Moment table"""
        db_table = 'intake_moment'
        ordering = ("intake_time", )

    def __str__(self):
        return "{}, {}, {}".format(self.posology_planning.planning, self.intake_time, self.dosage_amount)


class EachPosologyPlanning(TimeStampMixin):
    """
    Class representing Each posology Planning.
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    each_posology_days = models.IntegerField(null=True, blank=True)
    each_x_days = models.BooleanField(default=False)
    odd_days = models.BooleanField(default=False)
    even_days = models.BooleanField(default=False)

    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name="each_posology_plannings")

    intake_time = MultiSelectField(max_length=450, choices=INTAKE_TIME)
    dosage_amount = models.DecimalField(max_digits=6, decimal_places=2)
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4), inherit=True)

    class Meta:
        """Meta class for each posology table"""
        db_table = 'each_posology_planning'
        ordering = ("-updated_at",)

    def __str__(self):
        return "{}".format(self.planning, )


class FromToPosologyPlanning(TimeStampMixin):
    """
    Class representing From_To posology Planning.
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    starts_at = models.IntegerField()
    ends_at = models.IntegerField()
    month_lapse = models.IntegerField()

    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name="from_to_posology_plannings")

    intake_time = MultiSelectField(max_length=450, choices=INTAKE_TIME)
    dosage_amount = models.DecimalField(max_digits=6, decimal_places=2)
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4), inherit=True)

    class Meta:
        """Meta class for from_to posology table"""
        db_table = 'from_to_posology_planning'
        ordering = ("-updated_at",)

    def __str__(self):
        return "{}".format(self.planning, )
