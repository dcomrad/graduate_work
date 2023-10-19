class MongoBase:
    def __init__(self, collection):
        self.collection = collection

    async def _check_if_exists(self, _filter: dict) -> bool:
        return bool(await self.collection.count_documents(_filter))
