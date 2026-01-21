from fastapi import FastAPI 
# from fastapi_pagination import Page, add_pagination, paginate
from src.route.auth_route import auth_router
from src.route.group_route import group_router 
from src.route.socket_route import socket_router
from src.route.wallet_route import wallet_router
from .middleware import register_middleware





version = "v1"

description = """
A REST API for a Fintech Application Service.
    """

version_prefix =f"/api"

app = FastAPI( 
    title="FinApp",
    description=description,
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "url": "https://github.com/sasbaws221",
        "email": "ssako@faabsystems.com",
    },
    terms_of_service="https://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
)


register_middleware(app)

app.include_router(auth_router, prefix=f"{version_prefix}", tags=["Auth"]) 
app.include_router(group_router, prefix=f"{version_prefix}", tags=["Group"]) 
app.include_router(socket_router, prefix=f"{version_prefix}", tags=["Socket"]) 
app.include_router(wallet_router, prefix=f"{version_prefix}", tags=["Wallet"])

