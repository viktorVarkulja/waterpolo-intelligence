# Water Polo Champions League Analytics

Monorepo for a FastAPI + Next.js analytics dashboard.

## Structure

```
project/
  apps/web
  apps/api
  packages/waterpolo
  infra/docker-compose.yml
```

## Local dev (Docker)

If you're using the shared Traefik proxy, start it first:

```bash
cd /mnt/d/Viktor/TestCodes/traefik
docker compose up -d
```

Add hosts entries (Windows file at `C:\Windows\System32\drivers\etc\hosts`):

```
127.0.0.1 waterpolo.localhost
127.0.0.1 waterpolo-api.localhost
```

1) Start services:

```bash
docker compose -f infra/docker-compose.yml up --build
```

2) Run migrations:

```bash
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

3) Seed from CSV (via Traefik):

```bash
curl -X POST http://waterpolo-api.localhost/admin/import/csv \
  -H "Content-Type: application/json" \
  -d '{"path": "/mnt/data/match_data_correct.csv"}'
```

- Web UI: http://waterpolo.localhost
- API docs: http://waterpolo-api.localhost/docs

## Local dev (no Docker)

API:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ../../packages/waterpolo
pip install -e .
export DATABASE_URL="postgresql+psycopg2://waterpolo:waterpolo@localhost:5432/waterpolo"
export CSV_DEFAULT_PATH="/mnt/data/match_data_correct.csv"
export ADMIN_JWT_SECRET="change-me"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="admin"
alembic upgrade head
uvicorn app.main:app --reload
```

Web:

```bash
cd apps/web
npm install
export NEXT_PUBLIC_API_URL="http://waterpolo-api.localhost"
npm run dev
```

## Env files

- `apps/api/.env.example`
- `apps/web/.env.local.example`
Set `ADMIN_JWT_SECRET`, `ADMIN_USERNAME`, and `ADMIN_PASSWORD` for the admin panel.

## Data assumptions

- CSV rows come in home/away pairs; the importer pairs rows by index (0/1, 2/3, ...).
- `matches.match_key` uses a hash of team names + scores + row index. This is deterministic per CSV import and avoids duplicates.
- Dates and source URLs are nullable until the scraper provides them.

## Extending the scraper

Implement the `SeleniumChampionsLeagueScraper` methods in `packages/waterpolo/waterpolo/scrape/selenium_scraper.py`:
- `fetch_team_match_stats`: pull match stats tables (already done in notebooks) and return a DataFrame matching the CSV columns.
- `fetch_rosters`: collect roster data into `players` (team, name, number, position).
- `fetch_player_match_stats`: for each match page, collect per-player stats and map to `player_match_stats`.

The `/admin/scrape/run` endpoint is wired to the scraper interface; once implemented it can insert into DB via the ETL + upsert routines.

## First 10 derived metrics to add

1) Goals per match
2) Shooting percentage (ToG/ToSh)
3) Extra-man conversion (EXG/EXSh)
4) Center conversion (CeG/CeSh)
5) Counter conversion (CoG/CoSh)
6) Penalty conversion (PG/PSh)
7) Sprint win rate (SpW/Sp)
8) Turnovers per match (To / matches)
9) Steals per match (St / matches)
10) Exclusions drawn per match (ExCe / matches)
