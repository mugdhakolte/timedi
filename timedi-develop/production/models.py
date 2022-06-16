import uuid
import datetime

from django.db import models
from simple_history.models import HistoricalRecords

from planning.models import *
from timedi_auth.models import TimeStampMixin


class ProductionRecord(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    from_date = models.DateField()
    to_date = models.DateField()
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4))
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="production_records")

    class Meta:
        db_table = 'production_record'
        ordering = ("-updated_at",)

    def __str__(self):
        return "{} {} {}".format(self.from_date, self.to_date, self.user)


class Production(TimeStampMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    from_date = models.DateField()
    to_date = models.DateField()
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name="productions")
    production_record = models.ForeignKey(ProductionRecord, on_delete=models.CASCADE, related_name="produces")
    history = HistoricalRecords(history_id_field=models.UUIDField(default=uuid.uuid4))

    class Meta:
        db_table = 'production'
        ordering = ("-updated_at",)

    def __str__(self):
        return "{} {} {}".format(self.from_date, self.to_date, self.planning)
