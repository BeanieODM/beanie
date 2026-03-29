import asyncio
import inspect
from collections.abc import Callable
from enum import Enum
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from beanie.odm.documents import AsyncDocMethod, Document

P = ParamSpec("P")
R = TypeVar("R")


class EventTypes(str, Enum):
    """Enumeration of document lifecycle events that can trigger actions.

    Use these values (or their module-level aliases) with
    :func:`before_event` and :func:`after_event` decorators to attach
    hooks to specific operations on a :class:`~beanie.Document`.

    Aliases defined at module level for convenience:
    ``Insert``, ``Replace``, ``Save``, ``SaveChanges``,
    ``ValidateOnSave``, ``Delete``, ``Update``.

    Example::

        class Article(Document):
            title: str
            slug: str

            @before_event(Insert)
            def generate_slug(self):
                self.slug = self.title.lower().replace(" ", "-")

            @after_event(Delete)
            async def notify_deleted(self):
                await send_notification(f"{self.title} was deleted")
    """

    INSERT = "INSERT"
    REPLACE = "REPLACE"
    SAVE = "SAVE"
    SAVE_CHANGES = "SAVE_CHANGES"
    VALIDATE_ON_SAVE = "VALIDATE_ON_SAVE"
    DELETE = "DELETE"
    UPDATE = "UPDATE"


Insert = EventTypes.INSERT
Replace = EventTypes.REPLACE
Save = EventTypes.SAVE
SaveChanges = EventTypes.SAVE_CHANGES
ValidateOnSave = EventTypes.VALIDATE_ON_SAVE
Delete = EventTypes.DELETE
Update = EventTypes.UPDATE


class ActionDirections(str, Enum):  # TODO think about this name
    """Whether an action runs before or after the triggering event.

    Module-level aliases ``Before`` and ``After`` are provided for
    convenience and are the values typically passed to
    :func:`before_event` / :func:`after_event`.
    """

    BEFORE = "BEFORE"
    AFTER = "AFTER"


Before = ActionDirections.BEFORE
After = ActionDirections.AFTER


class ActionRegistry:
    _actions: dict[
        type["Document"],
        dict[EventTypes, dict[ActionDirections, list[Callable[..., Any]]]],
    ] = {}

    @classmethod
    def clean_actions(cls, document_class: type["Document"]):
        if cls._actions.get(document_class) is not None:
            del cls._actions[document_class]

    @classmethod
    def add_action(
        cls,
        document_class: type["Document"],
        event_types: list[EventTypes],
        action_direction: ActionDirections,
        funct: Callable,
    ):
        """
        Add action to the action registry
        :param document_class: document class
        :param event_types: List[EventTypes]
        :param action_direction: ActionDirections - before or after
        :param funct: Callable - function
        """
        if cls._actions.get(document_class) is None:
            cls._actions[document_class] = {
                action_type: {
                    action_direction: []
                    for action_direction in ActionDirections
                }
                for action_type in EventTypes
            }
        for event_type in event_types:
            cls._actions[document_class][event_type][action_direction].append(
                funct
            )

    @classmethod
    def get_action_list(
        cls,
        document_class: type["Document"],
        event_type: EventTypes,
        action_direction: ActionDirections,
    ) -> list[Callable]:
        """
        Get stored action list
        :param document_class: Type - document class
        :param event_type: EventTypes - type of needed event
        :param action_direction: ActionDirections - before or after
        :return: List[Callable] - list of stored methods
        """
        if document_class not in cls._actions:
            return []
        return cls._actions[document_class][event_type][action_direction]

    @classmethod
    async def run_actions(
        cls,
        instance: "Document",
        event_type: EventTypes,
        action_direction: ActionDirections,
        exclude: list[ActionDirections | str],
    ):
        """
        Run actions
        :param instance: Document - object of the Document subclass
        :param event_type: EventTypes - event types
        :param action_direction: ActionDirections - before or after
        """
        if action_direction in exclude:
            return

        document_class = instance.__class__
        actions_list = cls.get_action_list(
            document_class, event_type, action_direction
        )
        coros = []
        for action in actions_list:
            if action.__name__ in exclude:
                continue

            if inspect.iscoroutinefunction(action):
                coros.append(action(instance))
            elif inspect.isfunction(action):
                action(instance)
        await asyncio.gather(*coros)


# `Any` because there is arbitrary attribute assignment on this type
F = TypeVar("F", bound=Any)


def register_action(
    event_types: tuple[list[EventTypes] | EventTypes, ...],
    action_direction: ActionDirections,
) -> Callable[[F], F]:
    """
    Decorator. Base registration method.
    Used inside `before_event` and `after_event`
    :param event_types: Union[List[EventTypes], EventTypes] - event types
    :param action_direction: ActionDirections - before or after
    :return:
    """
    final_event_types = []
    for event_type in event_types:
        if isinstance(event_type, list):
            final_event_types.extend(event_type)
        else:
            final_event_types.append(event_type)

    def decorator(f: F) -> F:
        f.has_action = True
        f.event_types = final_event_types
        f.action_direction = action_direction
        return f

    return decorator


def before_event(
    *args: list[EventTypes] | EventTypes,
) -> Callable[[F], F]:
    """
    Decorator. It adds action, which should run before mentioned one
    or many events happen

    :param args: Union[List[EventTypes], EventTypes] - event types
    :return: None
    """
    return register_action(
        action_direction=ActionDirections.BEFORE, event_types=args
    )


def after_event(
    *args: list[EventTypes] | EventTypes,
) -> Callable[[F], F]:
    """
    Decorator. It adds action, which should run after mentioned one
    or many events happen

    :param args: Union[List[EventTypes], EventTypes] - event types
    :return: None
    """

    return register_action(
        action_direction=ActionDirections.AFTER, event_types=args
    )


def wrap_with_actions(
    event_type: EventTypes,
) -> Callable[["AsyncDocMethod[P, R]"], "AsyncDocMethod[P, R]"]:
    """
    Helper function to wrap Document methods with
    before and after event listeners
    :param event_type: EventTypes - event types
    :return: None
    """

    def decorator(
        f: "AsyncDocMethod[P, R]",
    ) -> "AsyncDocMethod[P, R]":
        @wraps(f)
        async def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> R:
            skip_actions: list[ActionDirections | str] = (
                kwargs.get("skip_actions") or []  # type: ignore[assignment]
            )

            self = cast("Document", args[0])

            await ActionRegistry.run_actions(
                self,
                event_type=event_type,
                action_direction=ActionDirections.BEFORE,
                exclude=skip_actions,
            )

            result = await f(*args, **kwargs)

            await ActionRegistry.run_actions(
                self,
                event_type=event_type,
                action_direction=ActionDirections.AFTER,
                exclude=skip_actions,
            )

            return result

        return wrapper

    return decorator
