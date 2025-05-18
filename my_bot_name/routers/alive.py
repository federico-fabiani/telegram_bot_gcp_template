from fastapi import APIRouter, status

router = APIRouter(tags=["alive"])


@router.get("/ping", status_code=status.HTTP_200_OK)
async def ping():
    """
    Ping endpoint.

    Returns:
        str: A string response indicating the alive status.
    """
    return "Alive"
