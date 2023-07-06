from rbf.engine.triggers import Trigger, Contains, Keyword, Regex


def test_trigger_class(trigger=Trigger):
    assert issubclass(trigger, object)


def test_contains_trigger():
    data = {
        "title": "A good ol' fashioned Old Fashioned",
    }
    values = ["A", "good", "ol'", "fashioned", "Old", "Fashioned"]
    component = Contains(values, fields=["title"])
    result = component.process(data)
    assert result == "a"
    component.require_all = True
    result = component.process(data)
    component.values = ["not", "present"]
    result = component.process(data)
    assert result is None
    component.fields = ["body"]
    result = component.process(data)
    assert result is None


def test_keyword_trigger():
    data = {
        "body": "A good ol' fashioned Old Fashioned",
    }
    keywords = ["good", "fashioned"]
    component = Keyword(keywords, fields=["body"])
    result = component.process(data)
    assert result == "good"


def test_regex_trigger():
    pass