from fastapi import APIRouter, HTTPException, Depends
from services.agent_service import get_agent_by_code
from models.agent import Agent
from core.security import verify_token

router = APIRouter()

@router.get("/{agent_code}")
def get_agent(agent_code: str, token: str = Depends(verify_token)):
    agent = get_agent_by_code(agent_code)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
