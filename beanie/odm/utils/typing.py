from typing import List, Optional, get_origin, get_args, NamedTuple, Type, _GenericAlias, ForwardRef

from pydantic import validator, field_validator

from beanie.odm.fields import Link, BackLink


def evaluate_forward_ref(t: ForwardRef) -> Type:
    return t._evaluate(globals(), locals(), set())


class AnnotationType(NamedTuple):
    is_optional: bool
    is_list: bool
    base_class: Type
    generic_type: Type

    @classmethod
    def set(cls,
            is_optional: bool,
            is_list: bool,
            base_class: Type,
            generic_type: Type,
            ):
        if isinstance(generic_type, ForwardRef):
            generic_type = evaluate_forward_ref(generic_type)
        return cls(
            is_optional=is_optional,
            is_list=is_list,
            base_class=base_class,
            generic_type=generic_type
        )


def get_annotation_type(annotation):
    origin = get_origin(annotation)
    args = get_args(annotation)

    classes = [Link, BackLink]

    for cls in classes:
        # Check if annotation is one of the custom classes
        if isinstance(annotation, _GenericAlias) and annotation.__origin__ is cls:
            return AnnotationType.set(is_optional=False, is_list=False, base_class=cls,
                                  generic_type=args[0])

        # Check if annotation is List[custom class]
        elif origin is List and len(args) == 1 and isinstance(args[0], _GenericAlias) and args[0].__origin__ is cls:
            return AnnotationType.set(is_optional=False, is_list=True, base_class=cls,
                                  generic_type=get_args(args[0])[0])

        # Check if annotation is Optional[custom class] or Optional[List[custom class]]
        elif origin is Optional and len(args) == 1:
            optional_origin = get_origin(args[0])
            optional_args = get_args(args[0])

            if isinstance(args[0], _GenericAlias) and args[0].__origin__ is cls:
                return AnnotationType.set(is_optional=True, is_list=False, base_class=cls,
                                      generic_type=optional_args[0])

            elif optional_origin is List and len(optional_args) == 1 and isinstance(optional_args[0], _GenericAlias) and \
                    optional_args[0].__origin__ is cls:
                return AnnotationType.set(is_optional=True, is_list=True, base_class=cls,
                                      generic_type=get_args(optional_args[0])[0])

    return None
