from beanie.odm.fields import WriteRules
from beanie.odm.operators.find.array import All
from tests.odm.models import DocumentTestModel, House, Window, Door


async def test_count(documents):
    await documents(4, "uno", True)
    c = await DocumentTestModel.count()
    assert c == 4


async def test_count_with_filter_query(documents):
    await documents(4, "uno", True)
    await documents(2, "dos", True)
    await documents(1, "cuatro", True)
    c = await DocumentTestModel.find_many({"test_str": "dos"}).count()
    assert c == 2


async def test_count_with_relation_id():
    house = House(
        windows=[Window(x=10, y=10), Window(x=11, y=11)],
        door=Door(t=10),
        name="test"
    )
    await house.insert(link_rule=WriteRules.WRITE)
    c1 = await House.find(House.door.id == house.door.id).count()
    assert c1 == 1

async def test_count_with_relation():
    house = House(
        windows=[Window(x=10, y=10), Window(x=11, y=11)],
        door=Door(t=10),
        name="test"
    )
    await house.insert(link_rule=WriteRules.WRITE)
    c2 = await House.find(House.door == house.door).count()
    assert c2 == 1
