from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from contextlib import asynccontextmanager

# Import routers (we'll import them after the routers are created)
from routers import auth, orders, establishments

# Import database utilities
from utils.database import connect_to_mongo, close_mongo_connection



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="OwlHacks Delivery API",
    description="A peer-to-peer delivery platform for college students",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Add health check endpoint first
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "OwlHacks Delivery API is running!"}

# Add test endpoint without authentication
@app.get("/api/test")
async def test_endpoint():
    try:
        from utils.database import get_database
        db = await get_database()
        return {"status": "ok", "message": "Database connection successful", "db_connected": True}
    except Exception as e:
        return {"status": "error", "message": str(e), "db_connected": False}

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(establishments.router, prefix="/api/establishments", tags=["establishments"])

@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.options("/{full_path:path}")
async def options_handler(request: Request, full_path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Serve static files (frontend) - this should be last to avoid intercepting API routes
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")