from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.scraping.manualslib_search import search_manualslib

router = APIRouter(prefix="/scrape", tags=["Scrape"])


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("/search")
async def search_manuals(request: SearchRequest):
    try:
        results = search_manualslib(request.query, request.limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "query": request.query,
        "results": results
    }
