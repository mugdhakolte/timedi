import xlwt
import pdfkit
from datetime import *

from pyvirtualdisplay import Display
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.barcode import createBarcodeDrawing

from django.utils import timezone
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.template.loader import get_template, render_to_string


def mul(intake, produce_day):
    return intake * produce_day


def xls_to_response(production_list):
    file_name = "{0}-Report-{1}.xls".format(str(12), str(timezone.now().date()))
    response = HttpResponse(content_type='application/ms-excel')
    content_disposition = "attachment; filename=" + file_name
    response['Content-Disposition'] = content_disposition
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("mymodel")

    row_num = 0

    columns = [
        (u"From Date", 8000),
        (u"To Date", 8000),
        (u"Planning", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1
    for obj in production_list:
        # obj.update((k, "NA") for k, v in obj.items() if v == None)
        row_num += 1
        row = [
            obj.from_date,
            obj.to_date,
            "{}".format(obj.planning)
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response


class BarcodeDrawing(Drawing):
    def __init__(self, text_value, *args, **kw):
        barcode = createBarcodeDrawing('Code128', value=text_value, barHeight=7 * mm, humanReadable=True)
        Drawing.__init__(self, barcode.width, barcode.height, *args, **kw)
        self.add(barcode, name='barcode')


def generate_pdf(template_src, production_list):
    template_path = template_src
    file_name = "{0}-Report-{1}.pdf".format(str(12), str(timezone.now().date()))
    html = render_to_string(template_path, {'production_list': production_list, 'date': str(timezone.now().date())})
    response = HttpResponse(content_type="application/pdf")
    disp = Display(backend="xvfb")
    disp.start()
    output = pdfkit.from_string(html, output_path=False)
    disp.stop()
    response.write(output)
    content_disposition = "attachment; filename=" + file_name
    response['Content-Disposition'] = content_disposition
    return response
