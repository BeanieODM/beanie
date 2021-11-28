# Revision

This feature helps with concurrent operations. It stores `revision_id` together with the document and changes it on each document update. If the application with the old local copy of the document will try to change it, an exception will be raised. Only when the local copy will be synced with the database, the application will be allowed to change the data. It helps to avoid losses of data.

This feature must be turned on in the `Settings` inner class explicitly.

```python
class Sample(Document):
    num: int
    name: str

    class Settings:
        use_revision = True
```

Any changing operation will check if the local copy of the document has the actual `revision_id` value:

```python
s = await Sample.find_one(Sample.name="TestName")
s.num = 10

# If a concurrent process already changed the doc, the next operation will raise an error
await s.replace()
```

If you want to ignore revision and apply all the changes even if the local copy is outdated, you can use the parameter `ignore_revision`

```python
await s.replace(ignore_revision=True)
```