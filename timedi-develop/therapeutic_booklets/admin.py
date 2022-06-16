from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from therapeutic_booklets.models import (Medicine, OfficialMedicine, TherapeuticBook, TherapeuticBookMedicine,
                                         AdditionalCodes)

admin.site.register(TherapeuticBookMedicine)
admin.site.register(TherapeuticBook)
admin.site.register(Medicine, SimpleHistoryAdmin)
admin.site.register(AdditionalCodes)
admin.site.register(OfficialMedicine)
