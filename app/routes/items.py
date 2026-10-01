from app.models.item import Item
from app.schemas.item import ItemCreate, ItemRead
from app.services.item_service import ItemService
from fastapi import APIRouter, HTTPException, Query, Response, status

router = APIRouter(prefix="/items", tags=["Items"])


async def require_item(item_id: int) -> Item:
    item = await ItemService.get_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item


@router.get("", response_model=list[ItemRead])
async def list_items(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await ItemService.list_items(offset, limit)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int):
    return await require_item(item_id)


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(data: ItemCreate):
    return await ItemService.create_item(data)


@router.put("/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, data: ItemCreate):
    return await ItemService.update_item(await require_item(item_id), data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    await ItemService.delete_item(await require_item(item_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
