# -*- coding: utf-8 -*-
"""Altissimo Firestore class file."""
from typing import Dict
from typing import List

from google.cloud import firestore
from google.cloud import firestore_v1
from google.cloud.firestore import DocumentSnapshot
from google.cloud.firestore_v1 import aggregation

from .fastapi import Pagination
from .fastapi import PaginatedList
from .tools import chunks

# pylint: disable=line-too-long
# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes


class FirestoreCollection:
    """Altissimo Firestore Collection class."""

    def __init__(self, db, collection_name):
        """Initialize Collection class."""
        self.collection = db.collection(collection_name)
        self.db = db
        self.name = collection_name

    @classmethod
    def count(cls, ref):
        """Return the number of results in a query reference."""
        for result in aggregation.AggregationQuery(ref).count().get():
            return result[0].value
        return 0

    def create_document(self, doc_id: str, data: dict, remove_id: bool = True) -> dict:
        """Create a document in this collection."""
        ref = self.collection.document(doc_id)
        if remove_id:
            del data["id"]
        ref.create(data)
        doc = ref.get()
        return {"id": doc.id, **doc.to_dict()}

    def delete_document(self, doc_id: str) -> dict:
        """Delete a document in this collection."""
        ref = self.collection.document(doc_id)
        ref.delete()
        return {"id": doc_id}

    def get_document(self, doc_id: str) -> DocumentSnapshot:
        """Return the document from this collection."""
        return self.collection.document(doc_id).get()

    def get_document_dict(self, doc_id, include_id=True) -> dict:
        """Return a document from this collection as a dict."""
        doc = self.get_document(doc_id)
        item = doc.to_dict()
        if include_id:
            item["id"] = doc.id
        return item

    def list_documents(self) -> List[DocumentSnapshot]:
        """Return a list of documents from this collection."""
        items = []
        for doc in self.collection.stream():
            items.append(doc)
        return items
    get_documents = list_documents

    def list_documents_dict(self) -> Dict[str, DocumentSnapshot]:
        """Return a dict of dicts from this collection."""
        items = {}
        for doc in self.list_documents():
            items[doc.id] = doc
        return items
    get_documents_dict = list_documents_dict

    def list_dicts(self, include_id: bool = True) -> List[dict]:
        """Return a documents from this collection as a list of dicts."""
        items = []
        for doc in self.list_documents():
            item = doc.to_dict()
            if include_id:
                item["id"] = doc.id
            items.append(item)
        return items
    get_dicts = list_dicts

    def list_dicts_dict(self, include_id: bool = True) -> Dict[str, dict]:
        """Return documents from this collection as a dict of dicts."""
        items = {}
        for doc in self.list_documents():
            item = doc.to_dict()
            if include_id:
                item["id"] = doc.id
            items[doc.id] = item
        return items
    get_dicts_dict = list_dicts_dict

    def __next_page_query(self, pagination):
        """Return results from a next_page cursor query."""
        snapshot = self.collection.document(pagination.next_cursor).get()
        if not snapshot:
            return self.__default_page_query(pagination)
        direction = firestore.Query.ASCENDING
        if pagination.direction == "descending":
            direction = firestore.Query.DESCENDING

        # create collection query with direction
        ref = self.collection.order_by(pagination.order_by, direction=direction)

        # get next page of results
        ref = ref.start_after(snapshot).limit(pagination.limit + 1)

        # retrieve items from stream
        items = []
        for doc in ref.stream():
            item = doc.to_dict()
            item["id"] = doc.id
            items.append(item)
        return items

    def __previous_page_query(self, pagination):
        """Return results from a previous_page cursor query."""
        snapshot = self.collection.document(pagination.previous_cursor).get()
        if not snapshot:
            return self.__default_page_query(pagination)
        direction = firestore.Query.DESCENDING
        if pagination.direction == "descending":
            direction = firestore.Query.ASCENDING

        # create collection query with direction
        ref = self.collection.order_by(pagination.order_by, direction=direction)

        # get next page of results
        ref = ref.start_after(snapshot).limit(pagination.limit + 1)

        # retrieve items from stream and return in reverse order
        items = []
        for doc in ref.stream():
            item = doc.to_dict()
            item["id"] = doc.id
            items.append(item)
        items.reverse()
        return items

    def __default_page_query(self, pagination):
        """Return results from pagination query with no cursor."""
        # get sort direction
        direction = firestore.Query.ASCENDING
        if pagination.direction == "descending":
            direction = firestore.Query.DESCENDING
        ref = self.collection.order_by(pagination.order_by, direction=direction)

        # check for limit
        if pagination.limit:
            ref = ref.limit(pagination.limit + 1)

        # retrieve items from stream
        items = []
        for doc in ref.stream():
            item = doc.to_dict()
            item["id"] = doc.id
            items.append(item)
        return items

    def list_dicts_paginated(self, pagination: Pagination) -> PaginatedList:
        """Return an embedded list of documents from this collection with pagination."""
        # ref = self.collection

        next_cursor = ""
        previous_cursor = ""

        if pagination.next_cursor:
            items = self.__next_page_query(pagination)
            previous_cursor = items[0]["id"]
            if len(items) > pagination.limit:
                items = items[:-1]
                next_cursor = items[-1]["id"]

        elif pagination.previous_cursor:
            items = self.__previous_page_query(pagination)
            next_cursor = items[-1]["id"]
            if len(items) > pagination.limit:
                items = items[1:]
                previous_cursor = items[0]["id"]

        else:
            items = self.__default_page_query(pagination)
            if len(items) > pagination.limit:
                items = items[:-1]
                next_cursor = items[-1]["id"]

        total = None
        if pagination.include_total:
            total = self.count(self.collection)

        if total:
            return PaginatedList(items=items, next_cursor=next_cursor, previous_cursor=previous_cursor, total=total)
        return PaginatedList(items=items, next_cursor=next_cursor, previous_cursor=previous_cursor)

    def save_document(self, doc_id, data, remove_id=True) -> dict:
        """Save a document in this collection."""
        ref = self.collection.document(doc_id)
        if remove_id:
            del data["id"]
        ref.create(data)
        doc = ref.get()
        return {"id": doc.id, **doc.to_dict()}
    update_document = save_document


class FirestoreUpdate:
    """Altissimo Firestore Update class."""

    def __init__(self, c, data, delete_items=False, diff=False, key_name=None):
        """Initialize a Firestore Update instance."""
        self.c = c
        self.collection = c.name

        self.db = self.c.db

        self.data = data
        self.delete_items = delete_items
        self.diff = diff
        self.key_name = key_name

        self.update(data)

    @classmethod
    def dict_keys(cls, *args: dict):
        """Return a list of keys from one or more dicts."""
        keys = set()
        for data in args:
            keys.update(set(data.keys()))
        return list(keys)

    @classmethod
    def keys_to_str(cls, data: dict) -> dict:
        """Return a dict with all the keys converted to string format."""
        items = {}
        for key, value in data.items():
            items[str(key)] = value
        return items

    @classmethod
    def remap_dict(cls, data: dict, key_name: str) -> Dict[str, dict]:
        """Return a dictionary remapped with a different field as the key."""
        response = {}
        for item in data.values():
            key = item[key_name]
            response[key] = item
        return response

    def __diff_items(self, item_a, item_b):
        """Diff two dict items and return the differences."""
        output = []
        for k in sorted(set(list(item_a) + list(item_b))):
            if self.key_name and k == "id":
                continue
            if k not in item_a:
                output.append(f"  {k}: {item_b[k]} (added)")
                continue
            if k not in item_b:
                output.append(f"  {k}: {item_a[k]} (removed)")
                continue
            a = item_a.get(k)
            b = item_b.get(k)
            if a != b:
                output.append(f"  {k}: {a} -> {b}")
        return output

    def __prepare_adds(self, current, data) -> Dict[str, dict]:
        """Return a dict of records to add to firestore."""
        adds: Dict[str, dict] = {}
        for key, item in data.items():
            if key not in current:
                doc_id = key
                if self.key_name:
                    doc_id = self.c.collection.document().id
                adds[doc_id] = item
        return adds

    def __prepare_deletes(self, current, data) -> List[str]:
        """Return a list of document IDs to delete from Firestore."""
        deletes: List[str] = []
        for key, item in current.items():
            if key not in data:
                doc_id = key
                if self.key_name:
                    doc_id = item["id"]
                deletes.append(doc_id)
        return deletes

    def __prepare_updates(self, current, data) -> Dict[str, dict]:
        """Return a dict of records to update in Firestore."""
        updates: Dict[str, dict] = {}
        for key, item in data.items():
            if key not in current:
                continue
            c = current[key]
            if c == item:
                continue
            output = self.__diff_items(c, item)
            if not output:
                continue
            if self.diff and output:
                print(f"Updating {key}:")
                print("\n".join(output))
            doc_id = key
            if self.key_name:
                doc_id = c["id"]
            updates[doc_id] = item
        return updates

    def __run_batch_adds(self, adds: Dict[str, dict]) -> None:
        """Perform the adds to Firestore."""
        for chunk in chunks(list(adds), 500):
            batch = self.db.batch()
            for doc_id in chunk:
                item = adds[doc_id]
                ref = self.c.collection.document(doc_id)
                batch.set(ref, item)
            batch.commit()
            print(f"Added {len(chunk)} docs to {self.collection}")

    def __run_batch_deletes(self, deletes: List[str]) -> None:
        """Perform the adds to Firestore."""
        if not self.delete_items:
            return
        for chunk in chunks(list(deletes), 500):
            batch = self.db.batch()
            for doc_id in chunk:
                ref = self.c.collection.document(doc_id)
                batch.delete(ref)
            batch.commit()
            print(f"Deleted {len(chunk)} docs from {self.collection}")

    def __run_batch_updates(self, updates: Dict[str, dict]):
        """Perform the adds to Firestore."""
        # do batch updates
        for chunk in chunks(list(updates), 500):
            batch = self.db.batch()
            for doc_id in chunk:
                item = updates[doc_id]
                ref = self.c.collection.document(doc_id)
                batch.set(ref, item)
            batch.commit()
            print(f"Updated {len(chunk)} docs in {self.collection}")

    def prepare_data(self, current, data):
        """Prepare the adds, deletes, and updates."""
        adds = self.__prepare_adds(current, data)
        deletes = self.__prepare_deletes(current, data)
        updates = self.__prepare_updates(current, data)
        print(
            f"[{self.collection}]: "
            f"Adds: {len(adds)}, "
            f"Deletes: {len(deletes)}, "
            f"Updates: {len(updates)}."
        )
        return adds, deletes, updates

    def update(self, data):
        """Run the Update process."""
        current = self.c.list_dicts_dict()

        if self.key_name:
            current = self.remap_dict(current, self.key_name)
            data = self.remap_dict(data, self.key_name)

        data = self.keys_to_str(data)

        adds, deletes, updates = self.prepare_data(current, data)

        self.__run_batch_adds(adds)
        self.__run_batch_deletes(deletes)
        self.__run_batch_updates(updates)

        print(f"[{self.collection}]: Done.")


class Firestore:
    """Altissimo Firestore class."""

    def __init__(self, project=None, credentials=None, database=None):
        """Initialize Firestore class."""
        self.project = project
        self.credentials = credentials
        self.database = database

        self.db = firestore.Client(
            project=project,
            credentials=credentials,
            database=database,
        )
        self.firestore = firestore
        self.firestore_v1 = firestore_v1

    #
    # Collections
    #
    def collection(self, collection_name) -> FirestoreCollection:
        """Return a Collection instance."""
        return FirestoreCollection(self.db, collection_name)

    def create_collection_document(self, collection, doc_id, data, remove_id=True) -> dict:
        """Create the doc in a collection."""
        c = self.collection(collection)
        return c.create_document(doc_id, data, remove_id)
    create_document = create_collection_document

    def delete_collection_document(self, collection, doc_id) -> dict:
        """Delete a document from a collection."""
        return self.collection(collection).delete_document(doc_id)
    delete_document = delete_collection_document

    def get_collection_document(self, collection, doc_id) -> dict:
        """Return the doc in a collection."""
        return self.collection(collection).get_document(doc_id)
    get_doc = get_collection_document
    get_document = get_collection_document

    def get_collection_document_dict(self, collection, doc_id, include_id: bool = True) -> dict:
        """Return a doc from collection as a dictionary."""
        return self.collection(collection).get_document_dict(doc_id, include_id)
    get_doc_dict = get_collection_document_dict
    get_document_dict = get_collection_document_dict

    def list_collection_dicts(self, collection, include_id=True) -> list:
        """Return a list of dicts from a collection."""
        return self.collection(collection).list_dicts(include_id)
    get_collection = list_collection_dicts
    get_collection_dicts = list_collection_dicts
    get_collection_items = list_collection_dicts

    def list_collection_dicts_dict(self, collection, include_id=True) -> Dict[str, dict]:
        """Return a list of dicts from a collection."""
        return self.collection(collection).list_dicts_dict(include_id)
    get_collection_dict = list_collection_dicts_dict
    get_collection_dicts_dict = list_collection_dicts_dict
    get_collection_items_dict = list_collection_dicts_dict

    def list_collection_dicts_paginated(self, collection, pagination) -> PaginatedList:
        """Return a paginated list of dicts from a Firestore collection."""
        return self.collection(collection).list_dicts_paginated(pagination)
    get_collection_dicts_paginated = list_collection_dicts_paginated

    def list_collection_documents(self, collection) -> List[DocumentSnapshot]:
        """Return a list of docs in a collection."""
        return self.collection(collection).list_documents()
    get_docs = list_collection_documents
    get_documents = list_collection_documents
    get_collection_docs = list_collection_documents

    def list_collection_documents_dict(self, collection) -> Dict[str, DocumentSnapshot]:
        """Return documentss from a collection as a dict."""
        return self.collection(collection).list_documents_dict()
    get_docs_dict = list_collection_documents_dict
    get_documents_dict = list_collection_documents_dict
    get_collection_docs_dict = list_collection_documents_dict

    def save_collection_document(self, collection, doc_id, data) -> dict:
        """Save a document in a collection."""
        return self.collection(collection).save_document(doc_id, data)
    save_document = save_collection_document
    update_collection_document = save_collection_document
    update_document = save_collection_document

    #
    # Collection Groups
    #
    def get_collection_group(self, collection, include_id=True) -> list:
        """Return a dict of dicts from a collection group."""
        ref = self.db.collection_group(collection)
        items = []
        for doc in ref.stream():
            item = doc.to_dict()
            if include_id:
                item["id"] = doc.id
            items.append(item)
        return items

    def get_collection_group_dict(self, collection, include_id=True) -> dict:
        """Return a dict of dicts from a collection group."""
        ref = self.db.collection_group(collection)
        items = {}
        for doc in ref.stream():
            item = doc.to_dict()
            if include_id:
                item["id"] = doc.id
            items[doc.id] = item
        return items

    #
    # Update
    #
    def update(self, collection_name, data, delete_items=False, diff=False, key_name=None) -> FirestoreUpdate:
        """Return a Firestore Update instance."""
        c = self.collection(collection_name)
        return FirestoreUpdate(c, data, delete_items, diff, key_name)
    update_collection = update
