import pytest
from outo_agentcore.core.message import Message

def test_forward_message():
    msg = Message(type="forward", sender="user", receiver="agent", content="hello")
    assert msg.type == "forward"
    assert msg.sender == "user"
    assert msg.receiver == "agent"
    assert msg.content == "hello"
    assert msg.call_id

def test_return_message():
    msg = Message(type="return", sender="agent", receiver="user", content="result")
    assert msg.type == "return"

def test_auto_call_id_unique():
    msg1 = Message(type="forward", sender="a", receiver="b", content="x")
    msg2 = Message(type="forward", sender="a", receiver="b", content="x")
    assert msg1.call_id != msg2.call_id

def test_custom_call_id():
    msg = Message(type="forward", sender="a", receiver="b", content="x", call_id="custom-123")
    assert msg.call_id == "custom-123"