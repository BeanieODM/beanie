from typing import ForwardRef, Union

from pydantic import BaseModel


class DocsRegistry:
    _registry: dict[str, type[BaseModel]] = {}

    @classmethod
    def register(cls, name: str, doc_type: type[BaseModel]):
        cls._registry[name] = doc_type

    @classmethod
    def get(cls, name: str) -> type[BaseModel]:
        return cls._registry[name]

    @classmethod
    def evaluate_fr(cls, forward_ref: Union[ForwardRef, type]):
        """
        Evaluate forward ref

        :param forward_ref: ForwardRef - forward ref to evaluate
        :return: type[BaseModel] - class of the forward ref
        """
        if (
            isinstance(forward_ref, ForwardRef)
            and forward_ref.__forward_arg__ in cls._registry
        ):
            return cls._registry[forward_ref.__forward_arg__]
        else:
            return forward_ref
