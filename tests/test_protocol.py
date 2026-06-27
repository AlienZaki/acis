"""Unit tests for the Pydantic WS protocol."""

from acis.protocol import AudioChunk, Hello, Ping, SessionStart, SessionStop, parse_inbound


def test_parse_hello():
    msg = parse_inbound('{"type": "hello"}')
    assert isinstance(msg, Hello)


def test_parse_session_start_with_name():
    msg = parse_inbound('{"type": "session.start", "name": "Team standup"}')
    assert isinstance(msg, SessionStart)
    assert msg.name == "Team standup"


def test_parse_session_start_no_name():
    msg = parse_inbound('{"type": "session.start"}')
    assert isinstance(msg, SessionStart)
    assert msg.name is None


def test_parse_session_stop():
    msg = parse_inbound('{"type": "session.stop"}')
    assert isinstance(msg, SessionStop)


def test_parse_audio_chunk():
    msg = parse_inbound('{"type": "audio.chunk", "data_b64": "AAAA", "sample_rate": 16000}')
    assert isinstance(msg, AudioChunk)
    assert msg.sample_rate == 16000


def test_parse_audio_chunk_default_sample_rate():
    msg = parse_inbound('{"type": "audio.chunk", "data_b64": "AAAA"}')
    assert isinstance(msg, AudioChunk)
    assert msg.sample_rate == 16000


def test_parse_ping():
    msg = parse_inbound('{"type": "ping"}')
    assert isinstance(msg, Ping)


def test_parse_unknown_returns_none():
    assert parse_inbound('{"type": "unknown_type"}') is None


def test_parse_malformed_returns_none():
    assert parse_inbound("not json at all") is None
    assert parse_inbound("{}") is None


def test_parse_dict_input():
    msg = parse_inbound({"type": "hello"})
    assert isinstance(msg, Hello)
