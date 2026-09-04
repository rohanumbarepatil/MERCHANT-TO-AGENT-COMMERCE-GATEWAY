from typing import Any

from fastapi import APIRouter, Query

from app.database.client import supabase


router = APIRouter(
    prefix="/api/products",
    tags=["Products"],
)


@router.get("/")
def get_products() -> dict[str, Any]:
    response = (
        supabase
        .table("products")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return {
        "success": True,
        "count": len(response.data),
        "products": response.data,
    }


@router.get("/search")
def search_products(
    q: str = Query(..., min_length=1),
    max_price: float | None = Query(default=None, gt=0),
) -> dict[str, Any]:

    query = (
        supabase
        .table("products")
        .select("*")
        .ilike("name", f"%{q}%")
    )

    if max_price is not None:
        query = query.lte("price", max_price)

    response = query.order("price").execute()

    return {
        "success": True,
        "query": q,
        "max_price": max_price,
        "count": len(response.data),
        "products": response.data,
    }