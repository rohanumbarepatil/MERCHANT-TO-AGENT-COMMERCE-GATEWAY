from fastapi import APIRouter

from app.database.client import supabase


router = APIRouter(
    prefix="/api/agents",
    tags=["Agents"],
)


@router.get("/")
def get_agents():
    response = supabase.table("agents").select("*").execute()

    return {
        "success": True,
        "count": len(response.data),
        "agents": response.data,
    }