from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentStatusCounts, IncidentSummary
from tortoise.functions import Count


class IncidentNotFoundError(Exception):
    pass


class IncidentService:
    @staticmethod
    async def summary(user_id: int) -> IncidentSummary:
        rows = await (
            Incident.filter(user_id=user_id)
            .order_by()
            .annotate(count=Count("id"))
            .group_by("status")
            .values("status", "count")
        )
        counts = IncidentStatusCounts(**{row["status"]: row["count"] for row in rows})
        return IncidentSummary(total=sum(row["count"] for row in rows), by_status=counts)

    @staticmethod
    async def list_incidents(
        user_id: int, offset: int = 0, limit: int = 20
    ) -> list[Incident]:
        return (
            await Incident.filter(user_id=user_id)
            .order_by("-created_at", "-id")
            .offset(offset)
            .limit(limit)
        )

    @staticmethod
    async def get_incident(user_id: int, incident_id: int) -> Incident:
        incident = await Incident.get_or_none(id=incident_id, user_id=user_id)
        if incident is None:
            raise IncidentNotFoundError("Incident not found")
        return incident

    @staticmethod
    async def create_incident(user_id: int, data: IncidentCreate) -> Incident:
        return await Incident.create(user_id=user_id, **data.model_dump())

    @staticmethod
    async def update_incident(
        user_id: int, incident_id: int, data: IncidentCreate
    ) -> Incident:
        incident = await IncidentService.get_incident(user_id, incident_id)
        incident.update_from_dict(data.model_dump())
        await incident.save(
            update_fields=["title", "description", "priority", "status", "updated_at"]
        )
        return incident

    @staticmethod
    async def delete_incident(user_id: int, incident_id: int) -> None:
        incident = await IncidentService.get_incident(user_id, incident_id)
        await incident.delete()
