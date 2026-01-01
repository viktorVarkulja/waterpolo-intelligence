from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_login, verify_token
from app.config import settings
from app.database import get_session
from app.importer import import_csv
from app.schemas import CsvImportRequest, ImportResult, LoginRequest, LoginResponse, ScrapeRequest, ScrapeResult
from waterpolo.common.logging import get_logger
from waterpolo.scrape.storage import run_scrape_full

router = APIRouter(prefix="/admin")
logger = get_logger("admin")


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    if not verify_login(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logger.info("Admin login success for user=%s", payload.username)
    token = create_access_token(payload.username)
    return LoginResponse(access_token=token)


@router.post("/import/csv", response_model=ImportResult)
def import_csv_endpoint(
    payload: CsvImportRequest,
    session: Session = Depends(get_session),
    _user: str = Depends(verify_token),
) -> ImportResult:
    logger.info("CSV import requested path=%s", payload.path or settings.csv_default_path)
    rows = import_csv(session, payload.path)
    session.commit()
    logger.info("CSV import complete rows=%s", rows)
    return ImportResult(rows_inserted=rows)


@router.post("/scrape/run", response_model=ScrapeResult)
def run_scrape(
    payload: ScrapeRequest,
    session: Session = Depends(get_session),
    _user: str = Depends(verify_token),
) -> ScrapeResult:
    logger.info(
        "Scrape run requested season=%s stage=%s calendar_url=%s",
        payload.season,
        payload.stage,
        payload.calendar_url,
    )
    run_scrape_full(
        session,
        season=payload.season,
        stage=payload.stage,
        calendar_url=payload.calendar_url,
    )
    session.commit()
    logger.info("Scrape run complete season=%s stage=%s", payload.season, payload.stage)
    return ScrapeResult(status="started")
