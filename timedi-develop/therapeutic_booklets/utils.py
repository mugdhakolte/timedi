import csv
import xlwt

from xhtml2pdf import pisa

from django.utils import timezone
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template, render_to_string


# def csv_to_response(list):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="export.csv"'
#     writer = csv.DictWriter(response, fieldnames=["id", "created_at", "updated_at", "medicine_name",
#                                                   "national_medication_code", "strength",
#                                                   "quantity", "type", "laboratories", "units_per_box",
#                                                   "non_packable_treatment", "price", "account"])
#     writer.writeheader()
#     for data in list.data:
#         writer.writerow(dict(data))
#     return response


def xls_to_response(medicine_list, account_id):
    file_name = "{0}-Report-{1}.xls".format(str(account_id), str(timezone.now().date()))
    response = HttpResponse(content_type='application/ms-excel')
    content_disposition = "attachment; filename=" + file_name
    response['Content-Disposition'] = content_disposition
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("mymodel")

    row_num = 0

    columns = [
        (u"medicine_name", 8000),
        (u"national_medication_code", 8000),
        (u"strength", 8000),
        (u"type", 8000),
        (u"laboratories", 8000),
        (u"units_per_box", 8000),
        (u"non_packable_treatment", 8000),
        (u"price", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1
    for obj in medicine_list.data:
        obj.update((k, "NA") for k, v in obj.items() if v == None)
        row_num += 1
        row = [
            obj["medicine_name"],
            obj["national_medication_code"],
            obj["strength"],
            obj["type"],
            obj["laboratories"],
            obj["units_per_box"],
            obj["non_packable_treatment"],
            obj["price"],
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


def generate_pdf(template_src, medicine_list, account_id):
    template_path = template_src
    file_name = "{0}-Report-{1}.pdf".format(str(account_id), str(timezone.now().date()))
    html = render_to_string(template_path, {'medicine_list': medicine_list.data, 'date': str(timezone.now().date())})
    response = HttpResponse(html, content_type='application/pdf')
    content_disposition = "attachment; filename=" + file_name
    response['Content-Disposition'] = content_disposition
    pisaStatus = pisa.CreatePDF(html, dest=response)
    if pisaStatus.err:
        return HttpResponse(_('Error in pdf creation'))
    return response
