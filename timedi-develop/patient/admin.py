from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
from patient.models import Patient, AssignCentreModule, IntermediateProduction, Application, AbsenceReason

admin.site.register(Patient, SimpleHistoryAdmin)
admin.site.register(AssignCentreModule)
admin.site.register(IntermediateProduction)
admin.site.register(Application)
admin.site.register(AbsenceReason)
