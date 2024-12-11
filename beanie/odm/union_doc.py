from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from motor.motor_asyncio import AsyncIOMotorClientSession

from beanie.exceptions import UnionDocNotInited
from beanie.odm.bulk import BulkWriter
from beanie.odm.interfaces.aggregate import AggregateInterface
from beanie.odm.interfaces.detector import DetectionInterface, ModelType
from beanie.odm.interfaces.find import FindInterface
from beanie.odm.interfaces.getters import OtherGettersInterface
from beanie.odm.settings.union_doc import UnionDocSettings

UnionDocType = TypeVar("UnionDocType", bound="UnionDoc")


class UnionDoc(
    FindInterface,
    AggregateInterface,
    OtherGettersInterface,
    DetectionInterface,
):
    _document_models: ClassVar[Optional[Dict[str, Type]]] = None
    _is_inited: ClassVar[bool] = False
    _settings: ClassVar[UnionDocSettings]

    @classmethod
    def get_settings(cls) -> UnionDocSettings:
        return cls._settings

    @classmethod
    def register_doc(cls, name: str, doc_model: Type):
        if cls._document_models is None:
            cls._document_models = {}

        if cls._is_inited is False:
            raise UnionDocNotInited

        cls._document_models[name] = doc_model
        return cls.get_settings().name

    @classmethod
    def get_model_type(cls) -> ModelType:
        return ModelType.UnionDoc

    def bulk_writer(
        self,
        session: Optional[AsyncIOMotorClientSession] = None,
        ordered: bool = True,
        bypass_document_validation: bool = False,
        comment: Optional[Any] = None,
    ):
        """
        Returns a BulkWriter instance for handling bulk write operations.

        Parameters:
        -----------
        :param session: ClientSession
            The session instance used for transactional operations.
        :param ordered: If ``True`` (the default) requests will be
            performed on the server serially, in the order provided. If an error
            occurs all remaining operations are aborted. If ``False`` requests
            will be performed on the server in arbitrary order, possibly in
            parallel, and all operations will be attempted.
        :param bypass_document_validation: (optional) If ``True``, allows the
            write to opt-out of document level validation. Default is
            ``False``.
        :param comment: A user-provided comment to attach to the BulkWriter

        Returns:
        --------
        BulkWriter
            An instance of BulkWriter configured with the provided settings.
        """
        return BulkWriter(
            session, ordered, bypass_document_validation, comment
        )
