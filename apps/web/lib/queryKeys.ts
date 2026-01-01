export const queryKeys = {
  freshness: ["freshness"] as const,
  teams: (filters: Record<string, string | number | null | undefined>) =>
    ["teams", filters] as const,
  team: (idOrSlug: string | number) => ["team", idOrSlug] as const,
  teamTrends: (id: number, filters: Record<string, string | number | null | undefined>) =>
    ["team-trends", id, filters] as const,
  teamMatches: (id: number, filters: Record<string, string | number | null | undefined>) =>
    ["team-matches", id, filters] as const,
  teamRoster: (id: number, filters: Record<string, string | number | null | undefined>) =>
    ["team-roster", id, filters] as const,
  compare: (filters: Record<string, string | number | null | undefined>) =>
    ["compare", filters] as const,
  players: (filters: Record<string, string | number | null | undefined>) =>
    ["players", filters] as const,
  player: (id: number) => ["player", id] as const,
  playerTrends: (id: number, filters: Record<string, string | number | null | undefined>) =>
    ["player-trends", id, filters] as const,
  matches: (filters: Record<string, string | number | null | undefined>) =>
    ["matches", filters] as const,
  match: (id: string | number) => ["match", id] as const,
  options: ["options"] as const
};
