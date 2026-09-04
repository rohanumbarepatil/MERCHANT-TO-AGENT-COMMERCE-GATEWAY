from fastapi import APIRouter

from app.database.client import supabase


router = APIRouter(
    prefix="/api/policies",
    tags=["Policies"],
)


@router.get("/")
def get_policies():
    response = supabase.table("policies").select("*").execute()

    return {
        "success": True,
        "count": len(response.data),
        "policies": response.data,
    }