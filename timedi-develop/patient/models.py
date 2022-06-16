"""
Models for patient module.
"""
import uuid

from django.db import models
from django.core.validators import RegexValidator
from simple_history.models import HistoricalRecords


from patient.choices import *
from hospital.models import Hospital
from multiselectfield import MultiSelectField
from timedi_auth.models import TimeStampMixin, Account, User


class AssignCentreModule(TimeStampMixin):
    """Class representing AssignCentreModule."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    module_name = models.CharField(max_length=20)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name="assign_centre_modules")
    assign_centre_module_type = models.CharField(max_length=20, choices=APPLICATION_TYPE)


    class Meta:
        """Meta class for assignCentre_module table"""
        db_table = 'assign_module'
        ordering = ("-updated_at",)

    def __str__(self):
        return "{} {}".format(self.hospital, self.module_name)

    @property
    def patients_count(self):
        return self.patients.all().count()


class Patient(TimeStampMixin):
    """Class representing Patient."""
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric value is allowed.')
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50)
    # patient_id = models.CharField(max_length=20)
    last_name = models.CharField(max_length=30)
    label_printing = models.CharField(max_length=50)
    profile = models.TextField(null=True, blank=True)
    room_number = models.CharField(max_length=30, null=True, blank=True)
    ss_id = models.CharField(max_length=14, validators=[alphanumeric], null=True, blank=True)
    doctor_name = models.CharField(max_length=30, null=True, blank=True)
    date_of_birth = models.DateField(null=True)
    DNI = models.CharField(max_length=14, null=True, blank=True, validators=[alphanumeric])
    location = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    email_id = models.EmailField(null=True, blank=True)
    contact_person = models.CharField(max_length=30, null=True, blank=True)
    telephone_1 = models.CharField(max_length=20, null=True, blank=True)
    telephone_2 = models.CharField(max_length=20, null=True, blank=True)
    registration_date = models.DateField(null=True)
    withdraw_date = models.DateField(null=True, blank=True)
    reason = models.CharField(max_length=50, null=True, blank=True)
    blister_responsible = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_TYPE)
    assign_centre_module = models.ForeignKey(AssignCentreModule, on_delete=models.PROTECT, null=True,
                                             related_name='patients')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE,
                                 related_name='patients')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='patients')
    account = models.ForeignKey(Account, on_delete=models.CASCADE,
                                related_name='patients')
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4))

    class Meta:
        """Meta class for patients table"""
        db_table = 'patient'
        ordering = ('-updated_at',)

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return '{}'.format(self.full_name)

    def __repr__(self):
        return str(self)


class IntermediateProduction(TimeStampMixin):
    """Class representing Hospital and Patient Intermediate Production."""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    setting_applied_to = models.CharField(max_length=20, blank=True, null=True, choices=SETIINGS_APPLIED_TO)
    floors = MultiSelectField(max_length=80, null=True, blank=True)
    medicines = MultiSelectField(max_length=500, blank=True, null=True)
    days = MultiSelectField(max_length=80, choices=Days)
    intake_moments = MultiSelectField(max_length=200, blank=True, null=True, choices=Moments)
    time = MultiSelectField(max_length=450, choices=Intake_Time)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name="intermediate_productions")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True, null=True,
                                related_name="intermediate_productions")
    production_type = models.CharField(max_length=20, choices=INTERMEDIATE_PRODUCTION_TYPE)

    class Meta:
        """Meta class for hospital_and_Patient_intermediate_productions table"""
        db_table = 'intermediate_productions'
        ordering = ("-updated_at",)

    def __str__(self):
        return "{} {} {}".format(self.production_type, self.hospital, self.patient)


class Application(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    application_name = models.CharField(max_length=50, null=True, blank=True)
    application_id = models.CharField(max_length=20, null=True, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, blank=True, null=True, related_name="applications")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True, null=True, related_name="applications")
    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPE)

    class Meta:
        """Meta class for application table"""
        db_table = 'application'

    def __str__(self):
        return "{} {}".format(self.application_type, self.application_name)


class AbsenceReason(TimeStampMixin):
    """Class representing AbsenceReason"""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    reason = models.CharField(max_length=50)
    release_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    no_return_date = models.BooleanField(default=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                related_name='absence_reasons')

    class Meta:
        """Meta class for AbsenceReason"""
        db_table = 'absence_Reason'
        ordering = ("-updated_at",)
