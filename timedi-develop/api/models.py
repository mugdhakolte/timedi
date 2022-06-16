# """Models for Hospital Management System"""
#
# from multiselectfield import MultiSelectField
#
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.core.validators import MinLengthValidator
# from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
# from timedi_auth.models import TimeStampMixin, Account, User
#
# from timedi_auth.models import TimeStampMixin, Account, User
# from .choices import Days, Intake_Time
# from hospital.models import Hospital
# from patient.models import Patient
#
#
# class Doctor(TimeStampMixin):
#     """Class representing Doctor."""
#     name = models.CharField(max_length=50)
#     age = models.IntegerField()
#     gender = models.CharField(max_length=30)
#     address = models.CharField(max_length=100)
#     account = models.ForeignKey(Account, on_delete=models.CASCADE,
#                                 related_name='Doctor_Account')
#
#     class Meta:
#         """Meta class for doctors table"""
#         db_table = 'doctor'
#
#     def __str__(self):
#         return '{}'.format(self.name)
#
#     def __repr__(self):
#         return str(self)
#
#
# class Store(TimeStampMixin):
#     """Class representing Store."""
#     name = models.CharField(max_length=50)
#     address = models.CharField(max_length=50)
#     account = models.ForeignKey(Account, on_delete=models.CASCADE,
#                                 related_name='Store_account')
#
#     class Meta:
#         """Meta class for store table"""
#         db_table = 'store'
#
#     def __str__(self):
#         return '{}'.format(self.name)
#
#     def __repr__(self):
#         return str(self)
#
#
# class MedicalProfile(TimeStampMixin):
#     """Class representing Patient's Medical Profile."""
#     select_diseases = models.CharField(max_length=50)
#     blood_glucose = models.DecimalField(decimal_places=2, max_digits=5)
#     height = models.DecimalField(decimal_places=2, max_digits=5)
#     weight = models.DecimalField(decimal_places=2, max_digits=5)
#     cholesterol = models.DecimalField(decimal_places=2, max_digits=5)
#     glucose = models.DecimalField(decimal_places=2, max_digits=5)
#     upload_date = models.DateField()
#     additional_info = models.CharField(max_length=50)
#     patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE,
#                                    related_name='Patient_Medical_Profile')
#
#     class Meta:
#         """Meta class for medical_profile table"""
#         db_table = 'medical_profile'
#
#
#
# class Output(TimeStampMixin):
#     """Class representing Patient Output."""
#     reason = models.CharField(max_length=250)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     absence = models.BooleanField()
#
#     class Meta:
#         """Meta class for output table"""
#         db_table = 'output'
#
#
#
#
# # class Permission(models.Model):
# #     """Class representing User Permission"""
# #
# #     read = models.BooleanField()
# #     write = models.BooleanField()
# #     user_id = models.ForeignKey(User, on_delete=models.CASCADE,
# #                                 related_name='User_Permission')
# #
# #     class Meta:
# #         """Meta class for Permission table"""
# #         db_table = 'permission'
#
#
# class CustomGroup(models.Model):
#     group = models.OneToOneField('auth.Group', unique=True, on_delete=models.CASCADE)
