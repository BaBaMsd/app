from models.agent import Agent

agents_db = {}

def get_agent_by_code(code: str) -> Agent:
    for agent in agents_db.values():
        if agent.code == code:
            return agent
    return None
