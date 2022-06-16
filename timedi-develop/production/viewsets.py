import json
import base64
import operator
import itertools
from datetime import *
from functools import reduce

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.dateparse import parse_date, parse_datetime
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from patient.models import *
from planning.models import *
from production.serializers import *
from timedi_auth.utils import CustomJSONRenderer
from timedi_auth.permissions import CheckPermission
from production.produce import (sent_to_produce, remove_from_production, ocs_file_generation)
from production.calculation import (specific_intake_calculation, intake_calculations)
from production.utils import (xls_to_response, generate_pdf, BarcodeDrawing, mul)


class ProductionViewSet(viewsets.ModelViewSet):
    """
       retrieve:
           Return the given production.

       list:
           Return a list of all productions.

       create:
           Create a new production.

       destroy:
           Delete a production.

       update:
           Update a production.

       partial_update:
           Update a production.

       report:
            Generates report in excel and PDF format.

       remove_list:
            list down productions dates in between from_date and to_date.

       remove:
            removes a production.

       sticker_report:
            generates patient sticker report in pdf format.

       delivery_date_list:
            list down created dates in between from_date and to_date of productions.

       delivery_report:
            generated delivery report in pdf format.

    """

    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_production", ]
    filter_backends = [DjangoFilterBackend]

    def create(self, request, *args, **kwargs):
        serializer = PatientsProductionSerializer(data=request.data)
        if serializer.is_valid():
            search_terms = serializer.data.get("patients", None)

            invalidated_planning_patient_list = []
            invalidated_planning_present = False
            for patient in search_terms:
                patient_obj = Patient.objects.get(id=patient)
                invalidated_plannings = Planning.objects. \
                    filter(medicine_planning__patient=patient_obj).exclude(is_validated=True)
                invalidated_planning_list = []
                for invalidated_planning in invalidated_plannings:
                    invalidated_planning_list.append(invalidated_planning.id)
                    invalidated_planning_present = True
                invalidated_planning_patient_list.append(
                    {"patient_id": patient_obj.id,
                     "patient_name": patient_obj.full_name,
                     "posologies": invalidated_planning_list})

            if invalidated_planning_present:
                return Response({"patients": invalidated_planning_patient_list,
                                 "message": _("Please validate plannings first.")},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                queryset = MedicinePlanning.objects.filter(
                    reduce(operator.or_, (Q(patient=term) for term in search_terms)))

                production_planning_serializer = ProductionCreatePlanningSerializer(queryset, many=True)
                result = production_planning_serializer.data

                from_date = datetime.datetime.strptime(serializer.data.get('from_date'), '%Y-%m-%d').date()
                to_date = datetime.datetime.strptime(serializer.data.get('to_date'), '%Y-%m-%d').date()
                prod_record = ProductionRecordSerializer(data={"from_date": from_date,
                                                               "to_date": to_date,
                                                               "user": request.user.id})
                prod_record.is_valid(raise_exception=True)
                prod_record.save()
                response_data = sent_to_produce(self, result, from_date, to_date, prod_record.data['id'])
                if not response_data:
                    ProductionRecord.objects.get(id=prod_record.data['id']).delete()
                file_response = ocs_file_generation(response_data)
                return file_response
                # return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path='remove-list', url_name='remove_list')
    def remove_list(self, request, *args, **kwargs):
        serializer = PatientsProductionSerializer(data=request.data)
        if serializer.is_valid():
            search_terms = serializer.data.get("patients", None)

            invalidated_planning_patient_list = []
            invalidated_planning_present = False
            for patient in search_terms:
                patient_obj = Patient.objects.get(id=patient)
                invalidated_plannings = Planning.objects. \
                    filter(medicine_planning__patient=patient_obj).exclude(is_validated=True)
                invalidated_planning_list = []
                for invalidated_planning in invalidated_plannings:
                    invalidated_planning_list.append(invalidated_planning.id)
                    invalidated_planning_present = True
                invalidated_planning_patient_list.append(
                    {"patient_id": patient_obj.id,
                     "patient_name": patient_obj.full_name,
                     "posologies": invalidated_planning_list})

            if invalidated_planning_present:
                return Response({"patients": invalidated_planning_patient_list,
                                 "message": _("Please validate plannings first.")},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                from_date = datetime.datetime.strptime(serializer.data.get('from_date'), '%Y-%m-%d').date()
                to_date = datetime.datetime.strptime(serializer.data.get('to_date'), '%Y-%m-%d').date()
                queryset = Production.objects.filter(
                    reduce(operator.or_, (Q(planning__medicine_planning__patient=term) for term in search_terms)),
                    from_date__gte=from_date, to_date__lte=to_date)

                if len(queryset) >= 1:
                    production_date_list = []
                    for obj in queryset:
                        production_dict = {
                            'production_id': obj.id,
                            'from_date': obj.from_date,
                            'to_date': obj.to_date,
                            'produced_at': obj.created_at,
                            'produced_by': self.request.user.full_name
                        }
                        production_date_list.append(production_dict)
                    return Response(production_date_list, status=status.HTTP_200_OK)
                else:
                    return Response({"message": _("No productions present for this from date and to date")},
                                    status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path='remove')
    def remove(self, request, *args, **kwargs):
        queryset = Production.objects.filter(
            reduce(operator.or_, (Q(id=production) for production in request.data.get("production_list"))))
        remove_from_production(self, queryset)
        return Response({"message": _("removed productions from plannings")},
                        status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path='patient-sticker-report', url_name='patient_sticker_report')
    def patient_sticker_report(self, request, *args, **kwargs):
        serializer = PatientsProductionSerializer(data=request.data)
        if serializer.is_valid():
            patient_list = serializer.data.get("patients", None)
            from_date = datetime.datetime.strptime(serializer.data.get("from_date"), '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(serializer.data.get("to_date"), '%Y-%m-%d').date()

            queryset = MedicinePlanning.objects.filter(
                reduce(operator.or_, (Q(patient=term) for term in patient_list)),
                plannings__productions__from_date__gte=from_date, plannings__productions__to_date__lte=to_date)

            medicine_planning_serializer = ProductionReportSerializer(queryset, many=True)
            medicine_planings = medicine_planning_serializer.data
            report_data = []
            for medicine_planing in medicine_planings:
                posology_list = []
                respone = {}
                for planning in medicine_planing["plannings"]:
                    planning_obj = Planning.objects.get(id=planning["id"])
                    if planning_obj.posology_type == "specific_posology":
                        posology = {}
                        type = planning_obj.posology_type
                        result = specific_intake_calculation(planning)
                        posology[type] = result
                        posology_list.append(posology)
                        # medicine_planing["medicine_data"][type] = result

                    elif planning_obj.posology_type in ["standard_posology", "cycle_posology"]:
                        posology = {}
                        type = planning_obj.posology_type
                        result = intake_calculations(planning)
                        posology[type] = result
                        posology[type] = result
                        posology_list.append(posology)
                        # medicine_planing["medicine_data"][type] = result

                    elif planning_obj.posology_type == "each_posology":
                        each_posologies = planning_obj.each_posology_plannings.all()
                        for posology in each_posologies:
                            each_posologies = {}
                            intake = posology.intake_time
                            intake = ','.join(intake)
                            each_posologies["intake"] = intake
                            each_posologies["dosage"] = posology.dosage_amount
                            posology_list.append({"each_posologies": each_posologies})
                            # medicine_planing["medicine_data"]["each_posologies"] = each_posologies

                    elif planning_obj.posology_type == "from_to_posology":
                        from_to_posologies = planning_obj.from_to_posology_plannings.all()
                        if from_to_posologies:
                            for posology in from_to_posologies:
                                from_to_posologies = {}
                                intake = posology.intake_time
                                intake = ','.join(intake)
                                from_to_posologies["intake"] = intake
                                from_to_posologies["dosage"] = posology.dosage_amount
                                posology_list.append({"from_to_posologies": from_to_posologies})

                medicine_planing["medicine_data"]["posologies"] = posology_list

                respone["patient_data"] = medicine_planing.pop("patient_data")
                respone["patient_data"]["from_date"] = from_date.strftime('%Y-%m-%d')
                respone["patient_data"]["to_date"] = to_date.strftime('%Y-%m-%d')
                respone["medicine_data"] = medicine_planing.pop("medicine_data")
                report_data.append(respone)
            if report_data:
                result = generate_pdf("report.html", report_data)
                return result
            return Response({"message": _("No data is produced in this interval ")}, status=status.HTTP_400_BAD_REQUEST)
            # return Response(report_data)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path='delivery-report', url_name='delivery_report')
    def delivery_report(self, request, *args, **kwargs):
        serializer = DeliverySerializer(data=request.data)
        if serializer.is_valid():

            date = datetime.datetime.strptime(serializer.data.get("date"), '%Y-%m-%d').date()
            try:
                hospital = Hospital.objects.get(id=serializer.data.get("hospital_id"))
            except Hospital.DoesNotExist:
                return Response({"message": _("Hospital does not exist")},
                                status=status.HTTP_200_OK)

            produce_data = Production.objects.filter(
                planning__medicine_planning__patient__hospital=serializer.data.get("hospital_id"),
                created_at__date=date)

            patient_id_list = list(set(produce_obj.planning.medicine_planning.patient.id
                                       for produce_obj in produce_data))

            parent_list = []
            for id in patient_id_list:
                queryset = produce_data.filter(planning__medicine_planning__patient__id=id)
                parent_list.append(queryset)

            parent_intacke_list = []
            produced_days = []
            for child_patinet_produce_objs in parent_list:
                patient_intacke_list = []
                diffrence_of_date = []
                for patinet_produce_obj in child_patinet_produce_objs:
                    posology_type = patinet_produce_obj.planning.posology_type
                    max_date = {"patient_name": patinet_produce_obj.planning.medicine_planning.patient.full_name,
                                "from_date": patinet_produce_obj.from_date.strftime('%Y-%m-%d'),
                                "to_date": patinet_produce_obj.to_date.strftime('%Y-%m-%d'),
                                "difference": (patinet_produce_obj.to_date - patinet_produce_obj.from_date).days}
                    diffrence_of_date.append(max_date)
                    if posology_type in ["standard_posology", "specific_posology", "cycle_posology"]:
                        intake_movements = IntakeMoment.objects.filter \
                            (posology_planning__planning=patinet_produce_obj.planning_id)
                        intake = [intake_movement.intake_time for intake_movement in intake_movements]
                        patient_intacke_list.extend(intake)
                    elif posology_type == "each_posology":
                        each_posology_objs = patinet_produce_obj.planning.each_posology_plannings.all()
                        for each_posology_obj in each_posology_objs:
                            intake = each_posology_obj.intake_time
                            patient_intacke_list.extend(intake)
                    elif posology_type == "from_to_posology":
                        each_posology_objs = patinet_produce_obj.planning.from_to_posology_plannings.all()
                        for each_posology_obj in each_posology_objs:
                            intake = each_posology_obj.intake_time
                            patient_intacke_list.extend(intake)
                parent_intacke_list.append(len(set(patient_intacke_list)))
                produced_days.append(diffrence_of_date)

            calculated_days = []
            patients = []
            for produced_day_data in produced_days:
                newlist = sorted(produced_day_data, key=operator.itemgetter('difference'))
                calculated_days.append(newlist[-1].pop("difference"))
                patients.append(newlist[-1])

            for no_intake, days, data in zip(parent_intacke_list, calculated_days, patients):
                intake = mul(no_intake, days)
                data["intake"] = intake

            if patients:
                response = {}
                response["hospital_name"] = hospital.hospital_name
                response["production_date"] = serializer.data.get("date")
                response["patients"] = patients
                response["patient_count"] = len(patients)

                barcode_string = serializer.data.get("hospital_id")+"-"+str(date)
                barcode = BarcodeDrawing("{}".format(barcode_string))
                binaryStuff = barcode.asString('png')
                base64EncodedStr = base64.b64encode(binaryStuff).decode('utf-8')
                response["barcode"] = base64EncodedStr
                result = generate_pdf("delivery_report.html", response)
                return result
                # return Response(response)
            else:
                return Response({"message": _("No data is produced in this interval ")},
                                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False, url_path='delivery-date-list', url_name='delivery_date_list')
    def delivery_date_list(self, request, *args, **kwargs):
        serializer = ReportListSerializer(data=request.data)
        if serializer.is_valid():
            hospital_id = serializer.data.get("hospital_id")
            from_date = datetime.datetime.strptime(serializer.data.get("from_date"), '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(serializer.data.get("to_date"), '%Y-%m-%d').date()
            produce_data = Production.objects.filter(planning__medicine_planning__patient__hospital=hospital_id,
                                                     created_at__date__gte=from_date, created_at__date__lte=to_date)
            serializer_obj = ProductionReportListSerializer(produce_data, many=True)
            if serializer_obj.data:
                produce_date_list = []
                for produce_obj in serializer_obj.data:
                    produce_date_list.append(parse_datetime(produce_obj.get("created_at")).date())
                return Response(set(produce_date_list))
            else:
                return Response(serializer.errors)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ProductionPlanningViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Return the given production plannings.

        list:
            Return a list of all validated production plannings.

        create:
            Create a new production plannings.

        destroy:
            Delete a production plannings.

        update:
            Update a production plannings.

        partial_update:
            Update a production plannings.
    """

    queryset = MedicinePlanning.objects.all()
    serializer_class = ProductionPlanningSerializer
    permission_classes = [CheckPermission, ]
    renderer_classes = (CustomJSONRenderer,)
    required_permission = ["manage_planning", ]

    @staticmethod
    def sorting(queryset, patient_list):
        return [q for p_id in patient_list for q in queryset.filter(patient__id=p_id)]

    def get_queryset(self):
        if self.request.user.role.name == "super_admin":
            search_terms = self.request.query_params.get('patient')
            # month = self.request.query_params.get('month')
            # year = self.request.query_params.get('year')
            if search_terms:
                patient_list = search_terms.split(',')
                return self.sorting(MedicinePlanning.objects.exclude(plannings__isnull=True). \
                                    filter(reduce(operator.or_, (Q(patient=term) for term in patient_list))),
                                    patient_list)
                # created_at__month=month, created_at__year=year)
            return MedicinePlanning.objects.all().exclude(plannings__isnull=True)
        else:
            search_terms = self.request.query_params.get('patient')
            if search_terms:
                patient_list = search_terms.split(',')
                return self.sorting(MedicinePlanning.objects.exclude(plannings__isnull=True). \
                                    filter(reduce(operator.or_, (Q(patient=term) for term in patient_list)),
                                           patient__account_id=self.request.user.account_id), patient_list)
            return MedicinePlanning.objects.exclude(plannings__isnull=True). \
                filter(patient__account_id=self.request.user.account_id)
