from typing import Optional
import httpx
import asyncio
from structlog import get_logger
from models.basketball_models import CountriesResponse, GamesResponse, LeaguesResponse, PlayersResponse, PlayersStatisticsResponse, SeasonsResponse, StatisticsResponse, TeamsResponse, TeamsStatisticsResponse

logger = get_logger()

class BasketballAPI:
    def __init__(self, api_key: str, base_url: str = "https://v1.basketball.api-sports.io"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "X-RapidAPI-Key": api_key,
                "Content-Type": "application/json"
            }
        )
    
    async def test_connection(self):
        """Проверка подключения к API"""
        try:
            response = await self.client.get(f"{self.base_url}/status")
            response.raise_for_status()
            data = response.json()
            logger.info("API connection test successful", response=data)
            return True
        except httpx.HTTPError as e:
            logger.error("API connection test failed", error=str(e))
            return False
    
    async def get_seasons(self) -> Optional[SeasonsResponse]:
        """Получение списка всех доступных сезонов"""
        try:
            response = await self.client.get(f"{self.base_url}/seasons")
            response.raise_for_status()
            data = response.json()
            return SeasonsResponse(**data)
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch seasons", error=str(e))
            return None
    
    async def get_countries(
        self, 
        country_id: Optional[int] = None,
        name: Optional[str] = None,
        code: Optional[str] = None,
        search: Optional[str] = None
    ) -> Optional[CountriesResponse]:
        """Получение списка стран с фильтрацией"""
        try:
            params = {}
            if country_id:
                params["id"] = country_id
            if name:
                params["name"] = name
            if code:
                params["code"] = code
            if search:
                params["search"] = search
                
            response = await self.client.get(
                f"{self.base_url}/countries",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return CountriesResponse(**data)
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch countries", params=params, error=str(e))
            return None

    async def get_leagues(
        self,
        league_id: Optional[int] = None,
        name: Optional[str] = None,
        country_id: Optional[int] = None,
        country: Optional[str] = None,
        type: Optional[str] = None,
        season: Optional[str] = None,
        search: Optional[str] = None,
        code: Optional[str] = None,
        filter_by_stats_coverage: bool = True  # Новая опция фильтрации
    ) -> Optional[LeaguesResponse]:
        """Получение списка лиг с фильтрацией по coverage статистики"""
        try:
            params = {}
            if league_id:
                params["id"] = league_id
            if name:
                params["name"] = name
            if country_id:
                params["country_id"] = country_id
            if country:
                params["country"] = country
            if type:
                params["type"] = type
            if season:
                params["season"] = season
            if search:
                params["search"] = search
            if code:
                params["code"] = code
                
            response = await self.client.get(
                f"{self.base_url}/leagues",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            leagues_response = LeaguesResponse(**data)
            
            # Фильтрация по coverage статистики
            if filter_by_stats_coverage and leagues_response.response:
                filtered_leagues = []
                for league in leagues_response.response:
                    # Проверяем каждый сезон лиги
                    valid_seasons = []
                    for season_data in league.seasons:
                        coverage = season_data.coverage
                        # Проверяем наличие статистики по играм, командам и игрокам
                        if (coverage.games and 
                            coverage.games.statistics and 
                            coverage.games.statistics.teams and 
                            coverage.games.statistics.players):
                            valid_seasons.append(season_data)
                    
                    # Если есть сезоны с полной статистикой, оставляем лигу
                    if valid_seasons:
                        league.seasons = valid_seasons
                        filtered_leagues.append(league)
                
                leagues_response.response = filtered_leagues
                leagues_response.results = len(filtered_leagues)
            
            return leagues_response
            
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch leagues", params=params, error=str(e))
            return None
    
    async def get_teams(
        self,
        team_id: Optional[int] = None,
        name: Optional[str] = None,
        country_id: Optional[int] = None,
        country: Optional[str] = None,
        league: Optional[int] = None,
        season: Optional[str] = None,
        search: Optional[str] = None
    ) -> Optional[TeamsResponse]:
        """Получение данных о командах с фильтрацией"""
        try:
            params = {}
            if team_id:
                params["id"] = team_id
            if name:
                params["name"] = name
            if country_id:
                params["country_id"] = country_id
            if country:
                params["country"] = country
            if league:
                params["league"] = league
            if season:
                params["season"] = season
            if search:
                params["search"] = search
            
            # Проверяем, что есть хотя бы один параметр
            if not params:
                logger.warning("Teams endpoint requires at least one parameter")
                return None
                
            response = await self.client.get(
                f"{self.base_url}/teams",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return TeamsResponse(**data)
            
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch teams", params=params, error=str(e))
            return None
        
    async def get_team_statistics(
        self,
        league: int,
        season: str,
        team: int,
        date: Optional[str] = None
    ) -> Optional[StatisticsResponse]:
        """Получение статистики команды за сезон"""
        try:
            params = {
                "league": league,
                "season": season,
                "team": team
            }
            if date:
                params["date"] = date
                
            response = await self.client.get(
                f"{self.base_url}/statistics",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            # Логируем ответ для отладки
            logger.info("Statistics API response", results=data.get('results'), has_errors=bool(data.get('errors')))
            
            return StatisticsResponse(**data)
            
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch team statistics", params=params, error=str(e))
            return None

    async def get_players(
        self,
        player_id: Optional[int] = None,
        team: Optional[int] = None,
        season: Optional[str] = None,
        search: Optional[str] = None
    ) -> Optional[PlayersResponse]:
        """Получение данных об игроках с фильтрацией"""
        try:
            params = {}
            if player_id:
                params["id"] = player_id
            if team:
                params["team"] = team
            if season:
                params["season"] = season
            if search:
                params["search"] = search
            
            # Проверяем, что есть хотя бы один параметр
            if not params:
                logger.warning("Players endpoint requires at least one parameter")
                return None
                
            response = await self.client.get(
                f"{self.base_url}/players",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return PlayersResponse(**data)
            
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch players", params=params, error=str(e))
            return None

    async def get_games(
        self,
        game_id: Optional[int] = None,
        date: Optional[str] = None,
        league: Optional[int] = None,
        season: Optional[str] = None,
        team: Optional[int] = None,
        timezone: Optional[str] = None
    ) -> Optional[GamesResponse]:
        """Получение данных о матчах с фильтрацией"""
        try:
            params = {}
            if game_id:
                params["id"] = game_id
            if date:
                params["date"] = date
            if league:
                params["league"] = league
                # Если указана лига, сезон становится обязательным
                if not season:
                    logger.error("Season parameter is required when using league filter")
                    return None
            if season:
                params["season"] = season
            if team:
                params["team"] = team
            if timezone:
                params["timezone"] = timezone
            
            # Проверяем, что есть хотя бы один параметр
            if not params:
                logger.warning("Games endpoint requires at least one parameter")
                return None
                
            response = await self.client.get(
                f"{self.base_url}/games",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return GamesResponse(**data)
            
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch games", params=params, error=str(e))
            return None

    async def get_teams_statistics(
        self,
        game_id: Optional[str] = None,
        game_ids: Optional[str] = None
    ) -> Optional[TeamsStatisticsResponse]:
        """Получение статистики команд по играм"""
        try:
            params = {}
            if game_id:
                params["id"] = game_id
            if game_ids:
                params["ids"] = game_ids
            
            # Проверяем, что есть хотя бы один параметр
            if not params:
                logger.warning("Teams statistics endpoint requires at least one parameter")
                return None
            
            # Проверяем максимальное количество игр (20)
            if game_ids:
                ids_count = len(game_ids.split('-'))
                if ids_count > 20:
                    logger.error(f"Maximum 20 game ids allowed, got {ids_count}")
                    return None
                
            response = await self.client.get(
                f"{self.base_url}/games/statistics/teams",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return TeamsStatisticsResponse(**data)
            
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch teams statistics", params=params, error=str(e))
            return None

    async def get_players_statistics(
        self,
        game_id: Optional[str] = None,
        game_ids: Optional[str] = None,
        player: Optional[int] = None,
        season: Optional[str] = None
    ) -> Optional[PlayersStatisticsResponse]:
        """Получение статистики игроков по играм"""
        try:
            params = {}
            if game_id:
                params["id"] = game_id
            if game_ids:
                params["ids"] = game_ids
            if player:
                params["player"] = player
            if season:
                params["season"] = season
            
            # Проверяем, что есть хотя бы один параметр
            if not params:
                logger.warning("Players statistics endpoint requires at least one parameter")
                return None
            
            # Проверяем максимальное количество игр (20)
            if game_ids:
                ids_count = len(game_ids.split('-'))
                if ids_count > 20:
                    logger.error(f"Maximum 20 game ids allowed, got {ids_count}")
                    return None
            
            # Если указан player, season становится обязательным
            if player and not season:
                logger.error("Season parameter is required when using player filter")
                return None
                
            response = await self.client.get(
                f"{self.base_url}/games/statistics/players",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return PlayersStatisticsResponse(**data)
            
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch players statistics", params=params, error=str(e))
            return None

    async def get_head_to_head(
        self,
        team1_id: int,
        team2_id: int,
        date: Optional[str] = None,
        league: Optional[int] = None,
        season: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> Optional[GamesResponse]:
        """Получение истории встреч между двумя командами"""
        try:
            params = {
                "h2h": f"{team1_id}-{team2_id}"
            }
            
            if date:
                params["date"] = date
            if league:
                params["league"] = league
            if season:
                params["season"] = season
            if timezone:
                params["timezone"] = timezone
                
            response = await self.client.get(
                f"{self.base_url}/games",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return GamesResponse(**data)
            
        except (httpx.HTTPError, Exception) as e:
            logger.error("Failed to fetch head-to-head statistics", params=params, error=str(e))
            return None

    async def close(self):
        """Закрытие клиента"""
        await self.client.aclose()