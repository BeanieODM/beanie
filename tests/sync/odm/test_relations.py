import pytest

from beanie.exceptions import DocumentWasNotSaved
from beanie.odm.fields import WriteRules, DeleteRules
from beanie.sync.odm import Link
from tests.sync.models import Window, Door, House, Roof


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
def house(house_not_inserted):
    return house_not_inserted.insert(link_rule=WriteRules.WRITE)


@pytest.fixture
def houses():
    for i in range(10):
        roof = Roof() if i % 2 == 0 else None
        house = House(
            door=Door(t=i),
            windows=[Window(x=10, y=10 + i), Window(x=11, y=11 + i)],
            roof=roof,
            name="test",
            height=i,
        ).insert(link_rule=WriteRules.WRITE)
        if i == 9:
            house.windows[0].delete()
            house.door.delete()


class TestInsert:
    def test_rule_do_nothing(self, house_not_inserted):
        with pytest.raises(DocumentWasNotSaved):
            house_not_inserted.insert()

    def test_rule_write(self, house_not_inserted):
        house_not_inserted.insert(link_rule=WriteRules.WRITE)
        windows = Window.all().to_list()
        assert len(windows) == 2
        doors = Door.all().to_list()
        assert len(doors) == 1
        houses = House.all().to_list()
        assert len(houses) == 1

    def test_insert_with_link(self, house_not_inserted, door_not_inserted):
        door = door_not_inserted.insert()
        link = Door.link_from_id(door.id)
        house_not_inserted.door = link
        house = House.parse_obj(house_not_inserted)
        house.insert(link_rule=WriteRules.WRITE)
        house.json()


class TestFind:
    def test_prefetch_find_many(self, houses):
        items = House.find(House.height > 2).sort(House.height).to_list()
        assert len(items) == 7
        for window in items[0].windows:
            assert isinstance(window, Link)
        assert isinstance(items[0].door, Link)
        assert items[0].roof is None
        assert isinstance(items[1].roof, Link)

        items = (
            House.find(House.height > 2, fetch_links=True)
            .sort(House.height)
            .to_list()
        )
        assert len(items) == 7
        for window in items[0].windows:
            assert isinstance(window, Window)
        assert isinstance(items[0].door, Door)
        assert items[0].roof is None
        assert isinstance(items[1].roof, Roof)

        houses = House.find_many(House.height == 9, fetch_links=True).to_list()
        assert len(houses[0].windows) == 1
        assert isinstance(houses[0].door, Link)
        houses[0].fetch_link(House.door)
        assert isinstance(houses[0].door, Link)

        houses = House.find_many(House.door.t > 5, fetch_links=True).to_list()

        assert len(houses) == 3

        houses = House.find_many(
            House.windows.y == 15, fetch_links=True
        ).to_list()

        assert len(houses) == 2

        houses = House.find_many(
            House.height > 5, limit=3, fetch_links=True
        ).to_list()

        assert len(houses) == 3

    def test_prefetch_find_one(self, house):
        house = House.find_one(House.name == "test").run()
        for window in house.windows:
            assert isinstance(window, Link)
        assert isinstance(house.door, Link)

        house = House.find_one(House.name == "test", fetch_links=True).run()
        for window in house.windows:
            assert isinstance(window, Window)
        assert isinstance(house.door, Door)

        house = House.get(house.id, fetch_links=True).run()
        for window in house.windows:
            assert isinstance(window, Window)
        assert isinstance(house.door, Door)

    def test_fetch(self, house):
        house = House.find_one(House.name == "test").run()
        for window in house.windows:
            assert isinstance(window, Link)
        assert isinstance(house.door, Link)

        house.fetch_all_links()
        for window in house.windows:
            assert isinstance(window, Window)
        assert isinstance(house.door, Door)

        house = House.find_one(House.name == "test").run()
        assert isinstance(house.door, Link)
        house.fetch_link(House.door)
        assert isinstance(house.door, Door)

        for window in house.windows:
            assert isinstance(window, Link)
        house.fetch_link(House.windows)
        for window in house.windows:
            assert isinstance(window, Window)

    def test_find_by_id_of_the_linked_docs(self, house):
        house_lst_1 = House.find(House.door.id == house.door.id).to_list()
        house_lst_2 = House.find(
            House.door.id == house.door.id, fetch_links=True
        ).to_list()
        assert len(house_lst_1) == 1
        assert len(house_lst_2) == 1

        house_1 = House.find_one(House.door.id == house.door.id).run()
        house_2 = House.find_one(
            House.door.id == house.door.id, fetch_links=True
        ).run()
        assert house_1 is not None
        assert house_2 is not None


class TestReplace:
    def test_do_nothing(self, house):
        house.door.t = 100
        house.replace()
        new_house = House.get(house.id, fetch_links=True).run()
        assert new_house.door.t == 10

    def test_write(self, house):
        house.door.t = 100
        house.replace(link_rule=WriteRules.WRITE)
        new_house = House.get(house.id, fetch_links=True).run()
        assert new_house.door.t == 100


class TestSave:
    def test_do_nothing(self, house):
        house.door.t = 100
        house.save()
        new_house = House.get(house.id, fetch_links=True).run()
        assert new_house.door.t == 10

    def test_write(self, house):
        house.door.t = 100
        house.windows = [Window(x=100, y=100)]
        house.save(link_rule=WriteRules.WRITE)
        new_house = House.get(house.id, fetch_links=True).run()
        assert new_house.door.t == 100
        for window in new_house.windows:
            assert window.x == 100
            assert window.y == 100


class TestDelete:
    def test_do_nothing(self, house):
        house.delete()
        door = Door.get(house.door.id).run()
        assert door is not None

        windows = Window.all().to_list()
        assert windows is not None

    def test_delete_links(self, house):
        house.delete(link_rule=DeleteRules.DELETE_LINKS)
        door = Door.get(house.door.id).run()
        assert door is None

        windows = Window.all().to_list()
        assert windows == []
