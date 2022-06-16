import math

from django.template.loader import get_template, render_to_string

import pdfkit
from pyvirtualdisplay import Display

from production.viewsets import *
from production.serializers import *
from datetime import datetime, timedelta


def posology_check(planning_obj, production_dict, planning):
    stock = 0
    if planning_obj.posology_type == "standard_posology" or planning_obj.posology_type == "specific_posology":
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
            planning['produced'] = [production_dict]

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
            planning['produced'] = [production_dict]
        return stock

    if planning_obj.posology_type == "cycle_posology":
        # ignore inactive days
        planning['produced'] = []
        active_period = planning_obj.active_period
        inactive_period = planning_obj.inactive_period
        start_date = planning_obj.start_date
        while start_date <= production_dict['to_date']:
            cycle_production_dict = {'from_date': start_date,
                                     'to_date': start_date + timedelta(days=active_period) - timedelta(days=1),
                                     'planning': planning_obj.id
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
                planning['produced'].append(cycle_production_dict)
            start_date += timedelta(days=active_period) + timedelta(days=inactive_period)
        return stock
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
                            "planning": planning_obj.id
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

                                planning['produced'].append(each_production_dict)

                        else:
                            dosage = len(posology.intake_time) * posology.dosage_amount
                            if dosage != 0:
                                stock += dosage
                            planning['produced'].append(each_production_dict)
                    start_date += timedelta(days=1)
            if posology.even_days:  # if even days true
                start_date = production_dict['from_date']
                while start_date <= production_dict['to_date']:
                    if start_date.day % 2 == 0:
                        each_production_dict = {
                            "from_date": start_date,
                            "to_date": start_date,
                            "planning": planning_obj.id
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
                                            planning['produced'].append(each_production_dict)
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
                                            planning['produced'].append(each_production_dict)
                                        else:
                                            break
                        else:
                            dosage = len(posology.intake_time) * posology.dosage_amount
                            if dosage != 0:
                                stock += dosage
                            planning['produced'].append(each_production_dict)
                    start_date += timedelta(days=1)
            if posology.each_x_days and posology.each_posology_days:  # if x days days true
                planning['produced'] = []
                start_date = planning_obj.start_date
                while start_date <= production_dict['to_date']:
                    each_production_dict = {'from_date': start_date,
                                            'to_date': start_date,
                                            'planning': planning_obj.id
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
                                planning['produced'].append(each_production_dict)

                        else:
                            dosage = len(posology.intake_time) * posology.dosage_amount * int(
                                (each_production_dict['to_date'] - each_production_dict['from_date']).days + 1)
                            if dosage != 0:
                                stock += dosage
                            planning['produced'].append(each_production_dict)

                    start_date += timedelta(days=posology.each_posology_days)
        return stock
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
            list_of_months = OrderedDict(
                (tuple(((production_dict['from_date'] + timedelta(_)).strftime(r"%m-%Y")).split("-")), None) for _ in
                range((production_dict['to_date'] -
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
                    if production_dict['from_date'] >= from_to_production_dict['from_date'] and production_dict[
                        'to_date'] <= from_to_production_dict['to_date']:
                        continue
                    dosage = len(posology.intake_time) * posology.dosage_amount * int(
                        (from_to_production_dict['to_date'] - from_to_production_dict['from_date']).days + 1)
                    if dosage != 0:
                        stock += dosage
                    planning['produced'].append(from_to_production_dict)
            else:
                production_from_date = starts_at - production_dict['from_date']
                from_to_production_dict = {
                    'from_date': starts_at if starts_at > production_dict['from_date'] else production_dict[
                        'from_date'],
                    'to_date': ends_at if ends_at < production_dict['to_date'] else production_dict['to_date'],
                    'planning': production_dict['planning']}

                if production_from_date.days > 0:
                    from_to_production_dict['from_date'] = production_dict['from_date'] + production_from_date

                dosage = len(posology.intake_time) * posology.dosage_amount * int(
                    (from_to_production_dict['to_date'] - from_to_production_dict['from_date']).days + 1)
                if dosage != 0:
                    stock += dosage
                planning['produced'].append(from_to_production_dict)
        return stock


def posology_check_with_absence_reason(planning_obj, production_dict, planning):
    stock = 0
    if planning_obj.posology_type == "standard_posology" or planning_obj.posology_type == "specific_posology":
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

            planning['produced'].append(production_dict)
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

            planning['produced'].append(production_dict)
        return stock

    elif planning_obj.posology_type == "cycle_posology":
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
                                     'planning': planning_obj.id}
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
                planning['produced'].append(cycle_production_dict)
            start_date += timedelta(days=active_period) + timedelta(days=inactive_period)
        return stock
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
                            "planning": planning_obj.id
                        }
                        dosage = len(posology.intake_time) * posology.dosage_amount
                        if dosage != 0:
                            stock += dosage
                        planning['produced'].append(each_production_dict)
                    start_date += timedelta(days=1)
            if posology.even_days:
                start_date = production_dict['from_date']
                while start_date <= production_dict['to_date']:
                    if start_date.day % 2 == 0:
                        each_production_dict = {
                            "from_date": start_date,
                            "to_date": start_date,
                            "planning": planning_obj.id
                        }
                        dosage = len(posology.intake_time) * posology.dosage_amount
                        if dosage != 0:
                            stock += dosage
                        planning['produced'].append(each_production_dict)
                    start_date += timedelta(days=1)
            if posology.each_x_days and posology.each_posology_days:
                each_production_dict = {}
                planning['produced'] = []
                if planning_obj.start_date == production_dict['from_date']:
                    each_production_dict = {'from_date': production_dict['from_date'],
                                            'to_date': production_dict['from_date'],
                                            'planning': production_dict['planning']}
                    dosage = len(posology.intake_time) * posology.dosage_amount * int(
                        (each_production_dict['to_date'] - each_production_dict['from_date']).days + 1)
                    if dosage != 0:
                        stock += dosage
                    planning['produced'].append(each_production_dict)
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
                            planning['produced'].append(each_production_dict)
        return stock

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
                    from_to_production_dict = {
                        'from_date': monthly_starts_at if monthly_starts_at > production_dict['from_date'] else
                        production_dict['from_date'],
                        'to_date': monthly_ends_at,
                        'planning': production_dict['planning']}
                    if production_from_date.days > 0:
                        from_to_production_dict['from_date'] = production_dict['from_date'] + production_from_date
                        from_to_production_dict['to_date'] = production_dict['to_date'] + production_to_date
                    if from_to_production_dict['from_date'] > from_to_production_dict['to_date']:
                        continue
                    dosage = len(posology.intake_time) * posology.dosage_amount * int(
                        (from_to_production_dict['to_date'] - from_to_production_dict['from_date']).days + 1)
                    if dosage != 0:
                        stock += dosage
                    planning['produced'].append(from_to_production_dict)
            else:
                production_from_date = starts_at - production_dict['from_date']
                from_to_production_dict = {
                    'from_date': starts_at if starts_at > production_dict['from_date'] else production_dict[
                        'from_date'],
                    'to_date': ends_at if ends_at < production_dict['to_date'] else production_dict['to_date'],
                    'planning': production_dict['planning']}
                if production_from_date.days > 0:
                    from_to_production_dict['from_date'] = production_dict['from_date'] + production_from_date
                if from_to_production_dict['from_date'] > from_to_production_dict['to_date']:
                    continue
                dosage = len(posology.intake_time) * posology.dosage_amount * int(
                    (from_to_production_dict['to_date'] - from_to_production_dict['from_date']).days + 1)
                if dosage != 0:
                    stock += dosage
                planning['produced'].append(from_to_production_dict)
        return stock


def stock_calculation(self, result, from_date, to_date):
    response_data = []
    for index, data in enumerate(result):
        if data not in result[index + 1:]:
            simulator_stock = 0
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
                    simulator_stock += posology_check(planning_obj, production_dict, planning)
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

                        simulator_stock += posology_check_with_absence_reason(planning_obj, production_dict, planning)
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
                            simulator_stock += posology_check_with_absence_reason(planning_obj,
                                                                                  production_dict, planning)

            data["simulator_stock"] = simulator_stock
            if data["units_per_box"]:
                data["box_quantity"] = math.ceil(simulator_stock / int(data["units_per_box"]))
            else:
                data["box_quantity"] = ""
            if float(data['stock']) < simulator_stock:
                response_data.append(data)
    return response_data


def generate_pdf(template_src, data, from_date, to_date):
    template_path = template_src
    file_name = "{0}-Report.pdf".format(str('Simulator'))
    html = render_to_string(template_path, {'hospital_list': data, 'from_date': from_date, "to_date": to_date})
    response = HttpResponse(html, content_type='application/pdf')
    disp = Display(backend="xvfb")
    disp.start()
    output = pdfkit.from_string(html, output_path=False)
    disp.stop()
    response.write(output)
    content_disposition = "attachment; filename=" + file_name
    response['Content-Disposition'] = content_disposition
    return response
