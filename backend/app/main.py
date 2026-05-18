from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import auth, products, offers, coupons, alerts, favorites, search

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
    allow_origins=["http://localhost:3000", "http://frontend:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(offers.router, prefix="/api/offers", tags=["Offers"])
app.include_router(coupons.router, prefix="/api/coupons", tags=["Coupons"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])


@app.get("/")
async def root():
    return {"message": "PriceHunter API v1.0", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
