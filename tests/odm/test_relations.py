import pytest

from beanie.exceptions import DocumentWasNotSaved
from beanie.odm.fields import WriteRules, Link, DeleteRules
from tests.odm.models import Window, Door, House


@pytest.fixture
def windows_not_inserted():
    return [Window(x=10, y=10), Window(x=11, y=11)]


@pytest.fixture
def door_not_inserted():
    return Door()


@pytest.fixture
def house_not_inserted(windows_not_inserted, door_not_inserted):
    return House(
        windows=windows_not_inserted, door=door_not_inserted, name="test"
    )


@pytest.fixture
async def house(house_not_inserted):
    return await house_not_inserted.insert(link_rule=WriteRules.WRITE)


class TestInsert:
    async def test_rule_do_nothing(self, house_not_inserted):
        with pytest.raises(DocumentWasNotSaved):
            await house_not_inserted.insert()

    async def test_rule_write(self, house_not_inserted):
        await house_not_inserted.insert(link_rule=WriteRules.WRITE)
        windows = await Window.all().to_list()
        assert len(windows) == 2
        doors = await Door.all().to_list()
        assert len(doors) == 1
        houses = await House.all().to_list()
        assert len(houses) == 1


class TestFind:
    async def test_prefetch_find_many(self, house):
        houses = await House.find(House.name == "test").to_list()
        for window in houses[0].windows:
            assert isinstance(window, Link)
        assert isinstance(houses[0].door, Link)

        houses = await House.find(
            House.name == "test", fetch_links=True
        ).to_list()
        for window in houses[0].windows:
            assert isinstance(window, Window)
        assert isinstance(houses[0].door, Door)

    async def test_prefetch_find_one(self, house):
        house = await House.find_one(House.name == "test")
        for window in house.windows:
            assert isinstance(window, Link)
        assert isinstance(house.door, Link)

        house = await House.find_one(House.name == "test", fetch_links=True)
        for window in house.windows:
            assert isinstance(window, Window)
        assert isinstance(house.door, Door)

        house = await House.get(house.id, fetch_links=True)
        for window in house.windows:
            assert isinstance(window, Window)
        assert isinstance(house.door, Door)

    async def test_fetch(self, house):
        house = await House.find_one(House.name == "test")
        for window in house.windows:
            assert isinstance(window, Link)
        assert isinstance(house.door, Link)

        await house.fetch_all_links()
        for window in house.windows:
            assert isinstance(window, Window)
        assert isinstance(house.door, Door)

        house = await House.find_one(House.name == "test")
        assert isinstance(house.door, Link)
        await house.fetch_link(House.door)
        assert isinstance(house.door, Door)

        for window in house.windows:
            assert isinstance(window, Link)
        await house.fetch_link(House.windows)
        for window in house.windows:
            assert isinstance(window, Window)


class TestReplace:
    async def test_do_nothing(self, house):
        house.door.t = 100
        await house.replace()
        new_house = await House.get(house.id, fetch_links=True)
        assert new_house.door.t == 10

    async def test_write(self, house):
        house.door.t = 100
        await house.replace(link_rule=WriteRules.WRITE)
        new_house = await House.get(house.id, fetch_links=True)
        assert new_house.door.t == 100


class TestSave:
    async def test_do_nothing(self, house):
        house.door.t = 100
        await house.save()
        new_house = await House.get(house.id, fetch_links=True)
        assert new_house.door.t == 10

    async def test_write(self, house):
        house.door.t = 100
        house.windows = [Window(x=100, y=100)]
        await house.save(link_rule=WriteRules.WRITE)
        new_house = await House.get(house.id, fetch_links=True)
        assert new_house.door.t == 100
        for window in new_house.windows:
            assert window.x == 100
            assert window.y == 100


class TestDelete:
    async def test_do_nothing(self, house):
        await house.delete()
        door = await Door.get(house.door.id)
        assert door is not None

        windows = await Window.all().to_list()
        assert windows is not None

    async def test_delete_links(self, house):
        await house.delete(link_rule=DeleteRules.DELETE_LINKS)
        door = await Door.get(house.door.id)
        assert door is None

        windows = await Window.all().to_list()
        assert windows == []
