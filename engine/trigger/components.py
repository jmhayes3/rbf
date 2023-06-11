import json
import re
from typing import Any


class Component:
    pass


class Contains(Component):
    def __init__(self, values, field, require_all=False, case=True) -> None:
        if not case:
            self.values = [value.lower() for value in values]
        else:
            self.values: Any = values

        self.field: Any = field
        self.require_all: bool = require_all
        self.case: bool = case

        self.validate()

    def validate(self) -> None:
        if not isinstance(self.values, list):
            raise TypeError
        for value in self.values:
            if not isinstance(value, str):
                raise TypeError
        if not isinstance(self.field, str):
            raise TypeError

    def process(self, data):
        if self.field in data:
            text = data[self.field]
            if not self.case:
                text = text.lower()
            matches = []
            for value in self.values:
                if value in text:
                    if not self.require_all:
                        return value
                    matches.append(value)
            if len(matches) == len(self.values):
                return matches
            return None

    def to_dict(self):
        return {
            "type": "contains",
            "field": self.field,
            "values": self.values,
            "require_all": self.require_all,
            "case": self.case,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class Regex(Component):
    def __init__(self, regex, field, case=True):
        self.regex = regex
        self.field = field
        self.case = case

        self.validate()
        self.compile()

    def validate(self):
        if not isinstance(self.regex, str):
            raise TypeError
        if not isinstance(self.field, str):
            raise TypeError

    def compile(self):
        if self.case:
            self.pattern = re.compile(self.regex)
        else:
            self.pattern = re.compile(self.regex, re.IGNORECASE)

    def process(self, data):
        if self.field in data:
            data = data[self.field]
            result = self.pattern.search(data)
            return result

    def to_dict(self):
        return {"regex": self.regex, "field": self.field, "case": self.case}

    def to_json(self):
        return json.dumps(self.to_dict())


class Keyword(Component):
    regex_template = "(?<![a-zA-Z0-9])({})(?![a-zA-Z0-9])"

    def __init__(self, keywords, fields, require_all=False, case=True):
        self.keywords = keywords
        self.fields = fields
        self.require_all = require_all
        self.case = case

        self.validate()
        self.compile()

    def validate(self):
        if not isinstance(self.keywords, list):
            raise TypeError
        for keyword in self.keywords:
            if not isinstance(keyword, str):
                raise TypeError
        if not isinstance(self.fields, list):
            raise TypeError

    def compile(self):
        keywords_as_regex = "|".join(self.keywords)
        if self.case:
            self.pattern = re.compile(
                Keyword.regex_template.format(keywords_as_regex),
            )
        else:
            self.pattern = re.compile(
                Keyword.regex_template.format(keywords_as_regex), re.IGNORECASE
            )

    def process(self, data):
        for field in self.fields:
            if field in data:
                text = data[field]
                if self.require_all:
                    result = self.pattern.findall(text)
                    result = [kw if kw in result else None for kw in self.keywords]
                    if all(result):
                        return result
                    else:
                        return None
                else:
                    result = self.pattern.search(text)
                    if result:
                        return result.group(0)

    def to_dict(self):
        return {
            "type": "keyword",
            "fields": self.fields,
            "keywords": self.keywords,
            "require_all": self.require_all,
            "case": self.case,
        }

    def to_json(self) -> str:
        return json.dumps(obj=self.to_dict())


class Domain(Component):
    def __init__(self, domain, field) -> None:
        self.domain: Any = domain
        self.field: Any = field

    def validate(self) -> None:
        pass

    def process(self, data) -> None:
        """
        if data["url"] != data["permalink"]:
            process
        """
        pass

    def to_dict(self) -> dict[str, Any]:
        return {"domain": self.domain, "field": self.field}

    def to_json(self) -> str:
        return json.dumps(obj=self.to_dict())


class NSFW(Component):
    def __init__(self, nsfw, field) -> None:
        self.nsfw: Any = nsfw
        self.field: Any = field

        self.validate()

    def validate(self) -> None:
        if not isinstance(self.nsfw, bool):
            raise TypeError
        if not isinstance(self.field, str):
            raise TypeError

    def process(self, data) -> bool | None:
        if self.field in data:
            nsfw = data[self.field]
            if nsfw == self.nsfw:
                return True
            return False

    def to_dict(self) -> dict[str, Any]:
        return {"nsfw": self.nsfw, "field": self.field}

    def to_json(self) -> str:
        return json.dumps(obj=self.to_dict())
