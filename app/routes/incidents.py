from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentRead, IncidentSummary
from app.services.incident_service import (IncidentNotFoundError,
                                           IncidentService)
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

router = APIRouter(prefix="/incidents", tags=["Incidencias"])


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
async def create_incident(data: IncidentCreate, user: User = Depends(get_current_user)):
    return await IncidentService.create_incident(user.id, data)


@router.get("", response_model=list[IncidentRead])
async def list_incidents(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
):
    return await IncidentService.list_incidents(user.id, offset, limit)


@router.get("/summary", response_model=IncidentSummary)
async def incident_summary(user: User = Depends(get_current_user)):
    return await IncidentService.summary(user.id)


@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: int, user: User = Depends(get_current_user)):
    try:
        return await IncidentService.get_incident(user.id, incident_id)
    except IncidentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.put("/{incident_id}", response_model=IncidentRead)
async def update_incident(
    incident_id: int, data: IncidentCreate, user: User = Depends(get_current_user)
):
    try:
        return await IncidentService.update_incident(user.id, incident_id, data)
    except IncidentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(incident_id: int, user: User = Depends(get_current_user)):
    try:
        await IncidentService.delete_incident(user.id, incident_id)
    except IncidentNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
