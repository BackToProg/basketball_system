from typing import List, Optional
from sqlalchemy import select, func
from storage.database import Team, TeamSeasonStats, db_manager
from storage.repositories.async_base import AsyncBaseRepository

class TeamRepository(AsyncBaseRepository[Team]):
    def __init__(self):
        super().__init__(Team)

    async def get_by_api_id(self, api_id: int) -> Optional[Team]:
        """Получение команды по API ID"""
        return await self.get_by_id(api_id)

    async def get_teams_by_country(self, country: str) -> List[Team]:
        """Получение команд по стране"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Team).filter(Team.country == country)
            )
            return result.scalars().all()

    async def get_teams_by_league(self, league_id: int, season: str) -> List[Team]:
        """Получение команд лиги (через статистику сезона)"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Team).join(TeamSeasonStats).filter(
                    TeamSeasonStats.league_id == league_id
                )
            )
            return result.scalars().all()

    async def search_teams(self, search_term: str) -> List[Team]:
        """Поиск команд по названию"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Team).filter(Team.name.ilike(f"%{search_term}%"))
            )
            return result.scalars().all()

class TeamSeasonStatsRepository(AsyncBaseRepository[TeamSeasonStats]):
    def __init__(self):
        super().__init__(TeamSeasonStats)

    async def get_team_season_stats(self, team_id: int, season_id: int) -> Optional[TeamSeasonStats]:
        """Получение статистики команды за сезон"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(TeamSeasonStats).filter(
                    TeamSeasonStats.team_id == team_id,
                    TeamSeasonStats.season_id == season_id
                )
            )
            return result.scalar_one_or_none()

    async def get_league_standings(self, league_id: int, season_id: int) -> List[TeamSeasonStats]:
        """Получение таблицы лиги за сезон"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(TeamSeasonStats).filter(
                    TeamSeasonStats.league_id == league_id,
                    TeamSeasonStats.season_id == season_id
                ).order_by(TeamSeasonStats.win_percentage_total.desc())
            )
            return result.scalars().all()