from beanie.odm.utils.pydantic import IS_PYDANTIC_V2

if IS_PYDANTIC_V2:
    from pydantic import Secret

    from tests.odm.models import (
        DocWithSecretFields,
        NestedSecret,
        SecretData,
        SecretDoc,
    )

    async def test_secret_model():
        x = await DocWithSecretFields(
            secret_doc=SecretDoc(a="secret1"),
            secret_data=SecretData(b="secret2", nested=7),
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
        assert (
            retrieved.secret_data.get_secret_value().nested.get_secret_value()
            == 7
        )
        assert retrieved.secret_int.get_secret_value() == 5

    async def test_nested_secret_works():
        doc = await NestedSecret(nested=Secret(Secret(777))).insert()
        retrieved = await NestedSecret.get(doc.id)

        assert retrieved.nested.get_secret_value().get_secret_value() == 777
