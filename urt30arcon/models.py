import dataclasses
import enum
import logging
import re
from typing import Self

logger = logging.getLogger(__name__)

RE_COLOR = re.compile(r"(\^\d)")
RE_SCORES = re.compile(r"\s*R:(?P<RED>\d+)\s+B:(?P<BLUE>\d+)")
RE_PLAYER = re.compile(
    r"^(?P<slot>[0-9]+):(?P<name>.*)\s+"
    r"TEAM:(?P<team>RED|BLUE|SPECTATOR|FREE)\s+"
    r"KILLS:(?P<kills>-?[0-9]+)\s+"
    r"DEATHS:(?P<deaths>[0-9]+)\s+"
    r"ASSISTS:(?P<assists>[0-9]+)\s+"
    r"PING:(?P<ping>[0-9]+|CNCT|ZMBI)\s+"
    r"AUTH:(?P<auth>.*)\s+"
    r"IP:(?P<ip_address>.*)(:(?P<ip_port>.*))?$",
    re.IGNORECASE,
)
_RE_CVAR_PATTERNS = (
    # "sv_maxclients" is:"16^7" default:"8^7"
    # latched: "12"  # noqa: ERA001
    re.compile(
        r'^"(?P<cvar>[a-z0-9_.]+)"\s+is:\s*'
        r'"(?P<value>.*?)(\^7)?"\s+default:\s*'
        r'"(?P<default>.*?)(\^7)?"$',
        re.IGNORECASE | re.MULTILINE,
    ),
    # "g_maxGameClients" is:"0^7", the default
    # latched: "1"  # noqa: ERA001
    re.compile(
        r'^"(?P<cvar>[a-z0-9_.]+)"\s+is:\s*'
        r'"(?P<default>(?P<value>.*?))(\^7)?",\s+the\sdefault$',
        re.IGNORECASE | re.MULTILINE,
    ),
    # "mapname" is:"ut4_abbey^7"
    re.compile(
        r'^"(?P<cvar>[a-z0-9_.]+)"\s+is:\s*"(?P<value>.*?)(\^7)?"$',
        re.IGNORECASE | re.MULTILINE,
    ),
)
_RE_AUTH_WHOIS = re.compile(
    r"^auth: id: (?P<id>\d+) - name: (?P<name>.*?) - login: (?P<login>.*?)"
    r" - notoriety: (?P<notoriety>.*?) - level: (?P<level>[-0-9]+)\s+"
)
_RE_STATUS_DEFAULT = re.compile(
    r"^\s*(?P<slot>\d+)\s+(?P<score>-?\d+)\s+(?P<ping>\d+|CNCT|ZMBI)\s+"
    r"(?P<name>.*?)\s+\d+\s+(?P<ip_address>[0-9.]+)(:\d+)?\s+\d+\s+(?P<rate>\d+)$"
)
_RE_STATUS_QUAKE3E = re.compile(
    r"^\s*(?P<slot>\d+)\s+(?P<score>-?\d+)\s+(?P<ping>\d+|CNCT|ZMBI)\s+"
    r"(?P<name>.*?)\s*\^7\s+(?P<ip_address>[0-9.]+)\s+(?P<rate>\d+)$"
)
_PING = {
    "CNCT": "-1",
    "ZMBI": "-2",
}

_GAME_MAP_UNKNOWN = "unknown"


class RconError(Exception):
    pass


@dataclasses.dataclass
class AuthWhois:
    id: str
    name: str
    login: str
    notoriety: str | None
    level: int

    @classmethod
    def from_string(cls, data: str) -> Self:
        if m := _RE_AUTH_WHOIS.match(data):
            return cls(
                id=m["id"],
                name=m["name"],
                login=m["login"],
                notoriety=m["notoriety"],
                level=int(m["level"]),
            )
        raise ValueError(data)


@dataclasses.dataclass
class Cvar:
    name: str
    value: str
    default: str | None = None

    @classmethod
    def from_string(cls, data: str) -> Self:
        for pat in _RE_CVAR_PATTERNS:
            if m := pat.match(data):
                break
        else:
            raise ValueError(data)
        try:
            default = m["default"]
        except IndexError:
            default = None
        return cls(name=m["cvar"], value=m["value"], default=default)


@dataclasses.dataclass
class ServerStatusClient:
    slot: str
    score: int
    ping: int
    name: str
    ip_address: str
    rate: int


@dataclasses.dataclass
class ServerStatus:
    map_name: str
    clients: list[ServerStatusClient]

    @classmethod
    def from_string(cls, data: str) -> Self:
        """
        Default (vanilla) output
        map: ut4_casa
        num score ping name            lastmsg address               qport rate
        --- ----- ---- --------------- ------- --------------------- ----- -----
          0     0    0 |30+|money            0 127.0.0.1:27961       58521 32000

        Quake3e output
        map: ut4_tohunga_b8
        cl score ping name               address         rate
        -- ----- ---- ------------------ --------------- -----
         5    11   32 |30+|hedgehog     ^7 11.22.222.222   32000
        """
        lines = data.splitlines()
        if lines[1].startswith("num"):
            re_status = _RE_STATUS_DEFAULT
        elif lines[1].startswith("cl"):
            re_status = _RE_STATUS_QUAKE3E
        else:
            raise ValueError(lines)
        clients = []
        for line in lines[3:]:
            if not line:
                continue
            if m := re_status.match(line):
                client = ServerStatusClient(
                    slot=m["slot"],
                    score=int(m["score"]),
                    ping=int(_PING.get(m["ping"], m["ping"])),
                    name=m["name"].removesuffix("^7"),
                    ip_address=m["ip_address"],
                    rate=int(m["rate"]),
                )
                clients.append(client)
            else:
                raise ValueError(line)
        return cls(map_name=lines[0][5:], clients=clients)


class Team(enum.Enum):
    FREE = "0"
    RED = "1"
    BLUE = "2"
    SPECTATOR = "3"


class GameType(enum.Enum):
    FFA = "0"
    LMS = "1"
    TDM = "3"
    TS = "4"
    FTL = "5"
    CAH = "6"
    CTF = "7"
    BOMB = "8"
    JUMP = "9"
    FREEZETAG = "10"
    GUNGAME = "11"


@dataclasses.dataclass
class Player:
    slot: str
    name: str
    auth: str = ""
    guid: str = ""
    team: Team = Team.SPECTATOR
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    ping: int = 0
    ip_address: str | None = None

    @property
    def clean_name(self) -> str:
        return RE_COLOR.sub("", self.name)

    @classmethod
    def from_string(cls, data: str) -> Self:
        """
        0:foo^7 TEAM:RED KILLS:8 DEATHS:5 ASSISTS:0 PING:98 AUTH:foo IP:127.0.0.1:27960
        """
        if m := RE_PLAYER.match(data.strip()):
            return cls(
                slot=m["slot"],
                name=m["name"].removesuffix("^7"),
                team=Team[m["team"]],
                kills=int(m["kills"]),
                deaths=int(m["deaths"]),
                assists=int(m["assists"]),
                ping=int(_PING.get(m["ping"], m["ping"])),
                auth=m["auth"],
                ip_address=m["ip_address"],
            )

        raise ValueError(data)


@dataclasses.dataclass
class Game:
    map_name: str = _GAME_MAP_UNKNOWN
    type: GameType = GameType.FFA
    time: str = "0:00"
    warmup: bool = False
    match_mode: bool = False
    score_red: int = 0
    score_blue: int = 0
    players: list[Player] = dataclasses.field(default_factory=list)

    @property
    def spectators(self) -> list[Player]:
        return self._get_players_by_team(Team.SPECTATOR)

    @property
    def team_free(self) -> list[Player]:
        return self._get_players_by_team(Team.FREE)

    @property
    def team_red(self) -> list[Player]:
        return self._get_players_by_team(Team.RED)

    @property
    def team_blue(self) -> list[Player]:
        return self._get_players_by_team(Team.BLUE)

    def _get_players_by_team(self, team: Team) -> list[Player]:
        return [p for p in self.players if p.team is team]

    @classmethod
    def from_string(cls, data: str) -> Self:  # noqa: PLR0912
        """
        Map: ut4_abbey
        Players: 3
        GameType: CTF
        Scores: R:5 B:10
        MatchMode: OFF
        WarmupPhase: NO
        GameTime: 00:12:04
        0:foo^7 TEAM:RED KILLS:15 DEATHS:22 ASSISTS:0 PING:98 AUTH:foo IP:127.0.0.1
        """
        game = cls()
        in_header = True
        parse_warnings = []
        player_count = 0
        for line in data.splitlines():
            k, v = line.split(":", maxsplit=1)
            v = v.strip()
            if in_header:
                if k == "Map":
                    game.map_name = v
                elif k == "Players":
                    player_count = int(v)
                elif k == "GameType":
                    game.type = GameType[v]
                elif k == "Scores":
                    if m := RE_SCORES.match(v):
                        game.score_red = int(m["RED"])
                        game.score_blue = int(m["BLUE"])
                elif k == "MatchMode":
                    game.match_mode = v != "OFF"
                elif k == "WarmupPhase":
                    game.warmup = v != "NO"
                elif k == "GameTime":
                    game.time = v
                    in_header = False
                else:
                    parse_warnings.append(f"unknown header: {k} - {v}")
            elif k.isnumeric():
                player = Player.from_string(line)
                game.players.append(player)
            elif k == "Map":
                # back-to-back messages, start over
                game.players.clear()
                game.map_name = v
                in_header = True

        parse_errors = []
        if game.map_name is _GAME_MAP_UNKNOWN:
            parse_errors.append("Map entry not found in data")

        if player_count != len(game.players):
            msg = (
                f"Player count {player_count} does not match "
                f"players {len(game.players)}"
                f"\n\n{game}"
            )
            parse_errors.append(msg)

        if parse_warnings:
            logger.warning("Game parse warnings\n\t%s", "\n\t".join(parse_warnings))

        if parse_errors:
            msg = "\n".join(parse_errors)
            msg += "\nData Received:\n\n" + data
            raise RconError(msg)

        return game
