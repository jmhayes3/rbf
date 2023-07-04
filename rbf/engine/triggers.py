"""
This module contains a collection of Trigger classes to be used by bot modules.
"""

import json
import re

from typing import List


class Trigger:
    """Trigger base class."""


class Contains(Trigger):
    def __init__(self, values: List[str], fields: List[str], case=False):
        self.values= values

        if not case:
            self.values = [value.lower() for value in self.values]

        self.fields = fields or ["body"]
        self.case = case

    def process(self, data):
        for field in self.fields:
            if field in data:
                text = data[field]
                if not self.case:
                    text = text.lower()
                for value in self.values:
                    if value in text:
                        return value

    def to_dict(self):
        return {
            "type": "contains",
            "fields": self.fields,
            "values": self.values,
            "case": self.case,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class Regex(Trigger):
    def __init__(self, regex: str, fields: List[str], case=False):
        self.regex = regex
        self.fields = fields or ["body"]
        self.case = case

        self.compile()

    def compile(self):
        if self.case:
            self.pattern = re.compile(self.regex)
        else:
            self.pattern = re.compile(self.regex, re.IGNORECASE)

    def process(self, data):
        for field in self.fields:
            if field in data:
                text = data[field]
                result = self.pattern.search(text)
                return result

    def to_dict(self):
        return {"regex": self.regex, "fields": self.fields, "case": self.case}

    def to_json(self):
        return json.dumps(self.to_dict())


class Keyword(Trigger):
    regex_template = "(?<![a-zA-Z0-9])({})(?![a-zA-Z0-9])"

    def __init__(self, keywords: List[str], fields: List[str], case=False):
        self.keywords = keywords
        self.fields = fields or ["body"]
        self.case = case

        self.compile()

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
                result = self.pattern.search(text)
                if result:
                    return result.group(0)

    def to_dict(self):
        return {
            "type": "keyword",
            "fields": self.fields,
            "keywords": self.keywords,
            "case": self.case,
        }

    def to_json(self):
        return json.dumps(obj=self.to_dict())


class Domain(Trigger):
    def __init__(self, domain: str, field: str):
        self.domain = domain
        self.field = field

    def process(self, data):
        """
        if data["url"] != data["permalink"]:
            process
        """
        pass

    def to_dict(self):
        return {"domain": self.domain, "field": self.field}

    def to_json(self):
        return json.dumps(obj=self.to_dict())


class NSFW(Trigger):
    def __init__(self, nsfw: bool, field: str):
        self.nsfw = nsfw
        self.field = field

    def process(self, data):
        if self.field in data:
            nsfw = data[self.field]
            if nsfw == self.nsfw:
                return True
        return False

    def to_dict(self):
        return {"nsfw": self.nsfw, "field": self.field}

    def to_json(self):
        return json.dumps(obj=self.to_dict())
