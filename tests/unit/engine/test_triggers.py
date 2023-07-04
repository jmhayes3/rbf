from rbf.engine.triggers import Trigger, Contains, Keyword, Regex


def test_trigger_class(trigger=Trigger):
    assert issubclass(trigger, object)


def test_contains_trigger():
    data = {
        "title": "A good ol' fashioned Old Fashioned",
    }
    values = ["A", "good", "ol'", "fashioned", "Old", "Fashioned"]
    component = Contains(values, field="title")
    result = component.process(data)
    assert result == "A"
    component.require_all = True
    result = component.process(data)
    assert isinstance(result, list)
    for value in values:
        assert value in result
    component.values = ["not", "present"]
    result = component.process(data)
    assert result is None
    component.field = "body"
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
    component.require_all = True
    result = component.process(data)
    assert result == keywords
    component = Keyword(["fashion"], fields=["body"])
    component.require_all = True
    result = component.process(data)
    assert result is None


def test_regex_trigger():
    pass