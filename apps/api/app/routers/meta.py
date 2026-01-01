from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud
from app.database import get_session
from app.schemas import MetaFreshness, OptionsResponse
from waterpolo.scrape.storage import list_contatori

router = APIRouter(prefix="/meta")


@router.get("/freshness", response_model=MetaFreshness)
def freshness(session: Session = Depends(get_session)) -> MetaFreshness:
    data = crud.get_meta_freshness(session)
    return MetaFreshness(**data)


@router.get("/options", response_model=OptionsResponse)
def options() -> OptionsResponse:
    data = list_contatori()
    return OptionsResponse(schedules=data.get("schedules", []))
