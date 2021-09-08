import asyncio
import inspect
from enum import Enum
from functools import wraps
from typing import Callable, List, Union, Dict, TYPE_CHECKING, Any

from beanie.odm.utils.class_path import (
    get_class_path_for_method,
    get_class_path_for_object,
)

if TYPE_CHECKING:
    from beanie.odm.documents import Document


class EventTypes(str, Enum):
    INSERT = "INSERT"
    REPLACE = "REPLACE"


class ActionDirections(str, Enum):  # TODO think about this name
    BEFORE = "BEFORE"
    AFTER = "AFTER"


class ActionRegistry:
    _actions: Dict[str, Any] = {}
    # TODO the real type is
    #  Dict[str, Dict[EventTypes,Dict[ActionDirections: List[Callable]]]]
    #  But mypy says it has syntax error inside. Fix it.

    @classmethod
    def add_action(
        cls,
        event_types: List[EventTypes],
        action_direction: ActionDirections,
        funct: Callable,
    ):
        class_path = get_class_path_for_method(funct)
        if cls._actions.get(class_path) is None:
            cls._actions[class_path] = {
                action_type: {
                    action_direction: []
                    for action_direction in ActionDirections
                }
                for action_type in EventTypes
            }
        for event_type in event_types:
            cls._actions[class_path][event_type][action_direction].append(
                funct
            )

    @classmethod
    def get_action_list(
        cls,
        class_path: str,
        event_types: EventTypes,
        action_direction: ActionDirections,
    ) -> List[Callable]:
        if class_path not in cls._actions:
            return []
        return cls._actions[class_path][event_types][action_direction]

    @classmethod
    async def run_actions(
        cls,
        instance: "Document",
        event_type: EventTypes,
        action_direction: ActionDirections,
    ):
        class_path = get_class_path_for_object(instance)
        actions_list = cls.get_action_list(
            class_path, event_type, action_direction
        )
        coros = []
        for action in actions_list:
            if inspect.iscoroutinefunction(action):
                coros.append(action(instance))
            elif inspect.isfunction(action):
                action(instance)
        await asyncio.gather(*coros)


def register_action(
    action_direction: ActionDirections,
    event_types: Union[List[EventTypes], EventTypes],
):
    if isinstance(event_types, EventTypes):
        event_types = [event_types]

    def decorator(f):
        ActionRegistry.add_action(
            event_types=event_types, action_direction=action_direction, funct=f
        )

    return decorator


def before_event(event_types: Union[List[EventTypes], EventTypes]):
    return register_action(
        action_direction=ActionDirections.BEFORE, event_types=event_types
    )


def after_event(event_types: Union[List[EventTypes], EventTypes]):
    return register_action(
        action_direction=ActionDirections.AFTER, event_types=event_types
    )


def wrap_with_actions(event_type: EventTypes):
    def decorator(f: Callable):
        @wraps
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
