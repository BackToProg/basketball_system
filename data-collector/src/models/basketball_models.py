from pydantic import BaseModel, field_validator, Field
from typing import Union, List, Dict, Any, Optional
from datetime import datetime

# Базовые модели API ответов
class APIResponse(BaseModel):
    get: str
    parameters: Union[List[Any], Dict[str, Any]]
    errors: Union[List[str], Dict[str, Any]]  # Может быть список ИЛИ словарь
    results: int
    response: Union[List[Any], Dict[str, Any]]  # Может быть список ИЛИ словарь
    # paging может отсутствовать в некоторых endpoints

class SeasonsResponse(APIResponse):
    response: List[Union[int, str]]

# Для endpoints где есть paging создаем отдельный класс
class PagedAPIResponse(APIResponse):
    paging: Dict[str, int]

class Country(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    flag: Optional[str] = None

class CountriesResponse(APIResponse):
    response: List[Country]

# Leagues endpoint models
class CoverageGamesStatistics(BaseModel):
    teams: bool = False
    players: bool = False

class CoverageGames(BaseModel):
    statistics: Optional[CoverageGamesStatistics] = None

class SeasonCoverage(BaseModel):
    games: Optional[CoverageGames] = None
    standings: bool = False
    players: bool = False
    odds: bool = False

class Season(BaseModel):
    season: Any = Field(...)
    start: Optional[str] = None
    end: Optional[str] = None
    coverage: Optional[SeasonCoverage] = None
    
    @field_validator('season', mode='before')
    @classmethod
    def normalize_season(cls, v):
        """Нормализуем season в строку"""
        if v is None:
            return ""
        if isinstance(v, (int, float)):
            return str(v)
        return v
    
    @field_validator('start', 'end', mode='before')
    @classmethod
    def handle_null_dates(cls, v):
        """Обрабатываем null в датах"""
        return v if v is not None else ""

class LeagueCountry(BaseModel):
    id: int
    name: str
    code: Optional[str] = ""
    flag: Optional[str] = ""
    
    @field_validator('code', 'flag', mode='before')
    @classmethod
    def handle_null_strings(cls, v):
        """Обрабатываем null в строках"""
        return v if v is not None else ""

class League(BaseModel):
    id: int
    name: str
    type: str
    logo: Optional[str] = ""
    country: LeagueCountry
    seasons: List[Season]
    
    @field_validator('logo', mode='before')
    @classmethod
    def handle_null_logo(cls, v):
        """Обрабатываем null в logo"""
        return v if v is not None else ""

class LeaguesResponse(APIResponse):
    response: List[League]

# Teams endpoint models
class TeamCountry(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = ""
    code: Optional[str] = ""
    flag: Optional[str] = ""
    
    @field_validator('id', mode='before')
    @classmethod
    def handle_null_id(cls, v):
        """Обрабатываем null в id"""
        return v if v is not None else 0
    
    @field_validator('name', 'code', 'flag', mode='before')
    @classmethod
    def handle_null_strings(cls, v):
        """Обрабатываем null в строках"""
        return v if v is not None else ""

class Team(BaseModel):
    id: int
    name: str
    nationnal: bool = False
    logo: Optional[str] = ""
    country: Optional[TeamCountry] = None
    
    @field_validator('country', mode='before')
    @classmethod
    def handle_null_country(cls, v):
        """Обрабатываем случай когда country = null"""
        if v is None:
            return TeamCountry(id=0, name="", code="", flag="")
        return v

class TeamsResponse(APIResponse):
    response: List[Team]

# Statistics endpoint models
class StatisticsLeague(BaseModel):
    id: int
    name: str
    type: str
    season: str
    logo: Optional[str] = ""

class StatisticsTeam(BaseModel):
    id: int
    name: str
    logo: Optional[str] = ""

class PlayedStats(BaseModel):
    home: int
    away: int
    all: int

class WinDrawLoseStats(BaseModel):
    total: int
    percentage: str

class LocationStats(BaseModel):
    home: WinDrawLoseStats
    away: WinDrawLoseStats
    all: WinDrawLoseStats

class GamesStats(BaseModel):
    played: PlayedStats
    wins: LocationStats
    draws: LocationStats
    loses: LocationStats

class TotalStats(BaseModel):
    home: int
    away: int
    all: int

class AverageStats(BaseModel):
    home: str
    away: str
    all: str

class PointsStats(BaseModel):
    total: TotalStats
    average: AverageStats

class PointsData(BaseModel):
    for_: PointsStats = Field(alias="for")
    against: PointsStats

    class Config:
        populate_by_name = True

class TeamStatistics(BaseModel):
    league: StatisticsLeague
    country: TeamCountry  # Используем существующую модель
    team: StatisticsTeam
    games: GamesStats
    points: PointsData

class StatisticsResponse(APIResponse):
    response: Union[TeamStatistics, List[Any]]  # Может быть статистика ИЛИ пустой список при ошибке

# Players endpoint models
class Player(BaseModel):
    id: int
    name: str
    number: Optional[str] = ""
    country: Optional[str] = ""
    position: Optional[str] = ""
    age: Optional[int] = None
    
    @field_validator('number', 'country', 'position', mode='before')
    @classmethod
    def handle_null_strings(cls, v):
        """Обрабатываем null в строках"""
        return v if v is not None else ""

class PlayersResponse(APIResponse):
    response: List[Player]

# Games endpoint models
class GameTeam(BaseModel):
    id: int
    name: str
    logo: Optional[str] = ""

class GameTeams(BaseModel):
    home: GameTeam
    away: GameTeam

class QuarterScores(BaseModel):
    quarter_1: Optional[int] = None
    quarter_2: Optional[int] = None
    quarter_3: Optional[int] = None
    quarter_4: Optional[int] = None
    over_time: Optional[int] = None
    total: Optional[int] = None

class GameScores(BaseModel):
    home: QuarterScores
    away: QuarterScores

class GameStatus(BaseModel):
    long: str
    short: str
    timer: Optional[str] = None

class GameLeague(BaseModel):
    id: int
    name: str
    type: str
    season: str
    logo: Optional[str] = ""

class GameCountry(BaseModel):
    id: int
    name: str
    code: str
    flag: Optional[str] = ""

class Game(BaseModel):
    id: int
    date: str
    time: str
    timestamp: int
    timezone: str
    stage: Optional[str] = None
    week: Optional[str] = None
    venue: Optional[str] = None
    status: GameStatus
    league: GameLeague
    country: GameCountry
    teams: GameTeams
    scores: GameScores

class GamesResponse(APIResponse):
    response: List[Game]

# Teams Statistics endpoint models
class ShootingStats(BaseModel):
    total: int
    attempts: int
    percentage: Optional[int] = None  # Делаем опциональным
    
    @field_validator('percentage', mode='before')
    @classmethod
    def handle_null_percentage(cls, v):
        """Обрабатываем null в percentage"""
        return v if v is not None else 0

class ReboundsStats(BaseModel):
    total: int
    offence: int
    defense: int

class TeamGameStats(BaseModel):
    game: Dict[str, int]  # {"id": 391053}
    team: Dict[str, int]  # {"id": 813}
    field_goals: ShootingStats
    threepoint_goals: ShootingStats
    freethrows_goals: ShootingStats
    rebounds: ReboundsStats
    assists: int
    steals: int
    blocks: int
    turnovers: int
    personal_fouls: int

class TeamsStatisticsResponse(APIResponse):
    response: List[TeamGameStats]

# Players Statistics endpoint models
class PlayerGameStats(BaseModel):
    game: Dict[str, int]  # {"id": 391053}
    team: Dict[str, int]  # {"id": 813}
    player: Dict[str, Any]  # {"id": 4235, "name": "Simonis Zygimantas"}
    type: str  # "starters" or "bench"
    minutes: str  # "27:35"
    field_goals: ShootingStats
    threepoint_goals: ShootingStats
    freethrows_goals: ShootingStats
    rebounds: Dict[str, int]  # {"total": 5}
    assists: int
    points: int

class PlayersStatisticsResponse(APIResponse):
    response: List[PlayerGameStats]

# # Обновляем остальные модели
# class Team(BaseModel):
#     id: int
#     name: str
#     code: Optional[str] = None
#     country: Optional[str] = None
#     founded: Optional[int] = None
#     logo: Optional[str] = None

# class Venue(BaseModel):
#     id: Optional[int] = None
#     name: Optional[str] = None
#     city: Optional[str] = None
#     capacity: Optional[int] = None

# class GameTeam(BaseModel):
#     id: int
#     name: str

# class GameTeams(BaseModel):
#     home: GameTeam
#     away: GameTeam

# class GameScores(BaseModel):
#     home: Optional[int] = None
#     away: Optional[int] = None

# class GameStatus(BaseModel):
#     long: str
#     short: str
#     elapsed: Optional[int] = None

# class Game(BaseModel):
#     id: int
#     date: datetime
#     time: str
#     timestamp: int
#     timezone: str
#     stage: Optional[str] = None
#     week: Optional[str] = None
#     status: GameStatus
#     league: Dict[str, Any]
#     country: Dict[str, Any]
#     teams: GameTeams
#     scores: GameScores
#     venue: Optional[Venue] = None

# class GamesResponse(PagedAPIResponse):  # Используем PagedAPIResponse
#     response: List[Game]

# class League(BaseModel):
#     id: int
#     name: str
#     type: str
#     logo: str
#     country: Dict[str, Any]

# class LeaguesResponse(PagedAPIResponse):  # Используем PagedAPIResponse
#     response: List[League]