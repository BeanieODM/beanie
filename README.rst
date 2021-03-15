.. image:: https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/with_text.svg

Beanie - is an asynchronous ODM for MongoDB, based on `Motor <https://motor.readthedocs.io/en/stable/>`_ and `Pydantic <https://pydantic-docs.helpmanual.io/>`_.

It uses an abstraction over Pydantic models and Motor collections to work with the database. Class Document allows to create, replace, update, get, find and aggregate.

Here you can see, how to use Beanie, in simple examples:

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

    # CREATE BEANIE DOCUMENT STRUCTURE

    class SubDocument(BaseModel):
        test_str: str


    class DocumentTestModel(Document):
        test_int: int
        test_list: List[SubDocument]
        test_str: str

    # CREATE MOTOR CLIENT AND DB

    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://user:pass@host:27017/db",
        serverSelectionTimeoutMS=100
    )
    db = client.beanie_db

    # INIT BEANIE

    init_beanie(database=db, document_models=[DocumentTestModel])


---------
Create
---------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create a document (insert it)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document = DocumentTestModel(
        test_int=42,
        test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
        test_str="kipasa",
    )

    await document.create()

^^^^^^^^^^^^^^^^^^^
Insert one document
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document = DocumentTestModel(
        test_int=42,
        test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
        test_str="kipasa",
    )

    await DocumentTestModel.insert_one(document)

^^^^^^^^^^^^^^^^^^^^^
Insert many documents
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document_1 = DocumentTestModel(
        test_int=42,
        test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
        test_str="kipasa",
    )
    document_2 = DocumentTestModel(
        test_int=42,
        test_list=[SubDocument(test_str="foo"), SubDocument(test_str="bar")],
        test_str="kipasa",
    )

    await DocumentTestModel.insert_many([document_1, document_2])

----
Find
----

^^^^^^^^^^^^^^^^
Get the document
^^^^^^^^^^^^^^^^

.. code-block:: python

    document = await DocumentTestModel.get(DOCUMENT_ID)

^^^^^^^^^^^^^^^^^
Find one document
^^^^^^^^^^^^^^^^^

.. code-block:: python

    document = await DocumentTestModel.find_one({"test_str": "kipasa"})

^^^^^^^^^^^^^^^^^^^
Find many documents
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    async for document in DocumentTestModel.find_many({"test_str": "uno"}):
        print(document)

OR

.. code-block:: python

    documents =  await DocumentTestModel.find_many({"test_str": "uno"}).to_list()

^^^^^^^^^^^^^^^^^^^^^^
Find all the documents
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    async for document in DocumentTestModel.find_all()
        print(document)

OR

.. code-block:: python

    documents = await DocumentTestModel.find_all().to_list()

------
Update
------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Replace the document (full update)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    document.test_str = "REPLACED_VALUE"
    await document.replace()

^^^^^^^^^^^^^^^^^^^^
Replace one document
^^^^^^^^^^^^^^^^^^^^

Replace one doc data by another

.. code-block:: python

    new_doc = DocumentTestModel(
        test_int=0,
        test_str='REPLACED_VALUE',
        test_list=[]
    )
    await DocumentTestModel.replace_one({"_id": document.id}, new_doc)

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Update the document (partial update)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

in this example, I'll add an item to the document's "test_list" field

.. code-block:: python

    to_insert = SubDocument(test_str="test")
    await document.update(update_query={"$push": {"test_list": to_insert.dict()}})

^^^^^^^^^^^^^^^^^^^
Update one document
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await DocumentTestModel.update_one(
        update_query={"$set": {"test_list.$.test_str": "foo_foo"}},
        filter_query={"_id": document.id, "test_list.test_str": "foo"},
    )

^^^^^^^^^^^^^^^^^^^^^
Update many documents
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await DocumentTestModel.update_many(
        update_query={"$set": {"test_str": "bar"}},
        filter_query={"test_str": "foo"},
    )

^^^^^^^^^^^^^^^^^^^^^^^^
Update all the documents
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await DocumentTestModel.update_all(
        update_query={"$set": {"test_str": "bar"}}
    )


------
Delete
------

^^^^^^^^^^^^^^^^^^^
Delete the document
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await document.delete()

^^^^^^^^^^^^^^^^^^^^
Delete one documents
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await DocumentTestModel.delete_one({"test_str": "uno"})

^^^^^^^^^^^^^^^^^^^^^
Delete many documents
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await DocumentTestModel.delete_many({"test_str": "dos"})

^^^^^^^^^^^^^^^^^^^^^^^^
Delete all the documents
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    await DocumentTestModel.delete_all()


---------
Aggregate
---------


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