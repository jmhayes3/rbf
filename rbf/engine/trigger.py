import json

from .components import (
    Component, Keyword
)


def create_trigger(data):
    stream = data.get("stream")
    targets = data.get("targets")

    components = []
    if "components" in data:
        for component in data["components"]:
            if component["type"] == "keyword":
                keyword_component = Keyword(
                    component["keywords"],
                    component["fields"],
                    component["require_all"],
                    component["case"]
                )
                components.append(keyword_component)

    return Trigger(stream, targets, components)


class Trigger:

    def __init__(self, stream, targets, components):
        self.stream = stream
        self.targets = targets
        self.components = components

        self.validate()

    def validate(self):
        if not isinstance(self.stream, str):
            raise TypeError
        if not isinstance(self.components, list):
            raise TypeError
        for component in self.components:
            if not isinstance(component, Component):
                raise TypeError

    def add_target(self, target):
        if isinstance(target, str):
            self.targets.append(target)

    def add_component(self, component):
        if isinstance(component, Component):
            self.components.append(component)

    def check_components(self, data):
        if self.components:
            for component in self.components:
                result = component.process(data)
                if not result:
                    return False
        return True

    def to_dict(self):
        return {
            "stream": self.stream,
            "targets": self.targets,
            "components": [c.to_dict() for c in self.components]
        }

    def to_json(self):
        return json.dumps(self.to_dict())
