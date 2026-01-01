from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import admin, compare, health, matches, meta, players, teams
from app.scheduler import start_scheduler

app = FastAPI(title="Water Polo Champions League API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://waterpolo.localhost",
        "http://waterpolo-api.localhost",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"http://.*\\.localhost(:\\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(meta.router)
app.include_router(teams.router)
app.include_router(matches.router)
app.include_router(players.router)
app.include_router(compare.router)
app.include_router(admin.router)


@app.on_event("startup")
def startup_event() -> None:
    start_scheduler()
