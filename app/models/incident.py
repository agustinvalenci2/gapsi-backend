from enum import Enum

from tortoise import fields, models


class Priority(str, Enum):
    LOW = "low"
    MID = "middle"
    HIGH = "high"


class IncidenceStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in progress"
    DONE = "done"
    REJECTED = "rejected"


class Incident(models.Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=100)
    description = fields.TextField(null=True)
    priority = fields.CharEnumField(Priority, default=Priority.LOW, db_index=True)
    status = fields.CharEnumField(
        IncidenceStatus, default=IncidenceStatus.PENDING, db_index=True
    )
    user = fields.ForeignKeyField(
        "models.User", related_name="incidents", on_delete=fields.CASCADE
    )
    created_at = fields.DatetimeField(auto_now_add=True, db_index=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "incidence"
