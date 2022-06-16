from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from production.models import *

# Register your models here.

admin.site.register(Production, SimpleHistoryAdmin)
admin.site.register(ProductionRecord, SimpleHistoryAdmin)
