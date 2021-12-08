import asyncio
import inspect
from enum import Enum
from functools import wraps
from typing import Callable, List, Union, Dict, TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from beanie.odm.documents import Document


class EventTypes(str, Enum):
    INSERT = "INSERT"
    REPLACE = "REPLACE"
    SAVE_CHANGES = "SAVE_CHANGES"
    VALIDATE_ON_SAVE = "VALIDATE_ON_SAVE"


Insert = EventTypes.INSERT
Replace = EventTypes.REPLACE
SaveChanges = EventTypes.SAVE_CHANGES
ValidateOnSave = EventTypes.VALIDATE_ON_SAVE


class ActionDirections(str, Enum):  # TODO think about this name
    BEFORE = "BEFORE"
    AFTER = "AFTER"


class ActionRegistry:
    _actions: Dict[Type, Any] = {}

    # TODO the real type is
    #  Dict[str, Dict[EventTypes,Dict[ActionDirections: List[Callable]]]]
    #  But mypy says it has syntax error inside. Fix it.

    @classmethod
    def clean_actions(cls, document_class: Type):
        if not cls._actions.get(document_class) is None:
            del cls._actions[document_class]

    @classmethod
    def add_action(
        cls,
        document_class: Type,
        event_types: List[EventTypes],
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
        document_class: Type,
        event_type: EventTypes,
        action_direction: ActionDirections,
    ) -> List[Callable]:
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
    ):
        """
        Run actions
        :param instance: Document - object of the Document subclass
        :param event_type: EventTypes - event types
        :param action_direction: ActionDirections - before or after
        """
        document_class = instance.__class__
        actions_list = cls.get_action_list(
            document_class, event_type, action_direction
        )
        coros = []
        for action in actions_list:
            if inspect.iscoroutinefunction(action):
                coros.append(action(instance))
            elif inspect.isfunction(action):
                action(instance)
        await asyncio.gather(*coros)


def register_action(
    event_types: Union[List[EventTypes], EventTypes],
    action_direction: ActionDirections,
):
    """
    Decorator. Base registration method.
    Used inside `before_event` and `after_event`
    :param event_types: Union[List[EventTypes], EventTypes] - event types
    :param action_direction: ActionDirections - before or after
    :return:
    """
    if isinstance(event_types, EventTypes):
        event_types = [event_types]

    def decorator(f):
        f.has_action = True
        f.event_types = event_types
        f.action_direction = action_direction
        return f

    return decorator


def before_event(event_types: Union[List[EventTypes], EventTypes]):
    """
    Decorator. It adds action, which should run before mentioned one
    or many events happen

    :param event_types: Union[List[EventTypes], EventTypes] - event types
    :return: None
    """
    return register_action(
        action_direction=ActionDirections.BEFORE, event_types=event_types
    )


def after_event(event_types: Union[List[EventTypes], EventTypes]):
    """
    Decorator. It adds action, which should run after mentioned one
    or many events happen

    :param event_types: Union[List[EventTypes], EventTypes] - event types
    :return: None
    """
    return register_action(
        action_direction=ActionDirections.AFTER, event_types=event_types
    )


def wrap_with_actions(event_type: EventTypes):
    """
    Helper function to wrap Document methods with
    before and after event listeners
    :param event_type: EventTypes - event types
    :return: None
    """

    def decorator(f: Callable):
        @wraps(f)
        async def wrapper(self, *args, **kwargs):
            await ActionRegistry.run_actions(
                self,
                event_type=event_type,
                action_direction=ActionDirections.BEFORE,
            )

            result = await f(self, *args, **kwargs)

            await ActionRegistry.run_actions(
                self,
                event_type=event_type,
                action_direction=ActionDirections.AFTER,
            )

            return result

        return wrapper

    return decorator
