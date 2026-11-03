
from smoke import ScriptedEngine, action, make_agent

STATE_KEY = "research"

def test_terminal_text_uses_native_user_interface():
    engine = ScriptedEngine([action("Fixture__read", {"name": "a"}), "Final answer: contents:a"])
    agent, _, reply = make_agent(engine)
    agent.step()
    agent.step()
    assert reply.calls == ["contents:a"]
