from textwrap import dedent

import pytest

from urt30arcon import Game, GameType, Player, Team
from urt30arcon.models import ServerStatus


def test_player_from_string() -> None:
    s = """\
    0:foo^7 TEAM:RED KILLS:20 DEATHS:22 ASSISTS:3 PING:98 AUTH:foo IP:127.0.0.1:58537
    """
    player = Player.from_string(dedent(s))
    assert player.name == "foo"
    assert player.team is Team.RED
    assert player.kills == 20
    assert player.deaths == 22
    assert player.assists == 3


def test_player_from_string_no_client_port() -> None:
    s = """\
    0:foo TEAM:RED KILLS:20 DEATHS:22 ASSISTS:3 PING:98 AUTH:foo IP:127.0.0.1
    """
    player = Player.from_string(dedent(s))
    assert player.name == "foo"
    assert player.ip_address == "127.0.0.1"


def test_player_negative_kills() -> None:
    s = """\
    0:foo^7 TEAM:RED KILLS:-1 DEATHS:2 ASSISTS:0 PING:98 AUTH:foo IP:127.0.0.1:58537
    """
    player = Player.from_string(dedent(s))
    assert player.name == "foo"
    assert player.team is Team.RED
    assert player.kills == -1
    assert player.deaths == 2
    assert player.assists == 0


def test_game_from_string_ctf() -> None:
    s = """\
    Map: ut4_abbey
    Players: 3
    GameType: CTF
    Scores: R:5 B:10
    MatchMode: OFF
    WarmupPhase: NO
    GameTime: 00:12:04
    0:foo^7 TEAM:RED KILLS:15 DEATHS:22 ASSISTS:0 PING:98 AUTH:foo IP:127.0.0.1:58537
    1:bar^7 TEAM:BLUE KILLS:20 DEATHS:9 ASSISTS:0 PING:98 AUTH:bar IP:127.0.0.1:58538
    2:baz^7 TEAM:RED KILLS:32 DEATHS:18 ASSISTS:0 PING:98 AUTH:baz IP:127.0.0.1:58539
    """
    game = Game.from_string(dedent(s))
    assert game.map_name == "ut4_abbey"
    assert game.type is GameType.CTF
    assert game.score_red == 5
    assert game.score_blue == 10
    assert game.time == "00:12:04"
    assert len(game.players) == 3


def test_game_from_string_ffa() -> None:
    s = """\
    Map: ut4_docks
    Players: 3
    GameType: FFA
    MatchMode: OFF
    WarmupPhase: NO
    GameTime: 00:12:04
    0:foo^7 TEAM:FREE KILLS:15 DEATHS:22 ASSISTS:0 PING:98 AUTH:foo IP:127.0.0.1:0
    1:bar^7 TEAM:FREE KILLS:20 DEATHS:9 ASSISTS:0 PING:98 AUTH:bar IP:127.0.0.1:0
    2:baz^7 TEAM:FREE KILLS:32 DEATHS:18 ASSISTS:0 PING:98 AUTH:baz IP:127.0.0.1:0
    """
    game = Game.from_string(dedent(s))
    assert game.map_name == "ut4_docks"
    assert game.type is GameType.FFA
    assert game.score_red == 0
    assert game.score_blue == 0
    assert game.time == "00:12:04"
    assert len(game.players) == 3


def test_game_from_string_double() -> None:
    s = """\
    Map: ut4_slumwar
    Players: 10
    GameType: CTF
    Scores: R:0 B:0
    MatchMode: OFF
    WarmupPhase: NO
    GameTime: 00:14:59
    0:|30+|LtStriker^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:75.159.59.35:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    1:|30+|money^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:67.181.15.50:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    2:|30+|Mandolin^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:75.81.154.133:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    8:Jojo^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:190.143.252.53:36118
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    9:|30+r|Duckling^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:108.26.199.179:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    10:Crazytheory^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:62.183.154.217:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    11:|16+|PaladsLittlestDottir^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:136.34.165.102:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    12:[Gz]Iron_Front^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:115.188.207.241:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    13:|30+|Sleap^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:163.182.76.81:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    16:^2Binge^3^2Grab^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:--- IP:108.170.156.105:15370
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    Map: ut4_slumwar
    Players: 10
    GameType: CTF
    Scores: R:0 B:0
    MatchMode: OFF
    WarmupPhase: NO
    GameTime: 00:14:53
    0:|30+|LtStriker^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:720 AUTH:ltstriker IP:75.159.59.35:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    1:|30+|money^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:636 AUTH:m0neysh0t IP:67.181.15.50:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    2:|30+|Mandolin^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:mandolin IP:75.81.154.133:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    8:Jojo^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:noobsaibot IP:190.143.252.53:36118
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    9:|30+r|Duckling^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:duckling IP:108.26.199.179:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    10:Crazytheory^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:crazytheory IP:62.183.154.217:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    11:|16+|PaladsLittlestDottir^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:paladslittlestdottir IP:136.34.165.102:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    12:[Gz]Iron_Front^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:wardog IP:115.188.207.241:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    13:|30+|Sleap^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:cplus IP:163.182.76.81:27960
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    16:^2Binge^3^2Grab^7 TEAM:SPECTATOR KILLS:0 DEATHS:0 ASSISTS:0 PING:0 AUTH:bingegrab IP:108.170.156.105:15370
    CTF: CAP:0 RET:0 KFC:0 STC:0 PRF:0
    """
    game = Game.from_string(dedent(s))
    assert len(game.players) == 10
    assert game.players[1].auth == "m0neysh0t"


def test_status_default_server() -> None:
    s = """\
    map: ut4_casa
    num score ping name            lastmsg address               qport rate
    --- ----- ---- --------------- ------- --------------------- ----- -----
      4    40  141 theName^7              0 11.22.33.44:27961     38410 32000
      5    13   48 theName2^7             0 11.22.33.45:27961     38410 32000
    """
    status = ServerStatus.from_string(dedent(s))
    assert len(status.clients) == 2
    assert status.clients[0].slot == "4"
    assert status.clients[0].score == 40
    assert status.clients[0].name == "theName"
    assert status.clients[0].ip_address == "11.22.33.44"
    assert status.clients[0].rate == 32000
    assert status.clients[1].slot == "5"
    assert status.clients[1].score == 13
    assert status.clients[1].name == "theName2"
    assert status.clients[1].ip_address == "11.22.33.45"
    assert status.clients[1].rate == 32000


def test_status_quake3e_server() -> None:
    s = """\
    map: ut4_tohunga_b8
    cl score ping name               address         rate
    -- ----- ---- ------------------ --------------- -----
     5    11   32 |30+|hedgehog     ^7 11.22.222.222   32000
     7     3   40 ^5B^2i^5nge^8&^8^9^3Grab        ^7 11.222.33.222   25000
    """
    status = ServerStatus.from_string(dedent(s))
    assert len(status.clients) == 2
    assert status.clients[0].slot == "5"
    assert status.clients[0].score == 11
    assert status.clients[0].ping == 32
    assert status.clients[0].name == "|30+|hedgehog"
    assert status.clients[0].rate == 32000
    assert status.clients[1].slot == "7"
    assert status.clients[1].score == 3
    assert status.clients[1].ping == 40
    assert status.clients[1].name == "^5B^2i^5nge^8&^8^9^3Grab"
    assert status.clients[1].ip_address == "11.222.33.222"
    assert status.clients[1].rate == 25000


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Red", Team.RED),
        ("r", Team.RED),
        ("1", Team.RED),
        ("Blue", Team.BLUE),
        ("b", Team.BLUE),
        ("2", Team.BLUE),
        ("Spectator", Team.SPECTATOR),
        ("Spec", Team.SPECTATOR),
        ("s", Team.SPECTATOR),
        ("3", Team.SPECTATOR),
    ],
)
def test_team_from_string_valid(value: str, expected: Team) -> None:
    assert Team.from_string(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "Read",
        "Blu",
        "Spek",
        "4",
    ],
)
def test_team_from_string_invalid(value: str) -> None:
    with pytest.raises(ValueError):  # noqa: PT011
        Team.from_string(value)
