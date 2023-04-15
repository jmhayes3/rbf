from engine.trigger.components import Contains, Keyword


def test_contains_component():
    data = {
        "title": "A good ol' fashioned Old Fashioned",
    }
    values = ["A", "good", "ol'", "fashioned", "Old", "Fashioned"]
    component = Contains(values, field="title")
    result = component.process(data)
    assert result == "A"
    component.require_all = True
    result = component.process(data)
    assert all([value if value in result else None for value in values])
    component.values = ["not", "present"]
    result = component.process(data)
    assert result is None
    component.field = "body"
    result = component.process(data)
    assert result is None


def test_keyword_component():
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
