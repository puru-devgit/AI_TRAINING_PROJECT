from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from services.agent import run_agent_query

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentQuery(BaseModel):
    query: str


@router.post("/")
def agent_endpoint(body: AgentQuery, db: Session = Depends(get_db)):
    response = run_agent_query(db, body.query)
    return {"response": response}
