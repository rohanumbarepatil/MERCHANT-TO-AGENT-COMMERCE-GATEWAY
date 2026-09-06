from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.products import router as products_router
from app.api.routes.merchants import router as merchants_router
from app.api.routes.agents import router as agents_router
from app.api.routes.policies import router as policies_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.payments import router as payments_router
from app.api.routes.approvals import router as approvals_router
from app.api.routes.audit import router as audit_router
from app.api.routes.agent import router as agent_router
from app.api.routes.webhook import router as webhook_router

app = FastAPI(title="Merchant-to-Agent Commerce Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(merchants_router)
app.include_router(products_router)
app.include_router(agents_router)
app.include_router(policies_router)
app.include_router(transactions_router)
app.include_router(payments_router)
app.include_router(approvals_router)
app.include_router(audit_router)
app.include_router(agent_router)
app.include_router(webhook_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "merchant-to-agent-commerce-gateway",
    }