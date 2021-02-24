============
Description
============


Beanie - is asynchronous ORM for MongoDB, based on `Motor <https://motor.readthedocs.io/en/stable/>`_ and `Pydantic <https://pydantic-docs.helpmanual.io/>`_.

Beanie uses an abstraction over Pydantic Models Motor collections to work with mongo. Document and Collection classes allow to create, replace, update, get, find and aggregate.

One collection can be associated with only one Document and it helps to keep it structured.

Here you can see, how to use Beanie in simple examples:

============
Installation
============

----
PIP
----

.. code-block:: bash

    pip install beanie


------
Poetry
------

.. code-block:: bash

    poetry add beanie

============
Usage
============

-----
Init
-----

.. code-block:: python

    from typing import List

    import motor
    from pydantic import BaseSettings, BaseModel

    from collections import Collection
    from documents import Document

    # CREATE MOTOR CLIENT AND DB

    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://user:pass@host:27017/db",
        serverSelectionTimeoutMS=100
    )
    db = client.beanie_db


    # CREATE BEANIE DOCUMENT STRUCTURE

    class SubDocument(BaseModel):
        test_str: str


    class DocumentTestModel(Document):
        test_int: int
        test_list: List[SubDocument]
        test_str: str


    # CREATE BEANIE COLLECTION WITH DocumentTestModel STRUCTURE

    test_collection = Collection(
        name="test_collection", db=db, document_model=DocumentTestModel
    )


---------
Documents
---------

^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create a document (Insert)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document = DocumentTestModel(
        test_int=42,
        test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
        test_str="kipasa",
    )

    await document.create()


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Replace the document (full update)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document.test_str = "REPLACED_VALUE"
    await document.replace()


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Update the document (partial update)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

in this example, I'll add an item to the document's "test_list" field

.. code-block:: python

    to_insert = SubDocument(test_str="test")
    await document.update(update_query={"$push": {"test_list": to_insert.dict()}})

^^^^^^^^^^^^^^^^^^^^^^^
Get the document
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document = await DocumentTestModel.get(DOCUMENT_ID)

^^^^^^^^^^^^^^^^^^^^^^^
Find one document
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document = await DocumentTestModel.find_one({"test_str": "kipasa"})

^^^^^^^^^^^^^^^^^^^^^^^
Find the documents
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    async for document in DocumentTestModel.find({"test_str": "uno"}):
        print(document)

OR

.. code-block:: python

    documents =  await DocumentTestModel.find({"test_str": "uno"}).to_list()

^^^^^^^^^^^^^^^^^^^^^^^
Get all the documents
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    async for document in DocumentTestModel.all()
        print(document)

OR

.. code-block:: python

    documents = await DocumentTestModel.all().to_list()

^^^^^^^^^^^^^^^^^^^^^^^
Delete the document
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await document.delete()

^^^^^^^^^^^^^^^^^^^^^^^
Delete many documents
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await DocumentTestModel.delete_many({"test_str": "wrong"})

^^^^^^^^^^^^^^^^^^^^^^^^^
Delete all the documents
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await DocumentTestModel.delete_all()

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Aggregate from the document model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    async for item in DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ):
        print(item)

OR

.. code-block:: python

    class OutputItem(BaseModel):
        id: str = Field(None, alias="_id")
        total: int

    async for item in DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        item_model=OutputModel
    ):
        print(item)

OR

.. code-block:: python

    results = await DocumentTestModel.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        item_model=OutputModel
    ).to_list()



------------
Collections
------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Insert the document into the collection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    inserted_document = await collection.insert_one(document)


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Replace the document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

     await collection.replace_one(document)

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Update the document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    to_insert = SubDocument(test_str="test")
    await collection.update_one(
        document, update_query={"$push": {"test_list": to_insert.dict()}}
    )

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Update many documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await collection.update_many(
        update_query={"$set": {"test_int": 100}}, filter_query={"test_str": "kipasa"},
    )

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Delete the document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await collection.delete_one(document)

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Delete many documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await collection.delete_many({"test_str": "uno"})

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Delete all the documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await collection.delete_all()

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Get the document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document = await collection.get_one(DOCUMENT_ID)


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Find the document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document = await collection.find_one({"test_str": "one"})

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Find many documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    async for document in collection.find({"test_str": "uno"}):
        print(document)

OR

.. code-block:: python

    documents = await collection.find({"test_str": "uno"}).to_list()

OR

.. code-block:: python

    documents = await collection.find({"test_str": "uno"}).to_list(length=10)

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Get all the documents from the collection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    async for document in collection.all():
        print(document)

OR

.. code-block:: python

    documents = await collection.all().to_list()


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Aggregate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    async for item in collection.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}]
    ):
        print(item)

OR

.. code-block:: python

    class OutputItem(BaseModel):
        id: str = Field(None, alias="_id")
        total: int

    async for item in collection.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        item_model=OutputModel
    ):
        print(item)

OR

.. code-block:: python


    results = await collection.aggregate(
        [{"$group": {"_id": "$test_str", "total": {"$sum": "$test_int"}}}],
        item_model=OutputModel
    ).to_list():
