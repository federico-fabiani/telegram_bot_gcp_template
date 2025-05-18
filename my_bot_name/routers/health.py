# src/backend/health/health.py
from fastapi import APIRouter, status

router = APIRouter(
    tags=["health"]
)


@router.get("/health", status_code=status.HTTP_200_OK, response_model=dict)
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: A JSON response indicating the health status.
    """
    return {"health": "OK"}
