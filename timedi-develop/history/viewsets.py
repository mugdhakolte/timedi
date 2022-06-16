import datetime
import operator
from functools import reduce

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from patient.models import (Patient, Hospital)
from planning.models import *
from therapeutic_booklets.models import Medicine
from production.models import ProductionRecord, Planning
from invoicing.models import Invoice

from history.utils import (generate_pdf)
from history.serializers import HistoryPlanningSerializer, PlanningHistorySerializer, HistoryTreatmentPlanningSerializer


class HistoryDashboardViewSet(viewsets.ViewSet):
    """
       list:
           Returns all history data.

       view_detail:
           returns details of history.

       treatment_details:
           returns treatment details.

       modification_detail:
           returns modification details of history.

       modification_report:
           returns modification report in pdf format.

    """

    def list(self, request, *agrs, **kwargs):

        data = []

        for patient in Patient.objects.filter(account__id=self.request.user.account_id):
            for his_data in patient.history.all():

                if his_data.history_user:
                    data.append({"user": his_data.history_user.full_name, "history_module": "Patient",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})
                else:
                    data.append({"user": None, "history_module": "Patient",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})

        for hospital in Hospital.objects.filter(account__id=self.request.user.account_id):
            for his_data in hospital.history.all():
                if his_data.history_user:
                    data.append({"user": his_data.history_user.full_name, "history_module": "hospital",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})
                else:
                    data.append({"user": None, "history_module": "hospital",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})

        for medicine in Medicine.objects.filter(
                therapeuticbooksmedicines__therapeuticbook__account_id=self.request.user.account_id):
            for his_data in medicine.history.all():
                if his_data.history_user:
                    data.append({"user": his_data.history_user.full_name, "history_module": "medicine",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})
                else:
                    data.append({"user": None, "history_module": "medicine",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})

        for planning in Planning.objects.filter(medicine_planning__patient__account_id=self.request.user.account_id):
            for his_data in planning.history.all():
                if his_data.history_user:
                    data.append({"user": his_data.history_user.full_name, "history_module": "planning",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id,
                                 "planning_id": his_data.id})
                else:
                    data.append({"user": None, "history_module": "planning",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id,
                                 "planning_id": his_data.id})

        for production in ProductionRecord.objects.filter(user__account_id=self.request.user.account_id):
            for his_data in production.history.all():
                if his_data.history_user:
                    data.append({"user": his_data.history_user.full_name, "history_module": "production",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})
                else:
                    data.append({"user": None, "history_module": "production",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})

        for invoice in Invoice.objects.filter(account__id=self.request.user.account_id):
            for his_data in invoice.history.all():
                if his_data.history_user:
                    data.append({"user": his_data.history_user.full_name, "history_module": "invoice",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})
                else:
                    data.append({"user": None, "history_module": "invoice",
                                 "history_action_type": his_data.history_type,
                                 "history_date": his_data.history_date.date(),
                                 "history_id": his_data.history_id})
        # history_managers = [model for model in apps.get_models() if 'Historical' in model._meta.object_name]
        #
        # history_objects = []
        # for manager in history_managers:
        #     history_objects += list(manager.objects.all())

        return Response({"data": sorted(data, key=lambda k: k['history_date'])})

    @action(methods=["GET"], detail=False, url_path='view-detail', url_name='view_detail')
    def view_detail(self, request, *args, **kwargs):
        history_id = request.query_params.get("history")
        planning_id = request.query_params.get("planning")
        data = HistoryPlanningSerializer(Planning.objects.get(id=planning_id))
        # data = []
        # for planning in Planning.objects.filter(medicine_planning__patient__account_id=self.request.user.account_id):
        #     for his_data in planning.history.all():
        #         if his_data.history_user:
        #             data.append({"user": his_data.history_user.full_name, "history_module": "planning",
        #                          "history_action_type": his_data.history_type,
        #                          "history_date": his_data.history_date.date(),
        #                          "history_id": his_data.history_id})
        #         else:
        #             data.append({"user": None, "history_module": "planning",
        #                          "history_action_type": his_data.history_type,
        #                          "history_date": his_data.history_date.date(),
        #                          "history_id": his_data.history_id})
        return Response({"data": data.data})

    @action(methods=["POST"], detail=False, url_path='treatment-details', url_name='treatment_details')
    def treatment_details(self, request, *args, **kwargs):
        patient_id = request.data.get("patient")
        medicines = request.data.get("medicines")
        from_date = datetime.datetime.strptime(request.data.get('from_date'), '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(request.data.get("to_date"), '%Y-%m-%d').date()

        queryset = MedicinePlanning.objects.filter(
            reduce(operator.or_, (Q(medicine=term) for term in medicines)), patient=patient_id)
        his_med_plan_serializer = HistoryTreatmentPlanningSerializer(queryset, many=True,
                                                                     context={"from_date": from_date,
                                                                              "to_date": to_date})
        return Response({"data": his_med_plan_serializer.data})

    @action(methods=["POST"], detail=False, url_path='modification-detail', url_name='modification_detail')
    def modification_detail(self, request, *args, **kwargs):
        patient_id = request.data.get("patient_id")
        from_date = datetime.datetime.strptime(request.data.get('from_date'), '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(request.data.get("to_date"), '%Y-%m-%d').date()

        patient = Patient.objects.get(id=patient_id)
        result = []
        for med_plan_obj in patient.medicine_plannings.all():
            if med_plan_obj.plannings.all():
                response = {}
                history_data = []
                for planning_obj in med_plan_obj.plannings.all():
                    data = PlanningHistorySerializer(Planning.objects.get(id=planning_obj.id))
                    if planning_obj and from_date <= planning_obj.start_date <= to_date:
                        history_data.extend(data.data["history_data"])
                if data and data.data["history_data"] and [d for d in history_data if d['dosage_amount'] not in ("0.00", "0.0")]:
                    response["history"] = [d for d in history_data if d['dosage_amount'] not in ("0.00", "0.0")]
                    response["medicine_name"] = med_plan_obj.medicine.medicine_name
                    response["national_medication_code"] = med_plan_obj.medicine.national_medication_code
                    result.append(response)
        return Response({"data": result})

    @action(methods=["POST"], detail=False, url_path='modification-report', url_name='modification_report')
    def modification_report(self, request, *args, **kwargs):
        patient_id = request.data.get("patient_id")
        from_date = datetime.datetime.strptime(request.data.get('from_date'), '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(request.data.get("to_date"), '%Y-%m-%d').date()

        patient = Patient.objects.get(id=patient_id)
        result = []
        for med_plan_obj in patient.medicine_plannings.all():
            if med_plan_obj.plannings.all():
                response = {}
                history_data = []
                for planning_obj in med_plan_obj.plannings.all():
                    if planning_obj and from_date <= planning_obj.start_date <= to_date:
                        data = PlanningHistorySerializer(Planning.objects.get(id=planning_obj.id))
                        history_data.extend(data.data["history_data"])
                if data.data["history_data"] and [d for d in history_data if d['dosage_amount'] not in ("0.00", "0.0")]:
                    response["history"] = [d for d in history_data if d['dosage_amount'] not in ("0.00", "0.0")]
                    response["medicine_name"] = med_plan_obj.medicine.medicine_name
                    response["national_medication_code"] = med_plan_obj.medicine.national_medication_code
                    result.append(response)
        output = generate_pdf("history_report.html", result)
        return output
