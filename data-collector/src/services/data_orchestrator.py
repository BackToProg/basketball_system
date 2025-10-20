import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from structlog import get_logger

from storage.repositories import repositories
from api.basketball_api import BasketballAPI
from storage.database import League, Season, Team

logger = get_logger()

class DataOrchestrator:
    def __init__(self, api_client: BasketballAPI):
        self.api_client = api_client
        self.is_running = False

    async def start_collection(self):
        """Запуск сбора данных"""
        if self.is_running:
            logger.warning("Data collection is already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting data collection")
        
        try:
            # Сбор исторических данных при первом запуске
            await self.collect_historical_data()
            
            # Запуск периодического сбора
            while self.is_running:
                await self.collect_live_data()
                await asyncio.sleep(60)  # Ждем 60 секунд между итерациями
                
        except Exception as e:
            logger.error("Data collection failed", error=str(e))
            self.is_running = False
            raise

    async def stop_collection(self):
        """Остановка сбора данных"""
        self.is_running = False
        logger.info("🛑 Stopping data collection")

    async def collect_historical_data(self):
        """Сбор исторических данных (лиги, команды, сезоны)"""
        logger.info("📚 Starting historical data collection")
        
        try:
            # 1. Получаем и сохраняем лиги с полной статистикой
            leagues_count = await self._collect_leagues()
            logger.info(f"✅ Leagues collected: {leagues_count}")
            
            # 2. Получаем команды для основных лиг
            teams_count = await self._collect_teams()
            logger.info(f"✅ Teams collected: {teams_count}")
            
            logger.info("🎉 Historical data collection completed")
            
        except Exception as e:
            logger.error("Historical data collection failed", error=str(e))
            raise

    async def collect_live_data(self):
        """Сбор лайв-данных"""
        logger.info("🎯 Collecting live data")
        
        try:
            # 1. Обновляем лайв-игры
            games_count = await self._update_live_games()
            logger.info(f"✅ Live games updated: {games_count}")
            
            # 2. Собираем статистику для активных игр
            stats_count = await self._collect_live_statistics()
            logger.info(f"✅ Live statistics collected: {stats_count}")
            
        except Exception as e:
            logger.error("Live data collection failed", error=str(e))

    async def _collect_leagues(self) -> int:
        """Сбор и сохранение лиг"""
        logger.info("🏀 Collecting leagues data")
        
        # Получаем доступные сезоны
        seasons_response = await self.api_client.get_seasons()
        if not seasons_response:
            logger.warning("❌ No seasons data available from API")
            return 0
        
        logger.info(f"📅 Available seasons from API: {len(seasons_response.response)}")
        logger.info(f"📅 Seasons sample: {seasons_response.response[:5]}")  # Покажем первые 5 сезонов
        
        # Берем подходящий сезон для бесплатного тарифа
        available_season = self._get_latest_season(seasons_response.response)
        logger.info(f"🎯 Using season for free plan: {available_season}")
        
        # Получаем все лиги для этого сезона
        logger.info(f"🔍 Fetching leagues for season: {available_season}")
        leagues_response = await self.api_client.get_leagues(season=available_season)
        
        if not leagues_response:
            logger.warning("❌ No leagues data available from API")
            return 0
        
        logger.info(f"🏆 Found {leagues_response.results} leagues in API")
        logger.info(f"🏆 API response: {leagues_response}")  # Отладим полный ответ
        
        # Проверим структуру response
        if hasattr(leagues_response, 'response'):
            leagues_list = leagues_response.response
            logger.info(f"📊 Leagues response type: {type(leagues_list)}")
            if leagues_list:
                logger.info(f"📊 First league sample: {leagues_list[0]}")
        else:
            logger.warning("❌ No 'response' attribute in leagues response")
            return 0
        
        leagues_saved = 0
        for league_data in leagues_list:
            try:
                # Сохраняем лигу
                league_saved = await self._save_league(league_data)
                if league_saved:
                    leagues_saved += 1
                    
            except Exception as e:
                logger.error("❌ Failed to save league", 
                        league_id=getattr(league_data, 'id', 'unknown'),
                        league_name=getattr(league_data, 'name', 'unknown'),
                        error=str(e))
        
        logger.info(f"💾 Successfully saved {leagues_saved} leagues to database")
        return leagues_saved

    async def _save_league(self, league_data) -> bool:
        """Сохранение одной лиги в БД"""
        try:
            # Извлекаем данные страны
            country_data = getattr(league_data, 'country', {})
            country_name = getattr(country_data, 'name', '') if country_data else ''
            country_code = getattr(country_data, 'code', '') if country_data else ''
            country_flag = getattr(country_data, 'flag', '') if country_data else ''
            
            # Сохраняем лигу
            league, created = await repositories.leagues.get_or_create(
                id=league_data.id,
                defaults={
                    'name': league_data.name,
                    'type': league_data.type,
                    'logo': league_data.logo or '',
                    'country_name': country_name,
                    'country_code': country_code,
                    'country_flag': country_flag
                }
            )
            
            # Сохраняем сезоны лиги
            seasons_data = getattr(league_data, 'seasons', [])
            seasons_saved = await self._save_league_seasons(league, seasons_data)
            
            action = "created" if created else "updated"
            logger.info(f"✅ League {action}: {league.name} (ID: {league.id}), seasons: {seasons_saved}")
            return True
            
        except Exception as e:
            logger.error("❌ Failed to save league", 
                       league_id=getattr(league_data, 'id', 'unknown'),
                       error=str(e))
            return False

    async def _save_league_seasons(self, league: League, seasons_data: List) -> int:
        """Сохранение сезонов для лиги"""
        seasons_saved = 0
        
        for season_data in seasons_data:
            try:
                # Проверяем coverage статистики
                coverage = getattr(season_data, 'coverage', None)
                has_full_stats = (
                    coverage and 
                    getattr(coverage, 'games', None) and 
                    getattr(coverage.games, 'statistics', None) and
                    getattr(coverage.games.statistics, 'teams', False) and
                    getattr(coverage.games.statistics, 'players', False)
                )
                
                # Парсим даты
                start_date = None
                end_date = None
                try:
                    start_str = getattr(season_data, 'start', None)
                    end_str = getattr(season_data, 'end', None)
                    
                    if start_str:
                        start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    if end_str:
                        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    logger.warning(f"⚠️ Failed to parse dates for season {getattr(season_data, 'season', 'unknown')}", 
                                 error=str(e))
                
                # Сохраняем сезон
                season, created = await repositories.seasons.get_or_create(
                    league_id=league.id,
                    season=season_data.season,
                    defaults={
                        'start_date': start_date,
                        'end_date': end_date,
                        'has_teams_stats': has_full_stats,
                        'has_players_stats': has_full_stats,
                        'has_standings': getattr(coverage, 'standings', False) if coverage else False,
                        'has_odds': getattr(coverage, 'odds', False) if coverage else False
                    }
                )
                
                seasons_saved += 1
                
            except Exception as e:
                logger.error("❌ Failed to save season", 
                           league_id=league.id,
                           season=getattr(season_data, 'season', 'unknown'),
                           error=str(e))
        
        return seasons_saved

    async def _collect_teams(self) -> int:
        """Сбор команд для основных лиг"""
        logger.info("👥 Collecting teams data")
        
        # Основные лиги для сбора команд
        main_leagues = [
            {"id": 12, "name": "NBA"},      # NBA
            {"id": 13, "name": "Euroleague"} # Euroleague
        ]
        
        total_teams_saved = 0
        
        for league_info in main_leagues:
            try:
                league_id = league_info["id"]
                league_name = league_info["name"]
                
                logger.info(f"🔍 Collecting teams for {league_name} (ID: {league_id})")
                
                # Получаем последний сезон лиги из БД
                seasons = await repositories.seasons.get_seasons_by_league(league_id)
                if not seasons:
                    logger.warning(f"⚠️ No seasons found for league {league_name}")
                    continue
                
                # Берем самый свежий сезон
                latest_season = max(seasons, key=lambda s: s.season)
                logger.info(f"📅 Using season: {latest_season.season} for {league_name}")
                
                # Получаем команды лиги из API
                teams_response = await self.api_client.get_teams(
                    league=league_id, 
                    season=latest_season.season
                )
                
                if not teams_response or not teams_response.response:
                    logger.warning(f"⚠️ No teams data for {league_name} season {latest_season.season}")
                    continue
                
                # Сохраняем команды
                teams_saved = 0
                for team_data in teams_response.response:
                    if await self._save_team(team_data):
                        teams_saved += 1
                
                total_teams_saved += teams_saved
                logger.info(f"✅ Saved {teams_saved} teams for {league_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to collect teams for league {league_info['name']}", 
                           error=str(e))
        
        logger.info(f"💾 Total teams saved: {total_teams_saved}")
        return total_teams_saved

    async def _save_team(self, team_data) -> bool:
        """Сохранение одной команды в БД"""
        try:
            # Извлекаем данные страны
            country_data = getattr(team_data, 'country', {})
            country_name = getattr(country_data, 'name', '') if country_data else ''
            country_code = getattr(country_data, 'code', '') if country_data else ''
            country_flag = getattr(country_data, 'flag', '') if country_data else ''
            
            # Сохраняем команду
            team, created = await repositories.teams.get_or_create(
                id=team_data.id,
                defaults={
                    'name': team_data.name,
                    'country': country_name,
                    'code': country_code,
                    'logo': team_data.logo or '',
                    'national': getattr(team_data, 'nationnal', False)
                }
            )
            
            action = "created" if created else "updated"
            logger.debug(f"✅ Team {action}: {team.name} (ID: {team.id})")
            return True
            
        except Exception as e:
            logger.error("❌ Failed to save team", 
                       team_id=getattr(team_data, 'id', 'unknown'),
                       error=str(e))
            return False

    async def _update_live_games(self) -> int:
        """Обновление лайв-игр"""
        logger.info("🔄 Updating live games")
        
        try:
            # Получаем лайв-игры из API
            games_response = await self.api_client.get_games(live=True)
            if not games_response or not games_response.response:
                logger.info("📭 No live games found")
                return 0
            
            games_updated = 0
            for game_data in games_response.response:
                if await self._save_game(game_data):
                    games_updated += 1
            
            logger.info(f"✅ Live games updated: {games_updated}")
            return games_updated
            
        except Exception as e:
            logger.error("❌ Failed to update live games", error=str(e))
            return 0

    async def _save_game(self, game_data) -> bool:
        """Сохранение игры в БД"""
        try:
            # TODO: Реализовать полное сохранение игр
            # Сейчас просто логируем для отладки
            home_team = getattr(game_data.teams, 'home', {})
            away_team = getattr(game_data.teams, 'away', {})
            
            logger.debug(f"🎯 Game found: {getattr(home_team, 'name', 'Unknown')} vs {getattr(away_team, 'name', 'Unknown')} "
                        f"(Status: {getattr(game_data.status, 'short', 'Unknown')})")
            
            return True
            
        except Exception as e:
            logger.error("❌ Failed to save game", 
                       game_id=getattr(game_data, 'id', 'unknown'),
                       error=str(e))
            return False

    async def _collect_live_statistics(self) -> int:
        """Сбор статистики для активных игр"""
        logger.info("📊 Collecting live statistics")
        
        try:
            # Получаем активные игры из БД
            live_games = await repositories.games.get_live_games()
            
            stats_collected = 0
            for game in live_games:
                if await self._collect_game_statistics(game.id):
                    stats_collected += 1
            
            logger.info(f"✅ Live statistics collected for {stats_collected} games")
            return stats_collected
            
        except Exception as e:
            logger.error("❌ Failed to collect live statistics", error=str(e))
            return 0

    async def _collect_game_statistics(self, game_id: int) -> bool:
        """Сбор статистики для конкретной игры"""
        try:
            # TODO: Реализовать сбор и сохранение статистики
            logger.debug(f"📈 Collecting statistics for game {game_id}")
            return True
            
        except Exception as e:
            logger.error("❌ Failed to collect game statistics", game_id=game_id, error=str(e))
            return False

    def _get_latest_season(self, seasons: List) -> str:
        """Получение самого актуального сезона с данными для бесплатного тарифа"""
        try:
            # Фильтруем только строковые сезоны формата "YYYY-YYYY"
            string_seasons = [s for s in seasons if isinstance(s, str) and '-' in s]
            if not string_seasons:
                logger.warning("⚠️ No valid season strings found, using fallback")
                return "2023-2024"
            
            # Для бесплатного тарифа используем сезоны 2023-2024 или 2022-2023
            # так как свежие сезоны могут быть недоступны
            available_seasons = [
                "2023-2024",  # Самый свежий доступный
                "2022-2023",  # Прошлый сезон (точно есть данные)
                "2021-2022"   # Запасной вариант
            ]
            
            # Ищем первый доступный сезон из нашего списка
            for season in available_seasons:
                if season in string_seasons:
                    logger.info(f"🎯 Using available season for free plan: {season}")
                    return season
            
            # Если ни один из ожидаемых сезонов не найден, берем самый последний из доступных
            string_seasons.sort(reverse=True)
            fallback_season = string_seasons[0]
            logger.warning(f"⚠️ No preferred seasons found, using fallback: {fallback_season}")
            return fallback_season
            
        except Exception as e:
            logger.error("❌ Failed to determine latest season", error=str(e))
            return "2023-2024"  # Надежный fallback