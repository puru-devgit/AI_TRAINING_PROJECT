from fastapi import APIRouter, Query
from services.rag import retrieve_risks

router = APIRouter(prefix="/risks", tags=["risks"])


@router.get("/")
def get_risks(query: str = Query(default="supply chain disruption"), top_k: int = Query(default=5)):
    results = retrieve_risks(query, top_k=top_k)
    return {"query": query, "results": results}
