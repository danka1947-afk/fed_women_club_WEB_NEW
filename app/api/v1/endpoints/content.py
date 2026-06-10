from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.content_session import get_content_db

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("/health")
def content_health(_db: Session = Depends(get_content_db)) -> dict[str, str]:
    """Health endpoint for the isolated content API surface."""

    return {"status": "ok", "service": "content", "database": "configured"}


@router.get("/cities")
def list_content_cities(_db: Session = Depends(get_content_db)) -> list[dict]:
    return []


@router.get("/categories")
def list_content_categories(_db: Session = Depends(get_content_db)) -> list[dict]:
    return []


@router.get("/partners")
def list_content_partners(_db: Session = Depends(get_content_db)) -> list[dict]:
    return []


@router.get("/partners/{partner_id}")
def read_content_partner(partner_id: int, _db: Session = Depends(get_content_db)) -> dict:
    return {"id": partner_id, "data": None}


@router.get("/partners/{partner_id}/offers")
def list_content_partner_offers(partner_id: int, _db: Session = Depends(get_content_db)) -> list[dict]:
    return []


@router.get("/giveaways")
def list_content_giveaways(_db: Session = Depends(get_content_db)) -> list[dict]:
    return []


@router.get("/banners")
def list_content_banners(_db: Session = Depends(get_content_db)) -> list[dict]:
    return []
