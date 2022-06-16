from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from invoicing.models import *

admin.site.register(Invoice, SimpleHistoryAdmin)
admin.site.register(InvoiceItem, SimpleHistoryAdmin)
admin.site.register(Store)
admin.site.register(InvoiceIntegration)
admin.site.register(InvoiceRelatedMedicine)
admin.site.register(InvoiceRelatedPatient)
