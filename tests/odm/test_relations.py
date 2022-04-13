import pytest

from beanie.exceptions import DocumentWasNotSaved
from beanie.odm.fields import WriteRules, Link, DeleteRules
from tests.odm.models import Window, Door, House, Roof


@pytest.fixture
def windows_not_inserted():
    return [Window(x=10, y=10), Window(x=11, y=11)]


@pytest.fixture
def door_not_inserted():
    return Door(t=10)


@pytest.fixture
def house_not_inserted(windows_not_inserted, door_not_inserted):
    return House(
        windows=windows_not_inserted, door=door_not_inserted, name="test"
    )


@pytest.fixture
async def house(house_not_inserted):
    return await house_not_inserted.insert(link_rule=WriteRules.WRITE)


@pytest.fixture
async def houses():
    for i in range(10):
        roof = Roof() if i % 2 == 0 else None
        house = await House(
            door=Door(t=i),
            windows=[Window(x=10, y=10 + i), Window(x=11, y=11 + i)],
            roof=roof,
            name="test",
            height=i,
        ).insert(link_rule=WriteRules.WRITE)
        if i == 9:
            await house.windows[0].delete()
            await house.door.delete()


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
    async def test_prefetch_find_many(self, houses):
        items = await House.find(House.height > 2).sort(House.height).to_list()
        assert len(items) == 7
        for window in items[0].windows:
            assert isinstance(window, Link)
        assert isinstance(items[0].door, Link)
        assert items[0].roof is None
        assert isinstance(items[1].roof, Link)

        items = (
            await House.find(House.height > 2, fetch_links=True)
            .sort(House.height)
            .to_list()
        )
        assert len(items) == 7
        for window in items[0].windows:
            assert isinstance(window, Window)
        assert isinstance(items[0].door, Door)
        assert items[0].roof is None
        assert isinstance(items[1].roof, Roof)

        houses = await House.find_many(
            House.height == 9, fetch_links=True
        ).to_list()
        assert len(houses[0].windows) == 1
        assert isinstance(houses[0].door, Link)
        await houses[0].fetch_link(House.door)
        assert isinstance(houses[0].door, Link)

        houses = await House.find_many(
            House.door.t > 5, fetch_links=True
        ).to_list()

        assert len(houses) == 3

        houses = await House.find_many(
            House.windows.y == 15, fetch_links=True
        ).to_list()

        assert len(houses) == 2

        houses = await House.find_many(
            House.height > 5, limit=3, fetch_links=True
        ).to_list()

        assert len(houses) == 3

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

    async def test_find_by_id_of_the_linked_docs(self, house):
        house_lst_1 = await House.find(
            House.door.id == house.door.id
        ).to_list()
        house_lst_2 = await House.find(
            House.door.id == house.door.id, fetch_links=True
        ).to_list()
        assert len(house_lst_1) == 1
        assert len(house_lst_2) == 1

        house_1 = await House.find_one(House.door.id == house.door.id)
        house_2 = await House.find_one(
            House.door.id == house.door.id, fetch_links=True
        )
        assert house_1 is not None
        assert house_2 is not None


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
