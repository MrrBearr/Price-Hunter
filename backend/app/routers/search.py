import logging
from typing import List, Optional
from fastapi import APIRouter, Query

from app.services.search_service import search_mercadolivre_direct

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    store: Optional[str] = None,
    sort_by: str = Query("relevance", enum=["relevance", "price_asc", "price_desc", "name"]),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """
    Search products - fetches directly from Mercado Livre API.
    No database required for basic search to work.
    """
    logger.info(f"Search request: q={q}, sort_by={sort_by}, page={page}")

    # Always fetch from ML API directly for fresh results
    ml_results = await search_mercadolivre_direct(q)
    logger.info(f"Got {len(ml_results)} direct results")

    if not ml_results:
        return []

    # Apply filters
    filtered = ml_results
    if min_price:
        filtered = [r for r in filtered if r.price >= min_price]
    if max_price:
        filtered = [r for r in filtered if r.price <= max_price]

    # Sort
    if sort_by == "price_asc":
        filtered.sort(key=lambda x: x.price)
    elif sort_by == "price_desc":
        filtered.sort(key=lambda x: x.price, reverse=True)
    elif sort_by == "name":
        filtered.sort(key=lambda x: x.name.lower())

    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]

    # Return as product-like response
    response = []
    for item in paginated:
        response.append({
            "id": item.id,
            "name": item.name,
            "slug": item.slug,
            "description": item.description,
            "category": item.category,
            "brand": item.brand,
            "image_url": item.image_url,
            "min_price": item.min_price,
            "max_price": item.max_price,
            "offers_count": item.offers_count,
            "created_at": item.created_at,
        })

    return response


@router.post("/trigger")
async def trigger_search(
    q: str = Query(..., min_length=2),
):
    """Trigger a search - returns results from ML API."""
    results = await search_mercadolivre_direct(q)
    return {"message": "Search completed", "query": q, "results_count": len(results)}
