import csv

from production.viewsets import *
from production.serializers import *
from collections import OrderedDict
from datetime import datetime, timedelta


def identify_intake(intake):
    if intake == "05:00":
        return "Fast"
    if intake == "08:00":
        return "Breakfast"
    if intake == "12:00":
        return "Lunch"
    if intake == "16:00":
        return "Snack"
    if intake == "18:00":
        return "Dinner"
    if intake == "22:00":
        return "Night"


def ocs_file_generation(production_data):
    file_name = "{0}-Report.csv".format("ocs")
    response = HttpResponse(content_type='text/csv', status=status.HTTP_201_CREATED)
    content_disposition = "attachment; filename=" + file_name
    response['Content-Disposition'] = content_disposition

    writer = csv.DictWriter(response, fieldnames=
    ["Hospital ID (*)", "Hospital name (*)", "Floor", "Room",
     "Patient ID (*)", "Patient Label (*)", "Date of Birth", "Dr. Name",
     "Production Start Date (*)", "Production End Date (*)", "National Code (NC) (*)",
     "Therapeutic Group. VMP", "Therapeutic Group VMPP", "Therapeutic Group 3",
     "Therapeutic Group 4", "Therapeutic Group 5", "Medicine Name (*)",
     "Non-Packable medicine (*)", "If needed (*)", "Special Dose (*)",
     "Dose (*)", "Administration date time (*)", "Intake time (*)", "Intake name",
     "Comments", "Medicine type", "Box size", "SS ID", "Phone", "E-mail"], delimiter=':')

    # writer.writeheader()

    for obj in production_data:
        for planning in obj['plannings']:
            planning_obj = Planning.objects.get(id=planning['id'])
            if planning_obj.posology_type in ['standard_posology', 'cycle_posology', "specific_posology"]:
                for posology in planning_obj.posology_plannings.all():
                    for intake in posology.intake_moments.all():
                        intake_name = identify_intake(intake.intake_time)
                        if 'produced' in planning:
                            for prod_index, production in enumerate(planning['produced']):
                                writer.writerow({"Hospital ID (*)": str(
                                    posology.planning.medicine_planning.patient.hospital.id),
                                    "Hospital name (*)": str(
                                        posology.planning.medicine_planning.patient.hospital),
                                    "Floor": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.hospital.assign_centre_modules.name) else str(
                                        posology.planning.medicine_planning.patient.hospital.assign_centre_modules.name),
                                    "Room": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.room_number) else str(
                                        posology.planning.medicine_planning.patient.room_number),
                                    "Patient ID (*)": str(
                                        posology.planning.medicine_planning.patient.id),
                                    "Patient Label (*)": str(
                                        posology.planning.medicine_planning.patient.full_name),
                                    "Date of Birth": str(
                                        posology.planning.medicine_planning.patient.date_of_birth),
                                    "Dr. Name": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.doctor_name) else str(
                                        posology.planning.medicine_planning.patient.doctor_name),
                                    "Production Start Date (*)": "{}".format(production['from_date']),
                                    "Production End Date (*)": "{}".format(production['to_date']),
                                    "National Code (NC) (*)": str(
                                        posology.planning.medicine_planning.medicine.national_medication_code),
                                    "Therapeutic Group. VMP": " ",
                                    "Therapeutic Group VMPP": " ",
                                    "Therapeutic Group 3": " ",
                                    "Therapeutic Group 4": " ",
                                    "Therapeutic Group 5": " ",
                                    "Medicine Name (*)": str(
                                        posology.planning.medicine_planning.medicine.medicine_name),
                                    "Non-Packable medicine (*)": 1 if posology.planning.medicine_planning.medicine.non_packable_treatment else 0,
                                    "If needed (*)": 1 if posology.planning.if_needed else 0,
                                    "Special Dose (*)": 1 if posology.planning.special_dose else 0,
                                    "Dose (*)": intake.dosage_amount,
                                    "Administration date time (*)": str(
                                        posology.planning.created_at.date()),
                                    "Intake time (*)": intake,
                                    "Intake name": intake_name,
                                    "Comments": posology.planning.comment,
                                    "Medicine type": posology.planning.medicine_planning.medicine.type,
                                    "Box size": posology.planning.medicine_planning.medicine.units_per_box,
                                    "SS ID": posology.planning.medicine_planning.patient.ss_id,
                                    "Phone": posology.planning.medicine_planning.patient.telephone_1,
                                    "E-mail": posology.planning.medicine_planning.patient.email_id})

            if planning_obj.posology_type == "each_posology":
                each_posologies = planning_obj.each_posology_plannings.all()
                for posology in each_posologies:
                    for index, intake in enumerate(posology.intake_time):
                        if 'produced' in planning:
                            for prod_index, production in enumerate(planning['produced']):
                                writer.writerow({"Hospital ID (*)": str(
                                    posology.planning.medicine_planning.patient.hospital.id),
                                    "Hospital name (*)": str(
                                        posology.planning.medicine_planning.patient.hospital),
                                    "Floor": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.hospital.assign_centre_modules.name) else str(
                                        posology.planning.medicine_planning.patient.hospital.assign_centre_modules.name),
                                    "Room": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.room_number) else str(
                                        posology.planning.medicine_planning.patient.room_number),
                                    "Patient ID (*)": str(
                                        posology.planning.medicine_planning.patient.id),
                                    "Patient Label (*)": str(
                                        posology.planning.medicine_planning.patient.full_name),
                                    "Date of Birth": str(
                                        posology.planning.medicine_planning.patient.date_of_birth),
                                    "Dr. Name": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.doctor_name) else str(
                                        posology.planning.medicine_planning.patient.doctor_name),
                                    "Production Start Date (*)": "{}".format(production['from_date']),
                                    "Production End Date (*)": "{}".format(production['to_date']),
                                    "National Code (NC) (*)": str(
                                        posology.planning.medicine_planning.medicine.national_medication_code),
                                    "Therapeutic Group. VMP": " ",
                                    "Therapeutic Group VMPP": " ",
                                    "Therapeutic Group 3": " ",
                                    "Therapeutic Group 4": " ",
                                    "Therapeutic Group 5": " ",
                                    "Medicine Name (*)": str(
                                        posology.planning.medicine_planning.medicine.medicine_name),
                                    "Non-Packable medicine (*)": 1 if posology.planning.medicine_planning.medicine.non_packable_treatment else 0,
                                    "If needed (*)": 1 if posology.planning.if_needed else 0,
                                    "Special Dose (*)": 1 if posology.planning.special_dose else 0,
                                    "Dose (*)": posology.dosage_amount,
                                    "Administration date time (*)": str(
                                        posology.planning.created_at.date()),
                                    "Intake time (*)": intake,
                                    "Intake name": " ",
                                    "Comments": posology.planning.comment,
                                    "Medicine type": posology.planning.medicine_planning.medicine.type,
                                    "Box size": posology.planning.medicine_planning.medicine.units_per_box,
                                    "SS ID": posology.planning.medicine_planning.patient.ss_id,
                                    "Phone": posology.planning.medicine_planning.patient.telephone_1,
                                    "E-mail": posology.planning.medicine_planning.patient.email_id})
            if planning_obj.posology_type == 'from_to_posology':
                from_to_posologies = planning_obj.from_to_posology_plannings.all()
                for posology in from_to_posologies:
                    for index, intake in enumerate(posology.intake_time):
                        if 'produced' in planning:
                            for prod_index, production in enumerate(planning['produced']):
                                writer.writerow({"Hospital ID (*)": str(
                                    posology.planning.medicine_planning.patient.hospital.id),
                                    "Hospital name (*)": str(
                                        posology.planning.medicine_planning.patient.hospital),
                                    "Floor": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.hospital.assign_centre_modules.name) else str(
                                        posology.planning.medicine_planning.patient.hospital.assign_centre_modules.name),
                                    "Room": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.room_number) else str(
                                        posology.planning.medicine_planning.patient.room_number),
                                    "Patient ID (*)": str(
                                        posology.planning.medicine_planning.patient.id),
                                    "Patient Label (*)": str(
                                        posology.planning.medicine_planning.patient.full_name),
                                    "Date of Birth": str(
                                        posology.planning.medicine_planning.patient.date_of_birth),
                                    "Dr. Name": " " if 'None' in str(
                                        posology.planning.medicine_planning.patient.doctor_name) else str(
                                        posology.planning.medicine_planning.patient.doctor_name),
                                    "Production Start Date (*)": "{}".format(production['from_date']),
                                    "Production End Date (*)": "{}".format(production['to_date']),
                                    "National Code (NC) (*)": str(
                                        posology.planning.medicine_planning.medicine.national_medication_code),
                                    "Therapeutic Group. VMP": " ",
                                    "Therapeutic Group VMPP": " ",
                                    "Therapeutic Group 3": " ",
                                    "Therapeutic Group 4": " ",
                                    "Therapeutic Group 5": " ",
                                    "Medicine Name (*)": str(
                                        posology.planning.medicine_planning.medicine.medicine_name),
                                    "Non-Packable medicine (*)": 1 if posology.planning.medicine_planning.medicine.non_packable_treatment else 0,
                                    "If needed (*)": 1 if posology.planning.if_needed else 0,
                                    "Special Dose (*)": 1 if posology.planning.special_dose else 0,
                                    "Dose (*)": posology.dosage_amount,
                                    "Administration date time (*)": str(
                                        posology.planning.created_at.date()),
                                    "Intake time (*)": intake,
                                    "Intake name": " ",
                                    "Comments": posology.planning.comment,
                                    "Medicine type": posology.planning.medicine_planning.medicine.type,
                                    "Box size": posology.planning.medicine_planning.medicine.units_per_box,
                                    "SS ID": posology.planning.medicine_planning.patient.ss_id,
                                    "Phone": posology.planning.medicine_planning.patient.telephone_1,
                                    "E-mail": posology.planning.medicine_planning.patient.email_id})
    return response


def stock_calculation(self, dosage, medicine_planning_id, flag):
    stock_dict = {'user': self.request.user.id,
                  'medicine_planning': medicine_planning_id,
                  'quantity': dosage}
    if flag == 'sent_to_produce':
        stock_dict['type'] = 'out'
        stock_dict['description'] = 'production'
    if flag == 'remove_from_production':
        stock_dict['type'] = 'in'
        stock_dict['description'] = 'production_cancelled'
    stock_serializer = PatientStockManagementSerializer(data=stock_dict)
    stock_serializer.is_valid(raise_exception=True)
    stock_serializer.save()


def production_create(self, production_dict):
    serializer = self.get_serializer(data=production_dict)
    serializer.is_valid(raise_exception=True)
    self.perform_create(serializer)
    return serializer


def posology_check(self, planning_obj, production_dict, planning, prod_record_id):
    stock = 0
    if planning_obj.posology_type == "standard_posology" or planning_obj.posology_type == "specific_posology":
        production_dict["production_record"] = prod_record_id
        planning['produced'] = []
        absence_reasons = planning_obj.medicine_planning.patient.absence_reasons.all()
        if absence_reasons:
            for absence_reason in absence_reasons:
                if planning_obj.end_date:
                    if planning_obj.end_date < absence_reason.release_date:
                        break
                    if absence_reason.release_date < production_dict['from_date']:
                        if absence_reason.return_date:
                            if absence_reason.return_date > production_dict['from_date']:
                                production_dict['from_date'] = absence_reason.return_date + timedelta(days=1)
                            if absence_reason.return_date > production_dict['to_date']:
                                production_dict['to_date'] = production_dict['to_date']
                            if production_dict['to_date'] < planning_obj.start_date:
                                break
                        else:
                            break
                else:
                    if planning_obj.start_date > production_dict['from_date']:
                        break
                    if absence_reason.release_date < production_dict['from_date']:
                        if absence_reason.return_date:
                            if absence_reason.return_date > production_dict['from_date']:
                                production_dict['from_date'] = absence_reason.return_date + timedelta(days=1)
                            if absence_reason.return_date > production_dict['to_date']:
                                production_dict['to_date'] = production_dict['to_date']
                            if production_dict['to_date'] < planning_obj.start_date:
                                break
                        else:
                            break
                days = [(production_dict['from_date'] + timedelta(days=day)).strftime('%A').lower()
                        for day in range(int((production_dict['to_date'] - production_dict['from_date']).days) + 1)]
                day_dict = {i: days.count(i) for i in days}
                for posology in planning_obj.posology_plannings.all():
                    if posology.day in day_dict.keys():
                        dosage = 0
                        for d in posology.intake_moments.all():
                            dosage += d.dosage_amount

                        stock += dosage * day_dict[posology.day]
            planning['produced'].append(production_create(self, production_dict).data)
        else:
            days = [(production_dict['from_date'] + timedelta(days=day)).strftime('%A').lower()
                    for day in range(int((production_dict['to_date'] - production_dict['from_date']).days) + 1)]
            day_dict = {i: days.count(i) for i in days}
            for posology in planning_obj.posology_plannings.all():
                if posology.day in day_dict.keys():
                    dosage = 0
                    for d in posology.intake_moments.all():
                        dosage += d.dosage_amount
                    stock += dosage * day_dict[posology.day]
            planning['produced'].append(production_create(self, production_dict).data)
    if planning_obj.posology_type == "cycle_posology":
        # ignore inactive days
        planning['produced'] = []
        active_period = planning_obj.active_period
        inactive_period = planning_obj.inactive_period
        start_date = planning_obj.start_date
        while start_date <= production_dict['to_date']:
            cycle_production_dict = {'from_date': start_date,
                                     'to_date': start_date + timedelta(days=active_period) - timedelta(days=1),
                                     'planning': planning_obj.id,
                                     "production_record": prod_record_id
                                     }

            diff = cycle_production_dict['to_date'] - cycle_production_dict['from_date']
            for i in range(diff.days + 1):
                day = cycle_production_dict['from_date'] + timedelta(days=i)
                if day == production_dict['from_date']:
                    cycle_production_dict['from_date'] = day

            if cycle_production_dict['to_date'] < production_dict['from_date']:
                pass
            else:
                if production_dict['to_date'] < cycle_production_dict['to_date']:
                    cycle_production_dict['to_date'] = production_dict['to_date']
                absence_reasons = planning_obj.medicine_planning.patient.absence_reasons.all()
                if absence_reasons:
                    for absence_reason in absence_reasons:
                        if absence_reason.release_date < cycle_production_dict['from_date']:
                            if absence_reason.return_date:
                                if absence_reason.return_date > cycle_production_dict['from_date']:
                                    cycle_production_dict['from_date'] = absence_reason.return_date + timedelta(days=1)
                                if absence_reason.return_date > cycle_production_dict['to_date']:
                                    cycle_production_dict['to_date'] = absence_reason.return_date + timedelta(days=1)
                            else:
                                pass
                days = set([(production_dict['from_date'] + timedelta(days=day)).strftime('%A').lower()
                            for day in
                            range(int((production_dict['to_date'] - production_dict['from_date']).days) + 1)])
                dosage = sum(
                    [d.dosage_amount for posology in planning_obj.posology_plannings.all() if posology.day in days
                     for d in posology.intake_moments.all()])
                if dosage != 0:
                    stock += dosage

                planning['produced'].append(production_create(self, cycle_production_dict).data)
            start_date += timedelta(days=active_period) + timedelta(days=inactive_period)
    if planning_obj.posology_type == "each_posology":
        planning['produced'] = []
        each_posologies = planning_obj.each_posology_plannings.all()
        for posology in each_posologies:
            if posology.odd_days:  # if odd days true
                start_date = production_dict['from_date']
                while start_date <= production_dict['to_date']:
                    if start_date.day % 2 != 0:
                        each_production_dict = {
                            "from_date": start_date,
                            "to_date": start_date,
                            "planning": planning_obj.id,
                            "production_record": prod_record_id
                        }
                        absence_reasons = planning_obj.medicine_planning.patient.absence_reasons.all()
                        if absence_reasons:
                            for absence_reason in absence_reasons:
                                if planning_obj.end_date:
                                    if planning_obj.end_date < absence_reason.release_date:
                                        break
                                    if absence_reason.release_date < each_production_dict['from_date']:
                                        if absence_reason.return_date:
                                            if absence_reason.return_date > each_production_dict['from_date']:
                                                each_production_dict[
                                                    'from_date'] = absence_reason.return_date + timedelta(
                                                    days=1)
                                            if absence_reason.return_date > each_production_dict['to_date']:
                                                each_production_dict['to_date'] = each_production_dict['to_date']

                                        else:
                                            break
                                else:
                                    if absence_reason.release_date < each_production_dict['from_date']:
                                        if absence_reason.return_date:
                                            if absence_reason.return_date > each_production_dict['from_date']:
                                                each_production_dict[
                                                    'from_date'] = absence_reason.return_date + timedelta(
                                                    days=1)
                                            if absence_reason.return_date > each_production_dict['to_date']:
                                                each_production_dict['to_date'] = each_production_dict['to_date']
                                        else:
                                            break
                                dosage = len(posology.intake_time) * posology.dosage_amount
                                if dosage != 0:
                                    stock += dosage

                                planning['produced'].append(production_create(self, each_production_dict).data)

                        else:
                            dosage = len(posology.intake_time) * posology.dosage_amount
                            if dosage != 0:
                                stock += dosage
                            planning['produced'].append(production_create(self, each_production_dict).data)
                    start_date += timedelta(days=1)
            if posology.even_days:  # if even days true
                start_date = production_dict['from_date']
                while start_date <= production_dict['to_date']:
                    if start_date.day % 2 == 0:
                        each_production_dict = {
                            "from_date": start_date,
                            "to_date": start_date,
                            "planning": planning_obj.id,
                            "production_record": prod_record_id
                        }
                        absence_reasons = planning_obj.medicine_planning.patient.absence_reasons.all()
                        if absence_reasons:
                            for absence_reason in absence_reasons:
                                if planning_obj.end_date:
                                    if planning_obj.end_date < absence_reason.release_date:
                                        break
                                    if absence_reason.release_date < each_production_dict['from_date']:
                                        if absence_reason.return_date:
                                            if absence_reason.return_date > each_production_dict['from_date']:
                                                each_production_dict[
                                                    'from_date'] = absence_reason.return_date + timedelta(
                                                    days=1)
                                            if absence_reason.return_date > each_production_dict['to_date']:
                                                each_production_dict['to_date'] = each_production_dict['to_date']
                                            dosage = len(posology.intake_time) * posology.dosage_amount
                                            if dosage != 0:
                                                stock += dosage
                                            planning['produced'].append(production_create(self, each_production_dict).data)
                                        else:
                                            break
                                else:
                                    if absence_reason.release_date < each_production_dict['from_date']:
                                        if absence_reason.return_date:
                                            if absence_reason.return_date > each_production_dict['from_date']:
                                                each_production_dict[
                                                    'from_date'] = absence_reason.return_date + timedelta(
                                                    days=1)
                                            if absence_reason.return_date > each_production_dict['to_date']:
                                                each_production_dict['to_date'] = each_production_dict['to_date']
                                            dosage = len(posology.intake_time) * posology.dosage_amount
                                            if dosage != 0:
                                                stock += dosage
                                            planning['produced'].append(production_create(self, each_production_dict).data)
                                        else:
                                            break
                        else:
                            dosage = len(posology.intake_time) * posology.dosage_amount
                            if dosage != 0:
                                stock += dosage
                            planning['produced'].append(production_create(self, each_production_dict).data)
                    start_date += timedelta(days=1)
            if posology.each_x_days and posology.each_posology_days:  # if x days days true
                planning['produced'] = []
                start_date = planning_obj.start_date
                while start_date <= production_dict['to_date']:
                    each_production_dict = {'from_date': start_date,
                                            'to_date': start_date,
                                            'planning': planning_obj.id,
                                            "production_record": prod_record_id
                                            }

                    diff = each_production_dict['to_date'] - each_production_dict['from_date']
                    for i in range(diff.days + 1):
                        day = each_production_dict['from_date'] + timedelta(days=i)
                        if day == production_dict['from_date']:
                            each_production_dict['from_date'] = day

                    if each_production_dict['to_date'] < production_dict['from_date']:
                        pass
                    else:
                        if production_dict['to_date'] < each_production_dict['to_date']:
                            each_production_dict['to_date'] = production_dict['to_date']
                        absence_reasons = planning_obj.medicine_planning.patient.absence_reasons.all()
                        if absence_reasons:
                            for absence_reason in absence_reasons:
                                if planning_obj.end_date:
                                    if planning_obj.end_date < absence_reason.release_date:
                                        break
                                    if absence_reason.release_date < each_production_dict['from_date']:
                                        if absence_reason.return_date:
                                            if absence_reason.return_date > each_production_dict['from_date']:
                                                each_production_dict[
                                                    'from_date'] = absence_reason.return_date + timedelta(
                                                    days=1)
                                            if absence_reason.return_date > each_production_dict['to_date']:
                                                each_production_dict['to_date'] = each_production_dict['to_date']
                                        else:
                                            break
                                else:
                                    if absence_reason.release_date < each_production_dict['from_date']:
                                        if absence_reason.return_date:
                                            if absence_reason.return_date > each_production_dict['from_date']:
                                                each_production_dict[
                                                    'from_date'] = absence_reason.return_date + timedelta(
                                                    days=1)
                                            if absence_reason.return_date > each_production_dict['to_date']:
                                                each_production_dict['to_date'] = each_production_dict['to_date']

                                        else:
                                            break
                                dosage = len(posology.intake_time) * posology.dosage_amount * int(
                                    (each_production_dict['to_date'] - each_production_dict['from_date']).days + 1)
                                if dosage != 0:
                                    stock += dosage
                                planning['produced'].append(production_create(self, each_production_dict).data)
                        else:
                            dosage = len(posology.intake_time) * posology.dosage_amount * int(
                                (each_production_dict['to_date'] - each_production_dict['from_date']).days + 1)
                            if dosage != 0:
                                stock += dosage
                            planning['produced'].append(production_create(self, each_production_dict).data)
                    start_date += timedelta(days=posology.each_posology_days)
    if planning_obj.posology_type == "from_to_posology":
        # consider month lapse and starts at and ends at difference
        if 'produced' in planning:
            planning['produced'] = planning['produced']
        else:
            planning['produced'] = []
        from_to_posologies = planning_obj.from_to_posology_plannings.all()
        for posology in from_to_posologies:
            starts_at = datetime(day=posology.starts_at, month=planning_obj.start_date.month,
                                 year=planning_obj.start_date.year).date()
            ends_at = datetime(day=posology.ends_at, month=planning_obj.start_date.month,
                               year=planning_obj.start_date.year).date()

            is_month_lapse = False
            list_of_months = OrderedDict((tuple(((production_dict['from_date'] + timedelta(_)).strftime(r"%m-%Y")).split("-")), None) for _ in range((production_dict['to_date'] -
                                                                                                                                                      production_dict['from_date']).days)).keys()
            if len(list_of_months) > posology.month_lapse:
                is_month_lapse = True

            if starts_at > production_dict['to_date']:
                break
            if is_month_lapse:
                for month, year in list(list_of_months)[::posology.month_lapse + 1]:
                    monthly_starts_at = datetime(day=posology.starts_at, month=int(month),
                                                 year=int(year)).date()
                    monthly_ends_at = datetime(day=posology.ends_at, month=int(month),
                                               year=int(year)).date()
                    production_from_date = monthly_starts_at - production_dict['from_date']  # 1
                    production_to_date = monthly_ends_at - production_dict['to_date']  # 2
                    if production_dict['from_date'] > monthly_starts_at:
                        monthly_starts_at = production_dict['from_date']

                    from_to_production_dict = {'from_date': monthly_starts_at,
                                               'to_date': monthly_ends_at,
                                               'planning': production_dict['planning']}
                    if production_from_date.days > 0:
                        from_to_production_dict['from_date'] = production_dict['from_date'] + production_from_date
                        from_to_production_dict['to_date'] = production_dict['to_date'] + production_to_date
                    if from_to_production_dict['from_date'] > from_to_production_dict['to_date']:
                        continue
                    if production_dict['from_date'] >= from_to_production_dict['from_date'] and production_dict['to_date'] <= from_to_production_dict['to_date']:
                        continue
                    from_to_production_dict["production_record"] = prod_record_id

                    dosage = len(posology.intake_time) * posology.dosage_amount * int(
                        (from_to_production_dict['to_date'] - from_to_production_dict['from_date']).days + 1)
                    if dosage != 0:
                        stock += dosage
                    planning['produced'].append(production_create(self, from_to_production_dict).data)
            else:
                production_from_date = starts_at - production_dict['from_date']
                from_to_production_dict = {
                    'from_date': starts_at if starts_at > production_dict['from_date'] else production_dict['from_date'],
                    'to_date': ends_at if ends_at < production_dict['to_date'] else production_dict['to_date'],
                    'planning': production_dict['planning']}

                if production_from_date.days > 0:
                    from_to_production_dict['from_date'] = production_dict['from_date'] + production_from_date

                dosage = len(posology.intake_time) * posology.dosage_amount * int(
                    (from_to_production_dict['to_date'] - from_to_production_dict['from_date']).days + 1)
                if dosage != 0:
                    stock += dosage
                from_to_production_dict["production_record"] = prod_record_id
                planning['produced'].append(production_create(self, from_to_production_dict).data)


def posology_check_with_absence_reason(self, planning_obj, production_dict, planning, prod_record_id):
    stock = 0
    if planning_obj.posology_type == "standard_posology" or planning_obj.posology_type == "specific_posology":
        production_dict['production_record'] = prod_record_id
        absence_reasons = planning_obj.medicine_planning.patient.absence_reasons.all()
        if absence_reasons:
            for absence_reason in absence_reasons:
                if planning_obj.end_date:
                    if planning_obj.end_date < absence_reason.release_date:
                        break
                    if absence_reason.release_date < production_dict['from_date']:
                        if absence_reason.return_date:
                            if absence_reason.return_date > production_dict['from_date']:
                                production_dict['from_date'] = absence_reason.return_date + timedelta(days=1)
                            if absence_reason.return_date > production_dict['to_date']:
                                production_dict['to_date'] = production_dict['to_date']
                            if production_dict['to_date'] < planning_obj.start_date:
                                break
                        else:
                            break
                else:
                    if planning_obj.start_date > production_dict['from_date']:
                        break
                    if absence_reason.release_date < production_dict['from_date']:
                        if absence_reason.return_date:
                            if absence_reason.return_date > production_dict['from_date']:
                                production_dict['from_date'] = absence_reason.return_date + timedelta(days=1)
                            if absence_reason.return_date > production_dict['to_date']:
                                production_dict['to_date'] = production_dict['to_date']
                            if production_dict['to_date'] < planning_obj.start_date:
                                break
                        else:
                            break
                days = [(production_dict['from_date'] + timedelta(days=day)).strftime('%A').lower()
                        for day in range(int((production_dict['to_date'] - production_dict['from_date']).days) + 1)]
                day_dict = {i: days.count(i) for i in days}
                for posology in planning_obj.posology_plannings.all():
                    if posology.day in day_dict.keys():
                        dosage = 0
                        for d in posology.intake_moments.all():
                            dosage += d.dosage_amount

                        stock += dosage * day_dict[posology.day]

            planning['produced'].append(production_create(self, production_dict).data)
        else:
            days = [(production_dict['from_date'] + timedelta(days=day)).strftime('%A').lower()
                    for day in range(int((production_dict['to_date'] - production_dict['from_date']).days) + 1)]
            day_dict = {i: days.count(i) for i in days}
            for posology in planning_obj.posology_plannings.all():
                if posology.day in day_dict.keys():
                    dosage = 0
                    for d in posology.intake_moments.all():
                        dosage += d.dosage_amount

                    stock += dosage * day_dict[posology.day]

            planning['produced'].append(production_create(self, production_dict).data)
    elif planning_obj.posology_type == "cycle_posology":
        production_dict['production_record'] = prod_record_id
        if 'produced' in planning:
            planning['produced'] = planning['produced']
        else:
            planning['produced'] = []
        active_period = planning_obj.active_period
        inactive_period = planning_obj.inactive_period
        start_date = planning_obj.start_date
        while start_date <= production_dict['to_date']:
            cycle_production_dict = {'from_date': start_date,
                                     'to_date': start_date + timedelta(days=active_period) - timedelta(days=1),
                                     'planning': planning_obj.id,
                                     'production_record': prod_record_id}
            diff = cycle_production_dict['to_date'] - cycle_production_dict['from_date']
            for i in range(diff.days + 1):
                day = cycle_production_dict['from_date'] + timedelta(days=i)
                if day == production_dict['from_date']:
                    cycle_production_dict['from_date'] = day

            if cycle_production_dict['to_date'] < production_dict['from_date']:
                pass
            else:
                if production_dict['to_date'] < cycle_production_dict['to_date']:
                    cycle_production_dict['to_date'] = production_dict['to_date']

                days = set([(production_dict['from_date'] + timedelta(days=day)).strftime('%A').lower()
                            for day in
                            range(int((production_dict['to_date'] - production_dict['from_date']).days) + 1)])
                dosage = sum(
                    [d.dosage_amount for posology in planning_obj.posology_plannings.all() if posology.day in days
                     for d in posology.intake_moments.all()])
                if dosage != 0:
                    stock += dosage
                planning['produced'].append(production_create(self, cycle_production_dict).data)
            start_date += timedelta(days=active_period) + timedelta(days=inactive_period)
    elif planning_obj.posology_type == "each_posology":
        each_posologies = planning_obj.each_posology_plannings.all()
        for posology in each_posologies:
            if posology.odd_days:
                start_date = production_dict['from_date']
                while start_date <= production_dict['to_date']:
                    if start_date.day % 2 != 0:
                        each_production_dict = {
                            "from_date": start_date,
                            "to_date": start_date,
                            "planning": planning_obj.id,
                            'production_record': prod_record_id
                        }
                        dosage = len(posology.intake_time) * posology.dosage_amount
                        if dosage != 0:
                            stock += dosage
                        planning['produced'].append(production_create(self, each_production_dict).data)
                    start_date += timedelta(days=1)
            if posology.even_days:
                start_date = production_dict['from_date']
                while start_date <= production_dict['to_date']:
                    if start_date.day % 2 == 0:
                        each_production_dict = {
                            "from_date": start_date,
                            "to_date": start_date,
                            "planning": planning_obj.id,
                            'production_record': prod_record_id
                        }
                        dosage = len(posology.intake_time) * posology.dosage_amount
                        if dosage != 0:
                            stock += dosage
                        planning['produced'].append(production_create(self, each_production_dict).data)
                    start_date += timedelta(days=1)
            if posology.each_x_days and posology.each_posology_days:
                each_production_dict = {}
                planning['produced'] = []
                if planning_obj.start_date == production_dict['from_date']:
                    each_production_dict = {'from_date': production_dict['from_date'],
                                            'to_date': production_dict['from_date'],
                                            'planning': production_dict['planning'],
                                            'production_record': prod_record_id}
                    dosage = len(posology.intake_time) * posology.dosage_amount * int(
                        (each_production_dict['to_date'] - each_production_dict['from_date']).days + 1)
                    if dosage != 0:
                        stock += dosage
                    planning['produced'].append(production_create(self, each_production_dict).data)
                if len(planning['produced']) >= 1:
                    for production in planning['produced']:
                        production_to_date = datetime.strptime(production['to_date'], '%Y-%m-%d').date()
                        if production_to_date <= production_dict['to_date']:
                            production_start_date = production_to_date + \
                                                    timedelta(days=posology.each_posology_days) + timedelta(days=1)
                            if production_start_date > production_dict['to_date']:
                                break
                            each_production_dict['from_date'] = production_start_date
                            each_production_dict['to_date'] = production_start_date
                            dosage = len(posology.intake_time) * posology.dosage_amount * int(
                                (each_production_dict['to_date'] - each_production_dict['from_date']).days + 1)
                            if dosage != 0:
                                stock += dosage
                            planning['produced'].append(production_create(self, each_production_dict).data)
    elif planning_obj.posology_type == "from_to_posology":
        if 'produced' in planning:
            planning['produced'] = planning['produced']
        else:
            planning['produced'] = []
        from_to_posologies = planning_obj.from_to_posology_plannings.all()
        for posology in from_to_posologies:
            # if posology.starts_at and posology.ends_at and posology.month_lapse:
            starts_at = datetime(day=posology.starts_at, month=production_dict['from_date'].month,
                                          year=production_dict['from_date'].year).date()
            ends_at = datetime(day=posology.ends_at, month=production_dict['from_date'].month,
                                        year=production_dict['from_date'].year).date()
            is_month_lapse = False
            list_of_months = OrderedDict(
                (tuple(((production_dict['from_date'] + timedelta(_)).strftime(r"%m-%Y")).split("-")), None) for _ in
                range((production_dict['to_date'] -
                       production_dict['from_date']).days)).keys()
            if len(list_of_months) > posology.month_lapse:
                is_month_lapse = True

            if starts_at > production_dict['to_date']:
                break
            # elif production_dict['from_date'] <= ends_at and production_dict['to_date'] >= starts_at:
            # 2020-07-01 <= 2020-07-08 and 2020-07-10 >= 2020-07-02
            # 2020-07-01 <= 2020-07-08 and 2020-10-10 >= 2020-07-02
            if is_month_lapse:
                for month, year in list(list_of_months)[::posology.month_lapse + 1]:
                    monthly_starts_at = datetime(day=posology.starts_at, month=int(month),
                                                 year=int(year)).date()
                    monthly_ends_at = datetime(day=posology.ends_at, month=int(month),
                                               year=int(year)).date()
                    production_from_date = monthly_starts_at - production_dict['from_date']
                    production_to_date = monthly_ends_at - production_dict['to_date']
                    from_to_production_dict = {'from_date': monthly_starts_at if monthly_starts_at > production_dict['from_date'] else production_dict['from_date'],
                                               'to_date': monthly_ends_at,
                                               'planning': production_dict['planning'],
                                               'production_record': prod_record_id}
                    if production_from_date.days > 0:
                        from_to_production_dict['from_date'] = production_dict['from_date'] + production_from_date
                        from_to_production_dict['to_date'] = production_dict['to_date'] + production_to_date
                    if from_to_production_dict['from_date'] > from_to_production_dict['to_date']:
                        continue
                    dosage = len(posology.intake_time) * posology.dosage_amount * int(
                        (from_to_production_dict['to_date'] - from_to_production_dict['from_date']).days + 1)
                    if dosage != 0:
                        stock += dosage
                    planning['produced'].append(production_create(self, from_to_production_dict).data)
            else:
                production_from_date = starts_at - production_dict['from_date']
                from_to_production_dict = {'from_date': starts_at if starts_at > production_dict['from_date'] else production_dict['from_date'],
                                           'to_date': ends_at if ends_at < production_dict['to_date'] else production_dict['to_date'],
                                           'planning': production_dict['planning'],
                                           'production_record': prod_record_id}
                if production_from_date.days > 0:
                    from_to_production_dict['from_date'] = production_dict['from_date'] + production_from_date
                if from_to_production_dict['from_date'] > from_to_production_dict['to_date']:
                    continue
                dosage = len(posology.intake_time) * posology.dosage_amount * int(
                    (from_to_production_dict['to_date'] - from_to_production_dict['from_date']).days + 1)
                if dosage != 0:
                    stock += dosage
                planning['produced'].append(production_create(self, from_to_production_dict).data)
    planning['stock'] = stock


def sent_to_produce(self, result, from_date, to_date, prod_record_id):
    response_data = []
    for index, data in enumerate(result):
        if data not in result[index + 1:]:
            medicine_stock = 0
            for planning in data['plannings']:
                planning_obj = Planning.objects.get(id=planning['id'])
                start_date = planning_obj.start_date
                if start_date > to_date:
                    continue
                end_date = planning_obj.end_date

                absence_reasons_objs = AbsenceReason.objects.filter(
                    patient__medicine_plannings__plannings__id=planning_obj.id)
                absence_reasons_objs = (
                        absence_reasons_objs.filter(release_date__gte=from_date, release_date__lte=to_date) |
                        absence_reasons_objs.filter(return_date__gte=from_date, return_date__lte=to_date) |
                        absence_reasons_objs.filter(release_date__gte=from_date, return_date__lte=to_date)
                ).order_by('release_date')
                if not absence_reasons_objs:
                    production_dict = {'from_date': start_date,
                                       'to_date': end_date if planning_obj.end_date else to_date,
                                       'planning': planning_obj.id}
                    if from_date > start_date:
                        production_dict['from_date'] = from_date
                    if end_date:
                        if end_date > to_date:
                            production_dict['to_date'] = to_date
                        # if end_date < to_date:
                        #     break
                    posology_check(self, planning_obj, production_dict, planning, prod_record_id)
                    stock = planning.get('stock', None)
                    if stock:
                        medicine_stock += stock
                else:
                    planning['produced'] = []
                    return_date = None
                    production_start_date = from_date if from_date > start_date else start_date
                    for absence_reason in absence_reasons_objs:
                        release_date = absence_reason.release_date
                        return_date = absence_reason.return_date
                        if production_start_date >= release_date:
                            if not return_date:
                                break
                            elif production_start_date <= return_date:
                                production_start_date = return_date + timedelta(days=1)

                        # if not return_date or (planning_obj.end_date and release_date >= planning_obj.end_date):
                        #     break
                        production_dict = {'from_date': production_start_date,
                                           'to_date': release_date - timedelta(days=1),
                                           'planning': planning_obj.id}
                        if not end_date:
                            production_to_date = release_date if release_date else to_date
                            production_dict['to_date'] = production_to_date - timedelta(days=1)
                        # elif return_date > end_date and release_date > to_date:
                        #     production_dict['to_date'] = to_date
                        elif start_date < release_date:
                            pass
                        else:
                            production_dict['from_date'] = return_date + timedelta(days=1)
                            production_dict['to_date'] = end_date if planning_obj.end_date else to_date

                        posology_check_with_absence_reason(self, planning_obj, production_dict, planning,
                                                           prod_record_id)
                        stock = planning.get('stock', None)
                        if stock:
                            medicine_stock += stock
                    if return_date:
                        if planning_obj.end_date and planning_obj.end_date > to_date:
                            production_to_date = to_date
                        else:
                            production_to_date = end_date if planning_obj.end_date else to_date
                        production_dict = {'from_date': return_date + timedelta(days=1),
                                           'to_date': production_to_date,
                                           'planning': planning_obj.id}
                        if not planning['produced']:
                            production_dict['from_date'] = production_start_date
                        if production_dict['to_date'] >= production_dict['from_date']:
                            posology_check_with_absence_reason(self, planning_obj, production_dict, planning,
                                                               prod_record_id)
                            stock = planning.get('stock', None)
                            if stock:
                                medicine_stock += stock
            print(medicine_stock)
            if medicine_stock > 0:
                stock_calculation(self, medicine_stock, data['id'], "sent_to_produce")
            response_data.append(data)
    return response_data


def remove_production_stock(self, production):
    if production.planning.posology_type == "standard_posology" or production.planning.posology_type == "specific_posology":
        days = set([(production.from_date + timedelta(days=day)).strftime('%A').lower()
                    for day in range(int((production.to_date - production.from_date).days) + 1)])
        dosage = sum(
            [d.dosage_amount for posology in production.planning.posology_plannings.all() if posology.day in days
             for d in posology.intake_moments.all()])
        if dosage != 0:
            stock_calculation(self, dosage, production.planning.medicine_planning.id, 'remove_from_production')
    elif production.planning.posology_type == "cycle_posology":
        days = set([(production.from_date + timedelta(days=day)).strftime('%A').lower()
                    for day in range(int((production.to_date - production.from_date).days) + 1)])
        dosage = sum(
            [d.dosage_amount for posology in production.planning.posology_plannings.all() if posology.day in days
             for d in posology.intake_moments.all()])
        if dosage != 0:
            stock_calculation(self, dosage, production.planning.medicine_planning.id, 'remove_from_production')
    elif production.planning.posology_type == "each_posology":
        each_posologies = production.planning.each_posology_plannings.all()
        for posology in each_posologies:
            dosage = len(posology.intake_time) * posology.dosage_amount * int(
                (production.to_date - production.from_date).days) + 1
            if dosage != 0:
                stock_calculation(self, dosage, production.planning.medicine_planning.id, 'remove_from_production')
    elif production.planning.posology_type == "from_to_posology":
        from_to_posologies = production.planning.from_to_posology_plannings.all()
        for posology in from_to_posologies:
            dosage = len(posology.intake_time) * posology.dosage_amount * int(
                (production.to_date - production.from_date).days) + 1
            if dosage != 0:
                stock_calculation(self, dosage, production.planning.medicine_planning.id, 'remove_from_production')


def remove_from_production(self, queryset):
    for index, production in enumerate(queryset):
        remove_production_stock(self, production)
        production.delete()
