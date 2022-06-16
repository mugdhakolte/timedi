def get_day_short_form(day):
    if day == "monday":
        return "Mon"
    elif day == "tuesday":
        return "Tue"
    elif day == "wednesday":
        return "Wed"
    elif day == "thursday":
        return "Thu"
    elif day == "friday":
        return "Fri"
    elif day == "saturday":
        return "Sat"
    elif day == "sunday":
        return "Sun"


def specific_intake_calculation(value):
    firstintake = set()
    secondintake = set()
    thirdintake = set()
    fourthintake = set()

    firstDay = set()
    secondDay = set()
    thirdDay = set()
    fourthDay = set()

    try:
        for posology in value.get('posology_plannings', None):
            for intake_moment in posology.get('intake_moments', None):
                if intake_moment.get('dosage_amount') == '0.25':
                    firstintake.add(intake_moment.get('intake_time'))
                    day = get_day_short_form(posology.get('day'))
                    firstDay.add(day)

                if intake_moment.get('dosage_amount') == '0.50':
                    secondintake.add(intake_moment.get('intake_time'))
                    day = get_day_short_form(posology.get('day'))
                    secondDay.add(day)

                if intake_moment.get('dosage_amount') == '1.00' or intake_moment.get('dosage_amount') == '1':
                    thirdintake.add(intake_moment.get('intake_time'))
                    day = get_day_short_form(posology.get('day'))
                    thirdDay.add(day)

                if intake_moment.get('dosage_amount') == '2.00' or intake_moment.get('dosage_amount') == '2':
                    fourthintake.add(intake_moment.get('intake_time'))
                    day = get_day_short_form(posology.get('day'))
                    fourthDay.add(day)
    except Exception as e:
        raise e
    result = []

    if firstintake:
        first_dosage_dict = {}
        first_dosage_dict["dosage"] = 0.25
        first_dosage_dict.update({"intake": [",".join(firstintake)]})
        first_dosage_dict.update({"days": "|".join(firstDay)})
        result.append(first_dosage_dict)

    if secondintake:
        second_dosage_dict = {}
        second_dosage_dict.update({"dosage": 0.50})
        second_dosage_dict.update({"intake": [",".join(secondintake)]})
        second_dosage_dict.update({"days": "|".join(secondDay)})
        result.append(second_dosage_dict)

    if thirdintake:
        third_dosage_dict = {}
        third_dosage_dict.update({"dosage": '1.00'})
        third_dosage_dict.update({"intake": [",".join(thirdintake)]})
        third_dosage_dict.update({"days": "|".join(thirdDay)})
        result.append(third_dosage_dict)

    if fourthintake:
        fourth_dosage_dict = {}
        fourth_dosage_dict.update({"dosage": '2.00'})
        fourth_dosage_dict.update({"intake": [",".join(fourthintake)]})
        fourth_dosage_dict.update({"days": "|".join(fourthDay)})
        result.append(fourth_dosage_dict)
    return result


def intake_calculations(planning):
    calculations = {
        "sunday": ['0', '0', '0', '0', '0', '0'],
        "monday": ['0', '0', '0', '0', '0', '0'],
        "tuesday": ['0', '0', '0', '0', '0', '0'],
        "wednesday": ['0', '0', '0', '0', '0', '0'],
        "thursday": ['0', '0', '0', '0', '0', '0'],
        "friday": ['0', '0', '0', '0', '0', '0'],
        "saturday": ['0', '0', '0', '0', '0', '0']
    }
    if planning.get('posology_type', None) in ["standard_posology", "cycle_posology"]:

        for posology_planning in planning.get('posology_plannings', []):

            for intake_moment in posology_planning.get("intake_moments", []):
                if posology_planning.get('day', "").lower() == 'sunday':

                    if intake_moment["intake_time"] == "05:00":
                        calculations["sunday"][0] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "08:00":
                        calculations["sunday"][1] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "12:00":
                        calculations["sunday"][2] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "16:00":
                        calculations["sunday"][3] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "18:00":
                        calculations["sunday"][4] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "22:00":
                        calculations["sunday"][5] = intake_moment.get("dosage_amount", '0')

                if posology_planning.get('day', "").lower() == 'monday':
                    if intake_moment["intake_time"] == "05:00":
                        calculations["monday"][0] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "08:00":
                        calculations["monday"][1] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "12:00":
                        calculations["monday"][2] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "16:00":
                        calculations["monday"][3] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "18:00":
                        calculations["monday"][4] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "22:00":
                        calculations["monday"][5] = intake_moment.get("dosage_amount", '0')


                elif posology_planning.get('day', "").lower() == 'tuesday':
                    if intake_moment["intake_time"] == "05:00":
                        calculations["tuesday"][0] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "08:00":
                        calculations["tuesday"][1] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "12:00":
                        calculations["tuesday"][2] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "16:00":
                        calculations["tuesday"][3] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "18:00":
                        calculations["tuesday"][4] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "22:00":
                        calculations["tuesday"][5] = intake_moment.get("dosage_amount", '0')


                elif posology_planning.get('day', "").lower() == 'wednesday':
                    if intake_moment["intake_time"] == "05:00":
                        calculations["wednesday"][0] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "08:00":
                        calculations["wednesday"][1] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "12:00":
                        calculations["wednesday"][2] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "16:00":
                        calculations["wednesday"][3] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "18:00":
                        calculations["wednesday"][4] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "22:00":
                        calculations["wednesday"][5] = intake_moment.get("dosage_amount", '0')


                elif posology_planning.get('day', "").lower() == 'thursday':
                    if intake_moment["intake_time"] == "05:00":
                        calculations["thursday"][0] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "08:00":
                        calculations["thursday"][1] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "12:00":
                        calculations["thursday"][2] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "16:00":
                        calculations["thursday"][3] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "18:00":
                        calculations["thursday"][4] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "22:00":
                        calculations["thursday"][5] = intake_moment.get("dosage_amount", '0')


                elif posology_planning.get('day', "").lower() == 'friday':
                    if intake_moment["intake_time"] == "05:00":
                        calculations["friday"][0] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "08:00":
                        calculations["friday"][1] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "12:00":
                        calculations["friday"][2] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "16:00":
                        calculations["friday"][3] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "18:00":
                        calculations["friday"][4] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "22:00":
                        calculations["friday"][5] = intake_moment.get("dosage_amount", '0')

                elif posology_planning.get('day', "").lower() == 'saturday':
                    if intake_moment["intake_time"] == "05:00":
                        calculations["saturday"][0] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "08:00":
                        calculations["saturday"][1] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "12:00":
                        calculations["saturday"][2] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "16:00":
                        calculations["saturday"][3] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "18:00":
                        calculations["saturday"][4] = intake_moment.get("dosage_amount", '0')

                    elif intake_moment["intake_time"] == "22:00":
                        calculations["saturday"][5] = intake_moment.get("dosage_amount", '0')

    for key, value in dict(calculations).items():
        if value == ['0', '0', '0', '0', '0', '0']:
            del calculations[key]

    days_calculations = list(calculations.keys())
    days = []
    dosage = []
    for day in days_calculations:
        result = get_day_short_form(day)
        days.append(result)
    dosage_calculations = calculations.values()
    for dose in dosage_calculations:
        intake = dose
        intake = '-'.join(intake)
        dosage.append(intake)
    calculations = {}
    calculations["days"] = days
    calculations["dosage"] = dosage
    return calculations
