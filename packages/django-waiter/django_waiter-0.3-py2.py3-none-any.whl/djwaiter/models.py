import uuid

from django.utils.translation import gettext as _
from django.db import models


class DateTimeModel(models.Model):
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)

    class Meta:
        abstract = True


class UUID4Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
