from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.manual_search import search_manual_online

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    model: str


@router.post("/manuals")
async def search_manual(req: SearchRequest):
    results = search_manual_online(req.model)

    if not results:
        raise HTTPException(404, "No manuals found on ManualOnline.")

    return {"results": results}

