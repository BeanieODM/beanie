import re
from datetime import date, datetime
from enum import Enum
from uuid import uuid4

import pytest
from bson import Binary, Regex
from pydantic import AnyUrl

from beanie.odm.utils.encoder import Encoder
from beanie.odm.utils.pydantic import IS_PYDANTIC_V2
from tests.odm.models import (
    BsonRegexDoc,
    Child,
    DictEnum,
    DocumentForEncodingTest,
    DocumentForEncodingTestDate,
    DocumentWithComplexDictKey,
    DocumentWithDecimalField,
    DocumentWithEnumKeysDict,
    DocumentWithHttpUrlField,
    DocumentWithKeepNullsFalse,
    DocumentWithStringField,
    ModelWithOptionalField,
    NativeRegexDoc,
    SampleWithMutableObjects,
)


async def test_encode_datetime():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTest(datetime_field=datetime.now())
    await doc.insert()
    new_doc = await DocumentForEncodingTest.get(doc.id)
    assert isinstance(new_doc.datetime_field, datetime)


async def test_encode_date():
    assert isinstance(Encoder().encode(datetime.now()), datetime)

    doc = DocumentForEncodingTestDate()
    await doc.insert()
    new_doc = await DocumentForEncodingTestDate.get(doc.id)
    assert new_doc.date_field == doc.date_field
    assert isinstance(new_doc.date_field, date)


async def test_encode_regex():
    raw_regex = r"^AA.*CC$"
    case_sensitive_regex = re.compile(raw_regex)
    case_insensitive_regex = re.compile(raw_regex, re.I)

    assert isinstance(Encoder().encode(case_sensitive_regex), Regex)
    assert isinstance(Encoder().encode(case_insensitive_regex), Regex)

    matching_doc = DocumentWithStringField(string_field="AABBCC")
    ignore_case_matching_doc = DocumentWithStringField(string_field="aabbcc")
    non_matching_doc = DocumentWithStringField(string_field="abc")

    for doc in (matching_doc, ignore_case_matching_doc, non_matching_doc):
        await doc.insert()

    assert {matching_doc.id, ignore_case_matching_doc.id} == {
        doc.id
        async for doc in DocumentWithStringField.find(
            DocumentWithStringField.string_field == case_insensitive_regex
        )
    }
    assert {matching_doc.id} == {
        doc.id
        async for doc in DocumentWithStringField.find(
            DocumentWithStringField.string_field == case_sensitive_regex
        )
    }


def test_encode_with_custom_encoder():
    assert isinstance(
        Encoder(custom_encoders={datetime: str}).encode(datetime.now()), str
    )


async def test_bytes():
    encoded_b = Encoder().encode(b"test")
    assert isinstance(encoded_b, Binary)
    assert encoded_b.subtype == 0

    doc = DocumentForEncodingTest(bytes_field=b"test")
    await doc.insert()
    new_doc = await DocumentForEncodingTest.get(doc.id)
    assert isinstance(new_doc.bytes_field, bytes)


async def test_bytes_already_binary():
    b = Binary(b"123", 3)
    encoded_b = Encoder().encode(b)
    assert isinstance(encoded_b, Binary)
    assert encoded_b.subtype == 3


async def test_mutable_objects_on_save():
    instance = SampleWithMutableObjects(
        d={"Bar": Child(child_field="Foo")}, lst=[Child(child_field="Bar")]
    )
    await instance.save()
    assert isinstance(instance.d["Bar"], Child)
    assert isinstance(instance.lst[0], Child)


async def test_decimal():
    test_amts = DocumentWithDecimalField(amt=1, other_amt=2)
    await test_amts.insert()
    obj = await DocumentWithDecimalField.get(test_amts.id)
    assert obj.amt == 1
    assert obj.other_amt == 2

    test_amts.amt = 6
    await test_amts.save_changes()

    obj = await DocumentWithDecimalField.get(test_amts.id)
    assert obj.amt == 6

    test_amts = (await DocumentWithDecimalField.find_all().to_list())[0]
    test_amts.other_amt = 7
    await test_amts.save_changes()

    obj = await DocumentWithDecimalField.get(test_amts.id)
    assert obj.other_amt == 7


def test_keep_nulls_false():
    model = ModelWithOptionalField(i=10)
    doc = DocumentWithKeepNullsFalse(m=model)

    encoder = Encoder(keep_nulls=False, to_db=True)
    encoded_doc = encoder.encode(doc)
    assert encoded_doc == {"m": {"i": 10}}


@pytest.mark.skipif(not IS_PYDANTIC_V2, reason="Test only for Pydantic v2")
def test_should_encode_pydantic_v2_url_correctly():
    url = AnyUrl("https://example.com")
    encoder = Encoder()
    encoded_url = encoder.encode(url)
    assert isinstance(encoded_url, str)
    # pydantic2 add trailing slash for naked url. see https://github.com/pydantic/pydantic/issues/6943
    assert encoded_url == "https://example.com/"


async def test_should_be_able_to_save_retrieve_doc_with_url():
    doc = DocumentWithHttpUrlField(url_field="https://example.com")
    assert isinstance(doc.url_field, AnyUrl)
    await doc.save()

    new_doc = await DocumentWithHttpUrlField.find_one(
        DocumentWithHttpUrlField.id == doc.id
    )

    assert isinstance(new_doc.url_field, AnyUrl)
    assert new_doc.url_field == doc.url_field


async def test_dict_with_complex_key():
    assert isinstance(Encoder().encode({uuid4(): datetime.now()}), dict)

    uuid = uuid4()
    # reset microseconds, because it looses by mongo
    dt = datetime.now().replace(microsecond=0)

    doc = DocumentWithComplexDictKey(dict_field={uuid: dt})
    await doc.insert()
    new_doc = await DocumentWithComplexDictKey.get(doc.id)

    assert isinstance(new_doc.dict_field, dict)
    assert new_doc.dict_field.get(uuid) == dt


async def test_dict_with_enum_keys():
    doc = DocumentWithEnumKeysDict(color={DictEnum.RED: "favorite"})
    await doc.save()

    assert isinstance(doc.color, dict)

    for key in doc.color:
        assert isinstance(key, Enum)
        assert key == DictEnum.RED


async def test_native_regex():
    regex = re.compile(r"^1?$|^(11+?)\1+$", (re.I | re.M | re.S) ^ re.UNICODE)
    doc = await NativeRegexDoc(regex=regex).insert()
    new_doc = await NativeRegexDoc.get(doc.id)
    assert new_doc.regex == regex
    assert new_doc.regex.pattern == r"^1?$|^(11+?)\1+$"
    assert new_doc.regex.flags == int(re.I | re.M | re.S ^ re.UNICODE)


async def test_bson_regex():
    regex = Regex(r"^1?$|^(11+?)\1+$")
    doc = await BsonRegexDoc(regex=regex).insert()
    new_doc = await BsonRegexDoc.get(doc.id)
    assert new_doc.regex == Regex(pattern=r"^1?$|^(11+?)\1+$")
