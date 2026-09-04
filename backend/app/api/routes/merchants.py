from fastapi import APIRouter

from app.database.client import supabase


router = APIRouter(
    prefix="/api/merchants",
    tags=["Merchants"],
)


@router.get("/")
def get_merchants():
    response = supabase.table("merchants").select("*").execute()

    return {
        "success": True,
        "count": len(response.data),
        "merchants": response.data,
    }