from abc import ABC, abstractmethod
from bson import ObjectId


class StorageProvider(ABC):

    @abstractmethod
    async def retrieve_user(self, search_query: dict) -> dict:
        pass

    @abstractmethod
    async def create_or_update_user(self, user_data: dict) -> tuple[int, ObjectId | None]:
        pass
