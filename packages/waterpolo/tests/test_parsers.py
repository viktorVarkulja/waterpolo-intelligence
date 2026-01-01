import json
from pathlib import Path

from waterpolo.scrape.parsers.calendar import parse_calendar
from waterpolo.scrape.parsers.match import parse_match
from waterpolo.scrape.parsers.roster import parse_roster
from waterpolo.scrape.parsers.stats import map_player_stats

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_calendar():
    payload = json.loads((FIXTURES / "calendar.json").read_text(encoding="utf-8"))
    matches = parse_calendar(payload)
    assert len(matches) == 1
    assert matches[0].home_team == "PRO RECCO"


def test_parse_calendar_microplus():
    payload = json.loads((FIXTURES / "microplus_calendar.json").read_text(encoding="utf-8"))
    matches = parse_calendar(payload)
    assert len(matches) == 1
    assert matches[0].season == "CL26"
    assert matches[0].home_team == "VK NOVI BEOGRAD"


def test_parse_match():
    payload = json.loads((FIXTURES / "match.json").read_text(encoding="utf-8"))
    match, stats, players, player_stats = parse_match(payload)
    assert match.match_id == "m1"
    assert len(stats) == 2
    assert stats[0].stats["ToG"] == 12
    assert players == []
    assert player_stats == []


def test_parse_roster():
    payload = json.loads((FIXTURES / "roster.json").read_text(encoding="utf-8"))
    players = parse_roster(payload)
    assert players[0].name == "Mario Bianchi"


def test_parse_microplus_roster():
    payload = json.loads((FIXTURES / "microplus_roster.json").read_text(encoding="utf-8"))
    players = parse_roster(payload)
    assert len(players) == 1
    assert players[0].team_name == "PAYS D'AIX NATATION"
    assert players[0].name == "ALBERTUCCI,H."

def test_map_player_stats():
    headers = ["G", "S", "A", "ST"]
    values = ["3", "5", "2", "1"]
    stats = map_player_stats(headers, values)
    assert stats["goals"] == 3
    assert stats["shots"] == 5


def test_parse_microplus_sta():
    payload = json.loads((FIXTURES / "microplus_sta.json").read_text(encoding="utf-8"))
    match, team_stats, players, player_stats = parse_match(payload)
    assert match.match_id.endswith("CL26")
    assert len(team_stats) == 2
    assert team_stats[0].stats["ToG"] == 14
    assert players[0].name == "PLAYER ONE"
    assert player_stats[0].stats["goals"] == 2
