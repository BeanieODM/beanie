# Revision

This feature helps with concurrent operations. 
It stores `revision_id` together with the document and changes it on each document update. 
If the application with an older local copy of the document tries to change it, an exception will be raised. 
Only when the local copy is synced with the database, the application will be allowed to change the data. 
This helps to avoid data losses.

This feature must be explicitly turned on in the `Settings` inner class:

```python
from beanie.sync import Document


class Sample(Document):
    num: int
    name: str

    class Settings:
        use_revision = True
```

Any changing operation will check if the local copy of the document has the up-to-date `revision_id` value:

```python
s = Sample.find_one(Sample.name="TestName").run()
s.num = 10

# If a concurrent process already changed the doc, the next operation will raise an error
s.replace()
```

If you want to ignore revision and apply all the changes even if the local copy is outdated, 
you can use the `ignore_revision` parameter:

```python
s.replace(ignore_revision=True)
```
