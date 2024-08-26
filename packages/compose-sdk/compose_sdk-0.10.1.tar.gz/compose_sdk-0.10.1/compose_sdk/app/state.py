from typing import Dict, Any, TYPE_CHECKING

dict_key = str
dict_value = Any

if TYPE_CHECKING:
    from .appRunner import AppRunner


class State:
    def __init__(self, appRunner: "AppRunner"):
        self._state = {}
        self.appRunner = appRunner

    def __onStateUpdate(self):
        self.appRunner.scheduler.create_task(self.appRunner.on_state_update())

    def __getitem__(self, key: dict_key) -> dict_value:
        return self._state[key]

    def __setitem__(self, key: dict_key, value: dict_value):
        self._state[key] = value
        self.__onStateUpdate()

    def overwrite(self, new_state: Dict[dict_key, dict_value]):
        self._state = new_state
        self.__onStateUpdate()

    def merge(self, new_state: Dict[dict_key, dict_value]):
        self._state.update(new_state)
        self.__onStateUpdate()

    def __repr__(self):
        return repr(self._state)
