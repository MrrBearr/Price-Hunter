import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Price comparison and coupon hunting platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Search router - NO database dependency, always works
from app.routers.search import router as search_router
app.include_router(search_router, prefix="/api/search", tags=["Search"])

# DB-dependent routers - load only if database modules are available
try:
    from app.routers.auth import router as auth_router
    from app.routers.products import router as products_router
    from app.routers.offers import router as offers_router
    from app.routers.coupons import router as coupons_router
    from app.routers.alerts import router as alerts_router
    from app.routers.favorites import router as favorites_router

    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(products_router, prefix="/api/products", tags=["Products"])
    app.include_router(offers_router, prefix="/api/offers", tags=["Offers"])
    app.include_router(coupons_router, prefix="/api/coupons", tags=["Coupons"])
    app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts"])
    app.include_router(favorites_router, prefix="/api/favorites", tags=["Favorites"])
    logger.info("All routers loaded (database available)")
except Exception as e:
    logger.warning(f"DB routers not loaded: {e}. Only /api/search is available.")


@app.get("/")
async def root():
    return {"message": "PriceHunter API v1.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
