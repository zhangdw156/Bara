
from smoke import ScriptedEngine, action, make_agent

STATE_KEY = "research"

def test_active_signature_repair_executes_through_native_tool():
    from are.simulation.tools import Tool

    class EmailReply(Tool):
        name = "Emails__reply_to_email"
        description = "Reply to an email."
        inputs = {"body": {"type": "string", "description": "Reply body"}}
        output_type = "string"

        def __init__(self):
            super().__init__()
            self.delivered = []

        def forward(self, body):
            self.delivered.append(body)
            return "sent"

    engine = ScriptedEngine([action("Emails__reply_to_email", {"body": "Thanks.\nThe event starts at 10."})])
    agent, _, _ = make_agent(engine,
                             task='Reply and sign off with "Best,\\nAlice Chen".')
    email = EmailReply()
    agent.tools[email.name] = email
    agent.init_tools()
    agent.step()
    assert email.delivered == ["Thanks.\nThe event starts at 10.\n\nBest,\nAlice Chen"]
    assert len(engine.requests) == 1
    assert agent.custom_state[STATE_KEY]["last_intervention"]["reason"] == "explicit_multiline_signature"
