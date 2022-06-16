import pdfkit
from datetime import *

from pyvirtualdisplay import Display

from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string


def get_action(action, is_active):
    if action == "+" and is_active:
        return "Added"
    elif action == "-" and is_active:
        return "delete"
    elif action == "~" and is_active:
        return "Modified"
    elif not is_active:
        return "Stopped"


def generate_pdf(template_src, history_list):
    template_path = template_src
    file_name = "{0}-Report-{1}.pdf".format(str(12), str(timezone.now().date()))
    html = render_to_string(template_path, {'history_list': history_list, 'date': str(timezone.now().date())})
    response = HttpResponse(content_type="application/pdf")
    disp = Display(backend="xvfb")
    disp.start()
    output = pdfkit.from_string(html, output_path=False)
    disp.stop()
    response.write(output)
    content_disposition = "attachment; filename=" + file_name
    response['Content-Disposition'] = content_disposition
    return response
