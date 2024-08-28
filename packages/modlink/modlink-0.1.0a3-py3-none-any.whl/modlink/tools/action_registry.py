import json
from typing import Dict, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from modlink.action import Action


class ActionRegistry:
    def __init__(self):
        self.action_map: Dict[str, Type["Action"]] = {}

    def add(self, action: Type["Action"]):
        self.action_map[action.name()] = action

    def add_all(self, *actions: Type["Action"]):
        for action in actions:
            self.add(action)

    def remove(self, action: Type["Action"]):
        del self.action_map[action.name()]

    def schemas(self) -> List[Dict]:
        return [action.action_schema() for action in self.action_map.values()]

    def from_dict(self, value: Dict) -> "Action":
        name = value.get("action")
        action_class = self.action_map.get(name)
        return action_class.model_validate(value)

    def from_json(self, value: str) -> "Action":
        data: Dict = json.loads(value)
        return self.from_dict(data)

    def validate(self, action: "Action"):
        name = action.name()
        if name not in self.action_map:
            raise ValueError(f"Unsupported action: {name}")
