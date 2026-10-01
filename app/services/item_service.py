from app.models.item import Item
from app.schemas.item import ItemCreate


class ItemService:
    @staticmethod
    async def list_items(offset: int = 0, limit: int = 20) -> list[Item]:
        return await Item.all().order_by("id").offset(offset).limit(limit)

    @staticmethod
    async def get_item(item_id: int) -> Item | None:
        return await Item.get_or_none(id=item_id)

    @staticmethod
    async def create_item(data: ItemCreate) -> Item:
        return await Item.create(**data.model_dump())

    @staticmethod
    async def update_item(item: Item, data: ItemCreate) -> Item:
        item.update_from_dict(data.model_dump())
        await item.save()
        return item

    @staticmethod
    async def delete_item(item: Item) -> None:
        await item.delete()
