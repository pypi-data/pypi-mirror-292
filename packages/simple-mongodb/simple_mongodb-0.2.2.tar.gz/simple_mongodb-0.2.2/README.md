# Simple-MongoDB

<p align="center">
    <a href="https://github.com/Gandori/Simple-MongoDB" target="_blank">
        <img src="https://img.shields.io/badge/3.12-3b78a9?style=for-the-badge&logo=Python&logoColor=ffffff" alt="Documentation">
    </a>
</p>

<p align="center">
    <a href="https://github.com/Gandori/Simple-MongoDB" target="_blank">
        <img src="https://img.shields.io/badge/Documentation-ef5552?style=for-the-badge&logo=Read the Docs&logoColor=ffffff" alt="Documentation">
    </a>
    <a href="https://github.com/Gandori/Simple-MongoDB" target="_blank">
        <img src="https://img.shields.io/badge/Source_code-0953dc?style=for-the-badge&logo=Github&logoColor=fffff" alt="Source Code">
    </a>
</p>


> Warning: This Python package is currently still in development phase

Features

| Feature | Impemented/NotImplemented |
| - | - |
| collection.find_one() | Implemented |
| collection.find_one_with_id() | Implemented |
| collection.find_one_and_delete() | NotImplemented |
| collection.find_one_and_replace() | NotImplemented |
| collection.find_one_and_update() | NotImplemented |
| collection.find() | Implemented |
| collection.find_raw_batches() | NotImplemented |
| collection.insert_one() | Implemented |
| collection.insert_one() the document param supports pure pydantic model | NotImplemented |
| collection.insert_many() the documents param supports list of pydantic models | NotImplemented |
| collection.update_one() | Implemented |
| collection.update_many() | NotImplemented |
| collection.delete_one() | Implemented |
| collection.delete_many() | NotImplemented |
| collection.replace_one() | NotImplemented |
| collection.create_index() | NotImplemented |
| collection.create_indexes() | NotImplemented |
| collection.drop_index() | NotImplemented |
| collection.drop_indexes() | NotImplemented |
| collection.list_indexes() | NotImplemented |
| collection.create_search_index() | NotImplemented |
| collection.create_search_indexes() | NotImplemented |
| collection.drop_search_index() | NotImplemented |
| collection.list_search_indexes() | NotImplemented |
| collection.index_information() | NotImplemented |
| collection.aggregate() | NotImplemented |
| collection.aggregate_raw_batches() | NotImplemented |
| collection.count_documents() | Implemented |
| collection.estimated_document_count() | NotImplemented |
| collection.bulk_write() | NotImplemented |
| collection.distinct() | NotImplemented |
| collection.rename() | NotImplemented |

## Description

Placeholder

## Installation

```sh
pip install simple-mongodb
```

### Simple Example

```python
import asyncio
from typing import Any

from bson import ObjectId
from pydantic import BaseModel

from simple_mongodb import BaseCollection, MongoDBClient


class AccountCollection(BaseCollection):
    db = 'my-db'  # The name of the database or set the enviroment variable MONGODB_DB
    collection = 'account-collection'  # The name of the collection


class Account(BaseModel):
    name: str


async def main() -> None:
    # Initialize a client object and pass the url or set enviroment variables
    #   MONGODB_HOST, MONGODB_PORT,
    #   MONGODB_USERNAME, MONGODB_PASSWORD
    # Is the url param or enviroment variables not set the default values are used
    client: MongoDBClient = MongoDBClient(url='mongodb://user:pass@host:27017')

    # Initialize the account collection
    account_collection: AccountCollection = AccountCollection(client=client)

    account: Account = Account(name='example-name')

    try:

        # Insert the document in the collection
        document: dict[str, Any] = account.model_dump()
        inserted_id: ObjectId = await account_collection.insert_one(document=document)

        # Find the document
        where: dict[str, Any] = {'_id': inserted_id}
        document: dict[str, Any] = await account_collection.find_one(where=where)

        # Update the document
        update: dict[str, Any] = {'$set': {'name': 'other-name'}}
        # Returns the id of the new document if upsert=True
        await account_collection.update_one(where=where, update=update, upsert=False)

    except account_collection.InsertError:
        pass
    except account_collection.FindError:
        pass
    except account_collection.UpdateError:
        pass
    except account_collection.ServerTimeoutError:
        pass

    # Close the db connection
    client.close()


if __name__ == '__main__':
    asyncio.run(main())
```