"use client";

import { useQuery } from "@tanstack/react-query";

import { api } from "./api";
import { queryKeys } from "./queryKeys";

export function useFreshness() {
  return useQuery({ queryKey: queryKeys.freshness, queryFn: api.freshness });
}

export function useOptions() {
  return useQuery({ queryKey: queryKeys.options, queryFn: api.options });
}

export function useTeams(filters: Record<string, string | number | null | undefined>) {
  return useQuery({ queryKey: queryKeys.teams(filters), queryFn: () => api.teams(filters) });
}

export function useTeam(idOrSlug: number | string, bySlug = false) {
  return useQuery({
    queryKey: queryKeys.team(idOrSlug),
    queryFn: () => (bySlug ? api.teamBySlug(idOrSlug as string) : api.teamById(idOrSlug as number))
  });
}

export function useTeamTrends(id: number, filters: Record<string, string | number | null | undefined>) {
  return useQuery({
    queryKey: queryKeys.teamTrends(id, filters),
    queryFn: () => api.teamTrends(id, filters),
    enabled: Number.isFinite(id)
  });
}

export function useTeamMatches(id: number, filters: Record<string, string | number | null | undefined>) {
  return useQuery({
    queryKey: queryKeys.teamMatches(id, filters),
    queryFn: () => api.teamMatches(id, filters),
    enabled: Number.isFinite(id)
  });
}

export function useTeamRoster(id: number, filters: Record<string, string | number | null | undefined>) {
  return useQuery({
    queryKey: queryKeys.teamRoster(id, filters),
    queryFn: () => api.teamRoster(id, filters),
    enabled: Number.isFinite(id)
  });
}

export function useCompare(filters: Record<string, string | number | null | undefined>) {
  return useQuery({ queryKey: queryKeys.compare(filters), queryFn: () => api.compare(filters) });
}

export function usePlayers(filters: Record<string, string | number | null | undefined>) {
  return useQuery({ queryKey: queryKeys.players(filters), queryFn: () => api.players(filters) });
}

export function usePlayer(id: number) {
  return useQuery({ queryKey: queryKeys.player(id), queryFn: () => api.player(id), enabled: Number.isFinite(id) });
}

export function usePlayerTrends(id: number, filters: Record<string, string | number | null | undefined>) {
  return useQuery({
    queryKey: queryKeys.playerTrends(id, filters),
    queryFn: () => api.playerTrends(id, filters),
    enabled: Number.isFinite(id)
  });
}

export function useMatches(filters: Record<string, string | number | null | undefined>) {
  return useQuery({ queryKey: queryKeys.matches(filters), queryFn: () => api.matches(filters) });
}

export function useMatch(id: string | number) {
  return useQuery({ queryKey: queryKeys.match(id), queryFn: () => api.match(id), enabled: !!id });
}
