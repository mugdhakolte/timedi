from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from planning.models import (Planning, PosologyPlanning, IntakeMoment,
                             MedicinePlanning, EachPosologyPlanning, FromToPosologyPlanning, PatientStockManagement)

admin.site.register(Planning, SimpleHistoryAdmin)
admin.site.register(PosologyPlanning, SimpleHistoryAdmin)
admin.site.register(EachPosologyPlanning, SimpleHistoryAdmin)
admin.site.register(IntakeMoment, SimpleHistoryAdmin)
admin.site.register(MedicinePlanning, SimpleHistoryAdmin)
admin.site.register(FromToPosologyPlanning, SimpleHistoryAdmin)
admin.site.register(PatientStockManagement)
