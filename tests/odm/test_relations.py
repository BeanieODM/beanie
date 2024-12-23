from typing import List

import pytest
from pydantic.fields import Field

from beanie import Document, init_beanie
from beanie.exceptions import DocumentWasNotSaved
from beanie.odm.fields import (
    BackLink,
    DeleteRules,
    Link,
    WriteRules,
)
from beanie.odm.utils.pydantic import (
    IS_PYDANTIC_V2,
    get_model_fields,
    parse_model,
)
from beanie.operators import In, Or
from tests.odm.models import (
    AddressView,
    ADocument,
    BDocument,
    DocumentToBeLinked,
    DocumentWithBackLink,
    DocumentWithBackLinkForNesting,
    DocumentWithLink,
    DocumentWithLinkForNesting,
    DocumentWithListBackLink,
    DocumentWithListLink,
    DocumentWithListOfLinks,
    DocumentWithTextIndexAndLink,
    Door,
    House,
    LinkDocumentForTextSeacrh,
    Lock,
    LongSelfLink,
    LoopedLinksA,
    LoopedLinksB,
    Region,
    Roof,
    RootDocument,
    SelfLinked,
    UsersAddresses,
    Window,
    Yard,
)


def lock_not_inserted_fn():
    return Lock(k=10)


@pytest.fixture
def locks_not_inserted():
    return [Lock(k=10001), Lock(k=20002)]


@pytest.fixture
def window_not_inserted():
    return Window(x=10, y=10, lock=lock_not_inserted_fn())


@pytest.fixture
def windows_not_inserted():
    return [
        Window(
            x=10,
            y=10,
            lock=lock_not_inserted_fn(),
        ),
        Window(
            x=11,
            y=11,
            lock=lock_not_inserted_fn(),
        ),
    ]


@pytest.fixture
def door_not_inserted(window_not_inserted, locks_not_inserted):
    return Door(t=10, window=window_not_inserted, locks=locks_not_inserted)


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
        if i % 2 == 0:
            yards = [Yard(v=10, w=10 + i), Yard(v=11, w=10 + i)]
        else:
            yards = None
        house = await House(
            door=Door(
                t=i,
                window=Window(x=20, y=21 + i, lock=Lock(k=20 + i))
                if i % 2 == 0
                else None,
                locks=[Lock(k=20 + i)],
            ),
            windows=[
                Window(x=10, y=10 + i, lock=Lock(k=10 + i)),
                Window(x=11, y=11 + i, lock=Lock(k=11 + i)),
            ],
            yards=yards,
            roof=roof,
            name="test",
            height=i,
        ).insert(link_rule=WriteRules.WRITE)
        if i == 9:
            await house.windows[0].delete()
            await house.windows[1].lock.delete()
            await house.door.delete()


class TestInsert:
    async def test_rule_do_nothing(self, house_not_inserted):
        with pytest.raises(DocumentWasNotSaved):
            await house_not_inserted.insert()

    async def test_rule_write(self, house_not_inserted):
        await house_not_inserted.insert(link_rule=WriteRules.WRITE)
        locks = await Lock.all().to_list()
        assert len(locks) == 5
        windows = await Window.all().to_list()
        assert len(windows) == 3
        doors = await Door.all().to_list()
        assert len(doors) == 1
        houses = await House.all().to_list()
        assert len(houses) == 1

    async def test_insert_with_link(
        self,
        house_not_inserted,
        door_not_inserted,
        window_not_inserted,
        locks_not_inserted,
    ):
        lock_links = []
        for lock in locks_not_inserted:
            lock = await lock.insert()
            link = Lock.link_from_id(lock.id)
            lock_links.append(link)
        door_not_inserted.locks = lock_links

        door_window_lock = await lock_not_inserted_fn().insert()
        door_window_lock_link = Lock.link_from_id(door_window_lock.id)
        window_not_inserted.lock = door_window_lock_link

        door_window = await window_not_inserted.insert()
        door_window_link = Window.link_from_id(door_window.id)
        door_not_inserted.window = door_window_link

        door = await door_not_inserted.insert()
        door_link = Door.link_from_id(door.id)
        house_not_inserted.door = door_link

        house = parse_model(House, house_not_inserted)
        await house.insert(link_rule=WriteRules.WRITE)

        if IS_PYDANTIC_V2:
            json_str = house.model_dump_json()
        else:
            json_str = house.json()
        assert json_str is not None

    async def test_multi_insert_links(self):
        house = House(name="random", windows=[], door=Door())
        window = await Window(x=13, y=23).insert()
        assert window.id
        house.windows.append(window)

        house = await house.insert(link_rule=WriteRules.WRITE)
        new_window_1 = Window(x=11, y=22)
        assert new_window_1.id is None
        house.windows.append(new_window_1)
        new_window_2 = Window(x=12, y=23)
        assert new_window_2.id is None
        house.windows.append(new_window_2)
        await house.save(link_rule=WriteRules.WRITE)
        for win in house.windows:
            assert isinstance(win, Window)
            assert win.id
        assert new_window_1.id is not None
        assert new_window_2.id is not None

    async def test_fetch_after_insert(self, house_not_inserted):
        # TODO: what is the point of this test if nothing was inserted to DB?
        await house_not_inserted.fetch_all_links()


class TestFind:
    async def test_prefetch_find_many(self, houses):
        items = await House.find(House.height > 2).sort(House.height).to_list()
        assert len(items) == 7
        for window in items[0].windows:
            assert isinstance(window, Link)
        assert items[0].yards is None
        for yard in items[1].yards:
            assert isinstance(yard, Link)
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
            assert isinstance(window.lock, Lock)
        assert items[0].yards == []
        for yard in items[1].yards:
            assert isinstance(yard, Yard)
        assert isinstance(items[0].door, Door)
        assert isinstance(items[1].door.window, Window)
        assert items[0].door.window is None
        assert isinstance(items[1].door.window.lock, Lock)
        for lock in items[0].door.locks:
            assert isinstance(lock, Lock)
        assert items[0].roof is None
        assert isinstance(items[1].roof, Roof)

        houses = await House.find_many(
            House.height == 9, fetch_links=True
        ).to_list()
        assert len(houses[0].windows) == 1
        assert isinstance(houses[0].windows[0].lock, Link)
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

    async def test_prefect_count(self, houses):
        c = await House.find(House.door.t > 5, fetch_links=True).count()
        assert c == 3

        c = await House.find_one(House.door.t > 5, fetch_links=True).count()
        assert c == 3

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
            assert isinstance(window.lock, Lock)
        assert isinstance(house.door, Door)
        assert isinstance(house.door.window, Window)
        for lock in house.door.locks:
            assert isinstance(lock, Lock)

        house = await House.find_one(House.name == "test")
        assert isinstance(house.door, Link)
        await house.fetch_link(House.door)
        assert isinstance(house.door, Door)
        assert isinstance(house.door.window, Window)
        for lock in house.door.locks:
            assert isinstance(lock, Lock)

        for window in house.windows:
            assert isinstance(window, Link)
        await house.fetch_link(House.windows)
        for window in house.windows:
            assert isinstance(window, Window)
            assert isinstance(window.lock, Lock)

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

    async def test_find_by_id_list_of_the_linked_docs(self, houses):
        items = (
            await House.find(House.height < 3, fetch_links=True)
            .sort(House.height)
            .to_list()
        )
        assert len(items) == 3

        house_lst_1 = await House.find(
            Or(
                House.door.id == items[0].door.id,
                In(House.door.id, [items[1].door.id, items[2].door.id]),
            )
        ).to_list()
        house_lst_2 = await House.find(
            Or(
                House.door.id == items[0].door.id,
                In(House.door.id, [items[1].door.id, items[2].door.id]),
            ),
            fetch_links=True,
        ).to_list()

        assert len(house_lst_1) == 3
        assert len(house_lst_2) == 3

    async def test_fetch_list_with_some_prefetched(self):
        docs = []
        for i in range(10):
            doc = DocumentToBeLinked()
            await doc.save()
            docs.append(doc)

        doc_with_links = DocumentWithListOfLinks(links=docs)
        await doc_with_links.save()

        doc_with_links = await DocumentWithListOfLinks.get(
            doc_with_links.id, fetch_links=False
        )
        doc_with_links.links[-1] = await doc_with_links.links[-1].fetch()

        await doc_with_links.fetch_all_links()

        for link in doc_with_links.links:
            assert isinstance(link, DocumentToBeLinked)

        assert len(doc_with_links.links) == 10

        # test order
        for i in range(10):
            assert doc_with_links.links[i].id == docs[i].id

    async def test_text_search(self):
        doc = DocumentWithTextIndexAndLink(
            s="hello world", link=LinkDocumentForTextSeacrh(i=1)
        )
        await doc.insert(link_rule=WriteRules.WRITE)

        doc2 = DocumentWithTextIndexAndLink(
            s="hi world", link=LinkDocumentForTextSeacrh(i=2)
        )
        await doc2.insert(link_rule=WriteRules.WRITE)

        docs = await DocumentWithTextIndexAndLink.find(
            {"$text": {"$search": "hello"}}, fetch_links=True
        ).to_list()
        assert len(docs) == 1

    async def test_self_nesting_find_parameters(self):
        self_linked_doc = LongSelfLink()
        await self_linked_doc.insert(link_rule=WriteRules.WRITE)
        self_linked_doc.link = self_linked_doc
        await self_linked_doc.save()

        self_linked_doc = await LongSelfLink.find_one(
            nesting_depth=4, fetch_links=True
        )
        assert self_linked_doc.link.link.link.link.id == self_linked_doc.id
        assert isinstance(self_linked_doc.link.link.link.link.link, Link)

        self_linked_doc = await LongSelfLink.find_one(
            nesting_depth=0, fetch_links=True
        )
        assert isinstance(self_linked_doc.link, Link)

    async def test_nesting_find_parameters(self):
        back_link_doc = DocumentWithBackLinkForNesting(i=1)
        await back_link_doc.insert()
        link_doc = DocumentWithLinkForNesting(link=back_link_doc, s="TEST")
        await link_doc.insert()

        doc = await DocumentWithBackLinkForNesting.find_one(
            DocumentWithBackLinkForNesting.i == 1,
            fetch_links=True,
            nesting_depths_per_field={"back_link": 2},
        )
        assert doc.back_link.link.id == doc.id
        assert isinstance(doc.back_link.link.back_link, BackLink)


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
        new_window = Window(x=100, y=100, lock=Lock(k=100))
        house.windows = [new_window]
        assert new_window.id is None
        await house.save(link_rule=WriteRules.WRITE)
        new_house = await House.get(house.id, fetch_links=True)
        assert new_house.door.t == 100
        for window in new_house.windows:
            assert window.x == 100
            assert window.y == 100
            assert window.id is not None
            assert isinstance(window.lock, Lock)
            assert window.lock.k == 100
            assert window.lock.id is not None
        assert new_window.id is not None


class TestDelete:
    async def test_do_nothing(self, house):
        await house.delete()
        door = await Door.get(house.door.id)
        assert door is not None

        windows = await Window.all().to_list()
        assert windows is not None

        locks = await Lock.all().to_list()
        assert locks is not None

    async def test_delete_links(self, house):
        await house.delete(link_rule=DeleteRules.DELETE_LINKS)
        door = await Door.get(house.door.id)
        assert door is None

        windows = await Window.all().to_list()
        assert windows == []

        locks = await Lock.all().to_list()
        assert locks == []


class TestOther:
    async def test_query_composition(self):
        SYS = {"id", "revision_id"}

        # Simple fields are initialized using the pydantic model_fields internal property
        # such fields are properly isolated when multi inheritance is involved.
        assert set(get_model_fields(RootDocument).keys()) == SYS | {
            "name",
            "link_root",
        }
        assert set(get_model_fields(ADocument).keys()) == SYS | {
            "name",
            "link_root",
            "surname",
            "link_a",
        }
        assert set(get_model_fields(BDocument).keys()) == SYS | {
            "name",
            "link_root",
            "email",
            "link_b",
        }

        # Where Document.init_fields() has a bug that prevents proper link inheritance when parent
        # documents are initialized. Furthermore, some-why BDocument._link_fields are not deterministic
        assert set(RootDocument._link_fields.keys()) == {"link_root"}
        assert set(ADocument._link_fields.keys()) == {"link_root", "link_a"}
        assert set(BDocument._link_fields.keys()) == {"link_root", "link_b"}

    async def test_with_projection(self):
        await UsersAddresses(region_id=Region()).insert(
            link_rule=WriteRules.WRITE
        )
        res = await UsersAddresses.find_one(fetch_links=True).project(
            AddressView
        )
        assert res.id is not None
        assert res.state == "TEST"
        assert res.city == "TEST"

    async def test_self_linked(self):
        await SelfLinked(item=SelfLinked(s="2"), s="1").insert(
            link_rule=WriteRules.WRITE
        )

        res = await SelfLinked.find_one(fetch_links=True)
        assert isinstance(res, SelfLinked)
        assert res.item is None

        await SelfLinked.delete_all()

        await SelfLinked(
            item=SelfLinked(
                item=SelfLinked(item=SelfLinked(s="4"), s="3"), s="2"
            ),
            s="1",
        ).insert(link_rule=WriteRules.WRITE)

        res = await SelfLinked.find_one(SelfLinked.s == "1", fetch_links=True)
        assert isinstance(res, SelfLinked)
        assert isinstance(res.item, SelfLinked)
        assert isinstance(res.item.item, SelfLinked)
        assert isinstance(res.item.item.item, Link)

    async def test_looped_links(self):
        await LoopedLinksA(
            b=LoopedLinksB(
                a=LoopedLinksA(
                    b=LoopedLinksB(
                        s="4",
                    ),
                    s="3",
                ),
                s="2",
            ),
            s="1",
        ).insert(link_rule=WriteRules.WRITE)
        res = await LoopedLinksA.find_one(
            LoopedLinksA.s == "1", fetch_links=True
        )
        assert isinstance(res, LoopedLinksA)
        assert isinstance(res.b, LoopedLinksB)
        assert isinstance(res.b.a, LoopedLinksA)
        assert isinstance(res.b.a.b, Link)

        await LoopedLinksA(
            b=LoopedLinksB(s="a2"),
            s="a1",
        ).insert(link_rule=WriteRules.WRITE)
        res = await LoopedLinksA.find_one(
            LoopedLinksA.s == "a1", fetch_links=True
        )
        assert isinstance(res, LoopedLinksA)
        assert isinstance(res.b, LoopedLinksB)
        assert res.b.a is None

    async def test_with_chaining_aggregation(self):
        region = Region()
        await region.insert()

        for i in range(10):
            await UsersAddresses(region_id=region).insert()

        region_2 = Region()
        await region_2.insert()

        for i in range(10):
            await UsersAddresses(region_id=region_2).insert()

        addresses_count = (
            await UsersAddresses.find(
                UsersAddresses.region_id.id == region.id, fetch_links=True
            )
            .aggregate([{"$count": "count"}])
            .to_list()
        )

        assert addresses_count[0] == {"count": 10}

    async def test_with_chaining_aggregation_and_text_search(self):
        # ARRANGE
        NUM_DOCS = 10
        NUM_WITH_LOWER = 5
        linked_document = LinkDocumentForTextSeacrh(i=1)
        await linked_document.insert()

        for i in range(NUM_DOCS):
            await DocumentWithTextIndexAndLink(
                s="lower" if i < NUM_WITH_LOWER else "UPPER",
                link=linked_document,
            ).insert()

        linked_document_2 = LinkDocumentForTextSeacrh(i=2)
        await linked_document_2.insert()

        for i in range(NUM_DOCS):
            await DocumentWithTextIndexAndLink(
                s="lower" if i < NUM_WITH_LOWER else "UPPER",
                link=linked_document_2,
            ).insert()

        # ACT
        query = DocumentWithTextIndexAndLink.find(
            {"$text": {"$search": "lower"}},
            DocumentWithTextIndexAndLink.link.i == 1,
            fetch_links=True,
        )

        # Test both aggregation and count methods
        document_count_aggregation = await query.aggregate(
            [{"$count": "count"}]
        ).to_list()
        document_count = await query.count()

        # ASSERT
        assert document_count_aggregation[0] == {"count": NUM_WITH_LOWER}
        assert document_count == NUM_WITH_LOWER

    async def test_with_extra_allow(self, houses):
        res = await House.find(fetch_links=True).to_list()
        assert get_model_fields(res[0]).keys() == {
            "id",
            "revision_id",
            "windows",
            "door",
            "roof",
            "yards",
            "name",
            "height",
        }

        res = await House.find_one(fetch_links=True)
        assert get_model_fields(res).keys() == {
            "id",
            "revision_id",
            "windows",
            "door",
            "roof",
            "yards",
            "name",
            "height",
        }


@pytest.fixture()
async def link_and_backlink_doc_pair():
    back_link_doc = DocumentWithBackLink()
    await back_link_doc.insert()
    link_doc = DocumentWithLink(link=back_link_doc)
    await link_doc.insert()
    return link_doc, back_link_doc


@pytest.fixture()
async def list_link_and_list_backlink_doc_pair():
    back_link_doc = DocumentWithListBackLink()
    await back_link_doc.insert()
    link_doc = DocumentWithListLink(link=[back_link_doc])
    await link_doc.insert()
    return link_doc, back_link_doc


class TestFindBackLinks:
    async def test_prefetch_direct(self, link_and_backlink_doc_pair):
        link_doc, back_link_doc = link_and_backlink_doc_pair
        back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        assert back_link_doc.back_link.id == link_doc.id
        assert back_link_doc.back_link.link.id == back_link_doc.id

    async def test_prefetch_list(self, list_link_and_list_backlink_doc_pair):
        link_doc, back_link_doc = list_link_and_list_backlink_doc_pair
        back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        assert back_link_doc.back_link[0].id == link_doc.id
        assert back_link_doc.back_link[0].link[0].id == back_link_doc.id

    async def test_nesting(self):
        back_link_doc = DocumentWithBackLinkForNesting(i=1)
        await back_link_doc.insert()
        link_doc = DocumentWithLinkForNesting(link=back_link_doc, s="TEST")
        await link_doc.insert()

        doc = await DocumentWithLinkForNesting.get(
            link_doc.id, fetch_links=True
        )
        assert isinstance(doc.link, Link)
        doc.link = await doc.link.fetch()
        assert doc.link.i == 1

        back_link_doc = await DocumentWithBackLinkForNesting.get(
            back_link_doc.id, fetch_links=True
        )
        assert (
            back_link_doc.back_link.link.back_link.link.back_link.id
            == link_doc.id
        )
        assert isinstance(
            back_link_doc.back_link.link.back_link.link.back_link.link, Link
        )


class TestReplaceBackLinks:
    async def test_do_nothing(self, link_and_backlink_doc_pair):
        link_doc, back_link_doc = link_and_backlink_doc_pair
        back_link_doc.back_link.s = "new value"
        await back_link_doc.replace()
        new_back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        assert new_back_link_doc.back_link.s == "TEST"

    async def test_do_nothing_list(self, list_link_and_list_backlink_doc_pair):
        link_doc, back_link_doc = list_link_and_list_backlink_doc_pair
        back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        for lnk in back_link_doc.back_link:
            lnk.s = "new value"
        await back_link_doc.replace()
        new_back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        for lnk in new_back_link_doc.back_link:
            assert lnk.s == "TEST"

    async def test_write(self, link_and_backlink_doc_pair):
        link_doc, back_link_doc = link_and_backlink_doc_pair
        back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        back_link_doc.back_link.s = "new value"
        await back_link_doc.replace(link_rule=WriteRules.WRITE)
        new_back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        assert new_back_link_doc.back_link.s == "new value"

    async def test_do_nothing_write_list(
        self, list_link_and_list_backlink_doc_pair
    ):
        link_doc, back_link_doc = list_link_and_list_backlink_doc_pair
        back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        for lnk in back_link_doc.back_link:
            lnk.s = "new value"
        await back_link_doc.replace(link_rule=WriteRules.WRITE)
        new_back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        for lnk in new_back_link_doc.back_link:
            assert lnk.s == "new value"


class TestSaveBackLinks:
    async def test_do_nothing(self, link_and_backlink_doc_pair):
        link_doc, back_link_doc = link_and_backlink_doc_pair
        back_link_doc.back_link.s = "new value"
        await back_link_doc.save()
        new_back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        assert new_back_link_doc.back_link.s == "TEST"

    async def test_do_nothing_list(self, list_link_and_list_backlink_doc_pair):
        link_doc, back_link_doc = list_link_and_list_backlink_doc_pair
        back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        for lnk in back_link_doc.back_link:
            lnk.s = "new value"
        await back_link_doc.save()
        new_back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        for lnk in new_back_link_doc.back_link:
            assert lnk.s == "TEST"

    async def test_write(self, link_and_backlink_doc_pair):
        link_doc, back_link_doc = link_and_backlink_doc_pair
        back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        back_link_doc.back_link.s = "new value"
        await back_link_doc.save(link_rule=WriteRules.WRITE)
        new_back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        assert new_back_link_doc.back_link.s == "new value"

    async def test_write_list(self, list_link_and_list_backlink_doc_pair):
        link_doc, back_link_doc = list_link_and_list_backlink_doc_pair
        back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        for lnk in back_link_doc.back_link:
            lnk.s = "new value"
        await back_link_doc.save(link_rule=WriteRules.WRITE)
        new_back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        for lnk in new_back_link_doc.back_link:
            assert lnk.s == "new value"


class HouseForReversedOrderInit(Document):
    name: str
    door: Link["DoorForReversedOrderInit"]
    owners: List[Link["PersonForReversedOrderInit"]]


class DoorForReversedOrderInit(Document):
    height: int = 2
    width: int = 1
    if IS_PYDANTIC_V2:
        house: BackLink[HouseForReversedOrderInit] = Field(
            json_schema_extra={"original_field": "door"}
        )
    else:
        house: BackLink[HouseForReversedOrderInit] = Field(
            original_field="door"
        )


class PersonForReversedOrderInit(Document):
    name: str
    if IS_PYDANTIC_V2:
        house: List[BackLink[HouseForReversedOrderInit]] = Field(
            json_schema_extra={"original_field": "owners"}
        )
    else:
        house: List[BackLink[HouseForReversedOrderInit]] = Field(
            original_field="owners"
        )


class TestDeleteBackLinks:
    async def test_do_nothing(self, link_and_backlink_doc_pair):
        link_doc, back_link_doc = link_and_backlink_doc_pair
        back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        await back_link_doc.delete()
        new_link_doc = await DocumentWithLink.get(
            link_doc.id, fetch_links=True
        )
        assert new_link_doc is not None

    async def test_do_nothing_list(self, list_link_and_list_backlink_doc_pair):
        link_doc, back_link_doc = list_link_and_list_backlink_doc_pair
        back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        await back_link_doc.delete()
        new_link_doc = await DocumentWithListLink.get(
            link_doc.id, fetch_links=True
        )
        assert new_link_doc is not None

    async def test_delete_links(self, link_and_backlink_doc_pair):
        link_doc, back_link_doc = link_and_backlink_doc_pair
        back_link_doc = await DocumentWithBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        await back_link_doc.delete(link_rule=DeleteRules.DELETE_LINKS)
        new_link_doc = await DocumentWithLink.get(
            link_doc.id, fetch_links=True
        )
        assert new_link_doc is None

    async def test_delete_links_list(
        self, list_link_and_list_backlink_doc_pair
    ):
        link_doc, back_link_doc = list_link_and_list_backlink_doc_pair
        back_link_doc = await DocumentWithListBackLink.get(
            back_link_doc.id, fetch_links=True
        )
        await back_link_doc.delete(link_rule=DeleteRules.DELETE_LINKS)
        new_link_doc = await DocumentWithListLink.get(
            link_doc.id, fetch_links=True
        )
        assert new_link_doc is None

    async def test_init_reversed_order(self, db):
        await init_beanie(
            database=db,
            document_models=[
                DoorForReversedOrderInit,
                HouseForReversedOrderInit,
                PersonForReversedOrderInit,
            ],
        )


class TestBuildAggregations:
    async def test_find_aggregate_without_fetch_links(self, houses):
        door = await Door.find_one()
        aggregation = House.find(House.door.id == door.id).aggregate(
            [
                {"$group": {"_id": "$height", "count": {"$sum": 1}}},
            ]
        )
        assert aggregation.get_aggregation_pipeline() == [
            {"$match": {"door.$id": door.id}},
            {"$group": {"_id": "$height", "count": {"$sum": 1}}},
        ]
        result = await aggregation.to_list()
        assert result == [{"_id": 0, "count": 1}]

    async def test_find_aggregate_with_fetch_links(self, houses):
        door = await Door.find_one()
        aggregation = House.find(
            House.door.id == door.id, fetch_links=True
        ).aggregate(
            [
                {"$group": {"_id": "$height", "count": {"$sum": 1}}},
            ]
        )
        assert len(aggregation.get_aggregation_pipeline()) == 12
        assert aggregation.get_aggregation_pipeline()[10:] == [
            {"$match": {"door._id": door.id}},
            {"$group": {"_id": "$height", "count": {"$sum": 1}}},
        ]
        result = await aggregation.to_list()
        assert result == [{"_id": 0, "count": 1}]
