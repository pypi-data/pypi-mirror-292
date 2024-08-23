from typing import Any, Dict, List, Type

from bson import ObjectId

from .exceptions import Exceptions
from .mongodb_client import MongoDBClient


class BaseCollection(Exceptions):
    db: str
    collection: str

    def __init__(self, client: MongoDBClient) -> None:
        self.client: MongoDBClient = client

        if not isinstance(self.client, MongoDBClient):  # type: ignore
            raise TypeError(f"The client value must be a instance of MongoDBClient")

        if not hasattr(self, 'db'):
            self.db = self.client.db

    @classmethod
    def __init_subclass__(cls: Type['BaseCollection']) -> None:
        if '__init__' in cls.__dict__:
            raise TypeError(
                f"The subclass '{cls.__name__}' of BaseCollection is not allowed to override __init__"
            )

        if hasattr(cls, 'db'):
            if not isinstance(cls.db, str):  # type: ignore
                raise TypeError(
                    f"The 'db' value in subclass '{cls.__name__}' of BaseCollection must be a string"
                )

        if not hasattr(cls, 'collection'):
            raise ValueError(
                f"The subclass '{cls.__name__}' of BaseCollection must define 'collection'"
            )

        if not isinstance(cls.collection, str):  # type: ignore
            raise TypeError(
                f"The 'collection' value in subclass '{cls.__name__}' of BaseCollection must be a string"
            )

    async def find_one(self, where: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Find one document in the collection.

        Args:
            where (dict):
                A dictionary specifying the criteria for finding the document.

        Returns:
            document (Dict[str, Any]):
                A dictionary representing the document.

        Raises:
            NotFoundError:
                If the document not find.
            FindOneError:
                If an error occurs while finding the document.
            ServerTimeoutError:
                Raised if the server takes too long to respond.
        '''

        return await self.client.find_one(
            db=self.db, collection=self.collection, where=where
        )

    async def find(
        self, where: Dict[str, Any] = {}, skip: int = 0, limit: int = 25
    ) -> List[Dict[str, Any]]:
        '''
        Find documents in the collection.

        Args:
            where (dict):
                A dictionary specifying the criteria for finding the documents.
            skip (int, optional):
                The number of documents to skip before starting to return results. Defaults to 0.
            limit (int, optional):
                The maximum number of documents to return. Defaults to 25.

        Returns:
            Documents (List[Dict[str, Any]]):
                A list of dictionaries, each representing a document.

        Raises:
            FindOneError:
                If an error occurs while finding the documents.
            ServerTimeoutError:
                Raised if the server takes too long to respond.
        '''

        return await self.client.find(
            db=self.db, collection=self.collection, where=where, skip=skip, limit=limit
        )

    async def insert_one(self, document: Dict[str, Any]) -> ObjectId:
        '''
        Insert one document into the collection.

        Args:
            document (dict):
                The document to be inserted into the collection.

        Returns:
            ObjectId (ObjectId):
                The _id of the inserted document.

        Raises:
            InsertError:
                If an error occurs while inserting the document.
            DuplicateKeyError:
                If the document cannot be inserted due to a duplicate key constraint violation.
            ServerTimeoutError:
                Raised if the server takes too long to respond.
        '''

        return await self.client.insert_one(
            db=self.db, collection=self.collection, document=document
        )

    async def insert_many(
        self,
        documents: List[Dict[str, Any]],
        ordered: bool = True,
        bypass_document_validation: bool = False,
    ) -> List[ObjectId]:
        '''
        Insert many documents in the collection.

        Args:
            documents (List[Dict[str, Any]]):
                A list of dictionaries, each representing
                a document to be inserted into the collection.
            ordered (bool):
                If True, documents will be inserted in the order provided,
                and the insertion will stop upon encountering an error. If False, the server
                will attempt to insert all documents, even if some fail.
            bypass_document_validation (bool):
                If True, bypasses server-side validation for the documents being inserted.

        Returns:
            ObjectId`s (list[ObjectId]):
                A list of _ids of the inserted documents, in the order provided.
                If False is passed for the ordered parameter the server may have inserted
                the documents in a different order than what is presented here.

        Raises:
            InsertError:
                If an error occurs while inserting the documents.
            ServerTimeoutError:
                Raised if the server takes too long to respond.
        '''

        return await self.client.insert_many(
            db=self.db,
            collection=self.collection,
            documents=documents,
            ordered=ordered,
            bypass_document_validation=bypass_document_validation,
        )

    async def update_one(
        self, where: Dict[str, Any], update: Dict[str, Any], upsert: bool = False
    ) -> ObjectId | None:
        '''
        Update one document in the collection.

        Args:
            where (dict):
                A dictionary specifying the criteria for finding the document to update.
            update (dict):
                A dictionary specifying the fields and values to update in the document.
            upsert (bool, optional):
                Whether to insert the document if it does not exist. Defaults to False.

        Returns:
            ObjectId | None:
                The _id of the inserted document if an upsert took place. Otherwise ``None``.

        Raises:
            UpdateError:
                If an error occurs while updating the document.
            DuplicateKeyError:
                If the document cannot be inserted due to a duplicate key constraint violation.
            ServerTimeoutError:
                Raised if the server takes too long to respond.
        '''

        return await self.client.update_one(
            db=self.db,
            collection=self.collection,
            where=where,
            update=update,
            upsert=upsert,
        )

    async def delete_one(self, where: Dict[str, Any]) -> None:
        '''
        Delete one document in the collection

        Args:
            where (dict[str, Any]):
                A dictionary specifying the criteria for finding the document to delete.

        Returns:
            None:
                This method does not return a value.

        Raises:
            DeleteError:
                If an error occurs while deleting the document.
            ServerTimeoutError:
                Raised if the server takes too long to respond.
        '''

        await self.client.delete_one(
            db=self.db, collection=self.collection, where=where
        )

    async def drop_collection(self) -> None:
        '''
        Drop the collection from the database

        Returns:
            None:
                This method does not return a value.

        Raises:
            DropCollectionError:
                Raised if an error occurs while dropping the collection.
            ServerTimeoutError:
                Raised if the server takes too long to respond.
        '''

        await self.client.drop_collection(db=self.db, collection=self.collection)

    async def count_documents(self, where: Dict[str, Any]) -> int:
        '''
        Counts the number of documents in the collection.

        Args:
            where (dict[str, Any]):
                A dictionary specifying the criteria to filter documents for counting.

        Returns:
            int:
                The number of documents in the collection that match the given criteria.

        Raises:
            CountDocumentsError:
                Raised if an error occurs while attempting to count the documents.
        '''
        return await self.client.count_documents(
            db=self.db, collection=self.collection, where=where
        )
