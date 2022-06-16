from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from hospital.models import Hospital, ProductionSetting, HospitalStockManagement

admin.site.register(Hospital, SimpleHistoryAdmin)
admin.site.register(ProductionSetting)
admin.site.register(HospitalStockManagement)
