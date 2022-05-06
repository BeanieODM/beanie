from typing import (
    Optional,
    List,
    Type,
    Union,
    Tuple,
    Mapping,
    Any,
    overload,
    ClassVar,
    TypeVar,
)

from pydantic import (
    BaseModel,
)
from pymongo.client_session import ClientSession

from beanie.odm.enums import SortDirection
from beanie.odm.queries.find import FindOne, FindMany
from beanie.odm.settings.base import ItemSettings

DocType = TypeVar("DocType", bound="FindInterface")
DocumentProjectionType = TypeVar("DocumentProjectionType", bound=BaseModel)


class FindInterface:
    # Customization
    # Query builders could be replaced in the inherited classes
    _find_one_query_class: ClassVar[Type] = FindOne
    _find_many_query_class: ClassVar[Type] = FindMany

    @classmethod
    def get_settings(cls) -> ItemSettings:
        pass

    @overload
    @classmethod
    def find_one(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> FindOne["DocType"]:
        ...

    @overload
    @classmethod
    def find_one(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type["DocumentProjectionType"],
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> FindOne["DocumentProjectionType"]:
        ...

    @classmethod
    def find_one(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type["DocumentProjectionType"]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> Union[FindOne["DocType"], FindOne["DocumentProjectionType"]]:
        """
        Find one document by criteria.
        Returns [FindOne](https://roman-right.github.io/beanie/api/queries/#findone) query object.
        When awaited this will either return a document or None if no document exists for the search criteria.

        :param args: *Mapping[str, Any] - search criteria
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session instance
        :param ignore_cache: bool
        :param **pymongo_kwargs: pymongo native parameters for find operation (if Document class contains links, this parameter must fit the respective parameter of the aggregate MongoDB function)
        :return: [FindOne](https://roman-right.github.io/beanie/api/queries/#findone) - find query instance
        """
        args = cls._add_class_id_filter(args)
        return cls._find_one_query_class(document_model=cls).find_one(
            *args,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
            **pymongo_kwargs,
        )

    @overload
    @classmethod
    def find_many(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> FindMany["DocType"]:
        ...

    @overload
    @classmethod
    def find_many(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type["DocumentProjectionType"] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> FindMany["DocumentProjectionType"]:
        ...

    @classmethod
    def find_many(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type["DocumentProjectionType"]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> Union[FindMany["DocType"], FindMany["DocumentProjectionType"]]:
        """
        Find many documents by criteria.
        Returns [FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) query object

        :param args: *Mapping[str, Any] - search criteria
        :param skip: Optional[int] - The number of documents to omit.
        :param limit: Optional[int] - The maximum number of results to return.
        :param sort: Union[None, str, List[Tuple[str, SortDirection]]] - A key or a list of (key, direction) pairs specifying the sort order for this query.
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session
        :param ignore_cache: bool
        :param **pymongo_kwargs: pymongo native parameters for find operation (if Document class contains links, this parameter must fit the respective parameter of the aggregate MongoDB function)
        :return: [FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) - query instance
        """
        args = cls._add_class_id_filter(args)
        return cls._find_many_query_class(document_model=cls).find_many(
            *args,
            sort=sort,
            skip=skip,
            limit=limit,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
            **pymongo_kwargs,
        )

    @overload
    @classmethod
    def find(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> FindMany["DocType"]:
        ...

    @overload
    @classmethod
    def find(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Type["DocumentProjectionType"],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> FindMany["DocumentProjectionType"]:
        ...

    @classmethod
    def find(
        cls: Type["DocType"],
        *args: Union[Mapping[str, Any], bool],
        projection_model: Optional[Type["DocumentProjectionType"]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        fetch_links: bool = False,
        **pymongo_kwargs,
    ) -> Union[FindMany["DocType"], FindMany["DocumentProjectionType"]]:
        """
        The same as find_many
        """
        return cls.find_many(
            *args,
            skip=skip,
            limit=limit,
            sort=sort,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            fetch_links=fetch_links,
            **pymongo_kwargs,
        )

    @overload
    @classmethod
    def find_all(
        cls: Type["DocType"],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        projection_model: None = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
    ) -> FindMany["DocType"]:
        ...

    @overload
    @classmethod
    def find_all(
        cls: Type["DocType"],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        projection_model: Optional[Type["DocumentProjectionType"]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
    ) -> FindMany["DocumentProjectionType"]:
        ...

    @classmethod
    def find_all(
        cls: Type["DocType"],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        projection_model: Optional[Type["DocumentProjectionType"]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
    ) -> Union[FindMany["DocType"], FindMany["DocumentProjectionType"]]:
        """
        Get all the documents

        :param skip: Optional[int] - The number of documents to omit.
        :param limit: Optional[int] - The maximum number of results to return.
        :param sort: Union[None, str, List[Tuple[str, SortDirection]]] - A key or a list of (key, direction) pairs specifying the sort order for this query.
        :param projection_model: Optional[Type[BaseModel]] - projection model
        :param session: Optional[ClientSession] - pymongo session
        :param **pymongo_kwargs: pymongo native parameters for find operation (if Document class contains links, this parameter must fit the respective parameter of the aggregate MongoDB function)
        :return: [FindMany](https://roman-right.github.io/beanie/api/queries/#findmany) - query instance
        """
        return cls.find_many(
            {},
            skip=skip,
            limit=limit,
            sort=sort,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            **pymongo_kwargs,
        )

    @overload
    @classmethod
    def all(
        cls: Type["DocType"],
        projection_model: None = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
    ) -> FindMany["DocType"]:
        ...

    @overload
    @classmethod
    def all(
        cls: Type["DocType"],
        projection_model: Type["DocumentProjectionType"],
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
    ) -> FindMany["DocumentProjectionType"]:
        ...

    @classmethod
    def all(
        cls: Type["DocType"],
        projection_model: Optional[Type["DocumentProjectionType"]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Union[None, str, List[Tuple[str, SortDirection]]] = None,
        session: Optional[ClientSession] = None,
        ignore_cache: bool = False,
        **pymongo_kwargs,
    ) -> Union[FindMany["DocType"], FindMany["DocumentProjectionType"]]:
        """
        the same as find_all
        """
        return cls.find_all(
            skip=skip,
            limit=limit,
            sort=sort,
            projection_model=projection_model,
            session=session,
            ignore_cache=ignore_cache,
            **pymongo_kwargs,
        )

    @classmethod
    async def count(cls) -> int:
        """
        Number of documents in the collections
        The same as find_all().count()

        :return: int
        """
        return await cls.find_all().count()

    @classmethod
    def _add_class_id_filter(cls, args: Tuple):
        if cls.get_settings().union_doc:
            args += ({"_class_id": cls.__name__},)
        return args
