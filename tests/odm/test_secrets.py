from beanie.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from tests.odm.models import DocWithSecretFields, SecretData, SecretDoc

    async def test_secret_model():
        x = await DocWithSecretFields(
            secret_doc=SecretDoc(a="secret1"),
            secret_data=SecretData(b="secret2"),
            secret_int=5,
        ).insert()
        retrieved = await DocWithSecretFields.get(x.id)
        assert retrieved == x
        assert retrieved.model_dump(mode="json", exclude="id") == {
            "secret_data": "**********",
            "secret_doc": "**********",
            "secret_int": "**********",
        }
        assert retrieved.secret_doc.get_secret_value().a == "secret1"
        assert retrieved.secret_data.get_secret_value().b == "secret2"
        assert retrieved.secret_int.get_secret_value() == 5
