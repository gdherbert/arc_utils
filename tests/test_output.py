import pytest

from arc_utils import output


def test_output_msg_reraises_arcpy_message_errors(monkeypatch, capsys):
    error = RuntimeError("message output failed")

    def fail_add_message(message):
        raise error

    monkeypatch.setattr(output.arcpy, "AddMessage", fail_add_message)

    with pytest.raises(RuntimeError) as raised:
        output.output_msg("message")

    assert raised.value is error
    assert capsys.readouterr().out == "message\n"
