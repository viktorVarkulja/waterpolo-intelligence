# Scraping Strategy

## Sources
- Primary: `https://championsleague.europeanaquatics.org/`
- Data often appears embedded via MicroPlus (len.microplustiming.com). We discover endpoints and then use requests.

### MicroPlus calendar JSON
Example fields (from `SCH_*.JSON`):
- `cp`: season code (e.g., `CL26`)
- `e[]`: events list
  - `nm`: match id
  - `gi`: date (dd/mm/yyyy)
  - `h`: local time (HH:MM)
  - `dt1` / `dt2`: home/away team names
  - `s1_p` / `s2_p`: final score
  - `d_en`: stage/group
  - `v`: venue

### MicroPlus match stats JSON (STA)
- `jsonfilename`: contains season code (e.g., `...CL26.JSON`)
- `d1_en` / `d2_en`: team names
- `r1` / `r2`: final score
- `s_en`: stat headers
- `s1_t` / `s2_t`: team totals aligned with `s_en`
- `s1_s` / `s2_s`: player lines; `s` aligned with `s_en`

### MicroPlus roster JSON (TeamRoster_ASM)
- `n[]`: team blocks
  - `d_en`: team display name
  - `p[]`: player list
    - `cod`: player id
    - `num`: jersey number
    - `cognNome`: display name
    - `r_en`: position

### MicroPlus Contatori JSON
- `contatori[]`: list of available files (schedule, rosters, standings)
- `cod`:
  - `SCH_D` = calendar files (e.g., `SCH_14102025.JSON`)
  - `TMR` = roster file

## Endpoint discovery
Run:

```bash
waterpolo scrape-discover --out config/endpoints.json
```

This produces a JSON file with endpoint patterns. Populate it with the discovered URLs for:
- `calendar`
- `match`
- `rosters`
- `player_stats`

## ID strategy
- Team: canonical name via normalization + alias mapping in `waterpolo/common/team_aliases.py`.
- Match: use `match_id` from source; fallback hash of `(season, stage, date, home_team, away_team, venue)`.
- Player: use source player id; fallback hash of `(season, team, name, number, dob)`.

## Storage + dedupe
- Upsert order: teams → matches → team_match_stats → players → player_match_stats.
- Matches stored in `matches.match_key` with deterministic id.
- `created_at` is used for freshness.

## Raw snapshots
Saved under `packages/waterpolo/waterpolo/scrape/data/raw_snapshots/{source}/{date}/...`.

## Commands

```bash
waterpolo scrape-discover --out config/endpoints.json
waterpolo scrape-full --season 2025
waterpolo scrape-match --match-id m1
waterpolo scrape-rosters --season 2025
waterpolo ingest-csv --path /path/to/match_data_correct.csv
```

## Adding a new season
1) Update endpoint config with season params.
2) Run `waterpolo scrape-full --season <year>`.
3) Validate match counts and spot-check roster + stats coverage.
