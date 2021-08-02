import pytest

from tickit.utils.topic_naming import input_topic, output_topic


def test_input_affixes():
    assert "tickit-my_device-in" == input_topic("my_device")


def test_input_raises_empty():
    with pytest.raises(ValueError):
        input_topic("")


def test_output_affixes():
    assert "tickit-my_device-out" == output_topic("my_device")


def test_output_raises_empty():
    with pytest.raises(ValueError):
        output_topic("")
