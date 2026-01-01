export type Freshness = {
  last_import: string | null;
  team_count: number;
  match_count: number;
  team_match_stat_count: number;
};

export type TeamAggregate = {
  matches: number;
  goals_per_match: number;
  shooting_pct: number;
  extra_man_pct: number;
  center_pct: number;
  counter_pct: number;
  penalty_pct: number;
  sprints_win_pct: number;
  turnovers_per_match: number;
  steals_per_match: number;
};

export type Team = {
  id: number;
  name: string;
  slug: string;
  aggregates: TeamAggregate;
  rank?: number | null;
  form?: number[] | null;
};

export type TrendPoint = {
  match_index: number;
  goals: number;
  shots: number;
  shooting_pct: number;
};

export type Trends = {
  team_id: number;
  window: number;
  points: TrendPoint[];
};

export type Player = {
  id: number;
  team_id: number | null;
  name: string;
  number: number | null;
  position: string | null;
  team_name?: string | null;
  age?: number | null;
  stats?: Record<string, number | null> | null;
};

export type Match = {
  id: number | string;
  season?: string | null;
  stage?: string | null;
  date?: string | null;
  home_team: string;
  away_team: string;
  home_score: number | null;
  away_score: number | null;
  venue?: string | null;
};

export type CompareResponse = {
  team_a: Team;
  team_b: Team;
  deltas: Record<string, number>;
};

export type ScheduleOption = {
  file: string;
  date: string | null;
  counter: string;
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://waterpolo-api.localhost";

function buildQuery(params: Record<string, string | number | null | undefined>): string {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === null || value === undefined || value === "") {
      return;
    }
    query.set(key, String(value));
  });
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

async function fetchJson<T>(path: string, params: Record<string, string | number | null | undefined> = {}) {
  const res = await fetch(`${baseUrl}${path}${buildQuery(params)}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  freshness: () => fetchJson<Freshness>("/meta/freshness"),
  options: () => fetchJson<{ schedules: ScheduleOption[] }>("/meta/options"),
  teams: (filters: Record<string, string | number | null | undefined>) =>
    fetchJson<Team[]>("/teams", filters),
  teamById: (id: number) => fetchJson<Team>(`/teams/${id}`),
  teamBySlug: (slug: string) => fetchJson<Team>(`/teams/slug/${slug}`),
  teamTrends: (id: number, filters: Record<string, string | number | null | undefined>) =>
    fetchJson<Trends>(`/teams/${id}/trends`, filters),
  teamMatches: (id: number, filters: Record<string, string | number | null | undefined>) =>
    fetchJson<Match[]>(`/teams/${id}/matches`, filters),
  compare: (filters: Record<string, string | number | null | undefined>) =>
    fetchJson<CompareResponse>("/compare", filters),
  players: (filters: Record<string, string | number | null | undefined>) =>
    fetchJson<Player[]>("/players", filters),
  player: (id: number) => fetchJson<Player>(`/players/${id}`),
  playerTrends: (id: number, filters: Record<string, string | number | null | undefined>) =>
    fetchJson<{ points: TrendPoint[] }>(`/players/${id}/trends`, filters),
  matches: (filters: Record<string, string | number | null | undefined>) =>
    fetchJson<Match[]>("/matches", filters),
  match: (id: string | number) => fetchJson<Match>(`/matches/${id}`)
};
