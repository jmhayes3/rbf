from rbf.engine.trigger import Trigger


def test_trigger_class(trigger=Trigger):
    assert issubclass(trigger, object)
