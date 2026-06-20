"""
cmd/api/main.py
Entry point FastAPI untuk Event Ticketing & Booking System.

Menginisialisasi aplikasi, mendaftarkan semua router,
dan menyiapkan database tables saat startup.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.database.connection import create_tables
from presentation.api.routes.event_routes import router as event_router
from presentation.api.routes.booking_routes import router as booking_router
from presentation.api.routes.ticket_routes import customer_router as ticket_router
from presentation.api.routes.ticket_routes import gate_router as gate_router
from presentation.api.routes.refund_routes import router as refund_router

# ─────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────
# Lifespan (startup / shutdown)
# ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager untuk startup dan shutdown aplikasi.
    Menggantikan @app.on_event("startup") yang sudah deprecated di FastAPI 0.93+.
    """
    logger.info("Starting up Event Ticketing API...")
    create_tables()
    logger.info("Database tables verified/created.")
    yield
    logger.info("Shutting down Event Ticketing API.")


# ─────────────────────────────────────────────────────────
# FastAPI Application
# ─────────────────────────────────────────────────────────

app = FastAPI(
    title="Event Ticketing & Booking System",
    description=(
        "REST API untuk sistem pembelian tiket event berbasis "
        "Clean Architecture dan Domain-Driven Design.\n\n"
        "Dikembangkan untuk mata kuliah **EF234402 – Konstruksi Perangkat Lunak**  \n"
        "Institut Teknologi Sepuluh Nopember (ITS)"
    ),
    version="1.0.0",
    contact={
        "name": "Rafian Dany Azadirahta & Muhammad Alfaraldi Raihan",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain spesifik di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────

# Event & Ticket Category management
app.include_router(event_router, prefix="/api/v1")

# Booking (nested under event: /api/v1/events/{event_id}/bookings)
app.include_router(booking_router, prefix="/api/v1")

# Customer tickets
app.include_router(ticket_router, prefix="/api/v1")

# Gate officer check-in
app.include_router(gate_router, prefix="/api/v1")

# Refund management
app.include_router(refund_router, prefix="/api/v1")


# ─────────────────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"], summary="Health check")
def health_check() -> dict:
    """Cek apakah API sedang berjalan."""
    return {"status": "ok", "service": "event-ticketing-api"}


@app.get("/", tags=["Root"], include_in_schema=False)
def root() -> dict:
    return {
        "message": "Event Ticketing API is running.",
        "docs": "/docs",
        "redoc": "/redoc",
    }
