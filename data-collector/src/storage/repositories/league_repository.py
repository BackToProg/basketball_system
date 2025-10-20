from typing import List, Optional
from sqlalchemy import select
from storage.database import League, Season, db_manager
from storage.repositories.async_base import AsyncBaseRepository

class LeagueRepository(AsyncBaseRepository[League]):
    def __init__(self):
        super().__init__(League)

    async def get_by_api_id(self, api_id: int) -> Optional[League]:
        """Получение лиги по API ID"""
        return await self.get_by_id(api_id)

    async def get_leagues_with_stats_coverage(self, season: str) -> List[League]:
        """Получение лиг с coverage статистики для указанного сезона"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(League).join(Season).filter(
                    Season.season == season,
                    Season.has_teams_stats == True,
                    Season.has_players_stats == True
                )
            )
            return result.scalars().all()

class SeasonRepository(AsyncBaseRepository[Season]):
    def __init__(self):
        super().__init__(Season)

    async def get_by_league_and_season(self, league_id: int, season: str) -> Optional[Season]:
        """Получение сезона по лиге и названию сезона"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Season).filter(
                    Season.league_id == league_id,
                    Season.season == season
                )
            )
            return result.scalar_one_or_none()

    async def get_seasons_by_league(self, league_id: int) -> List[Season]:
        """Получение всех сезонов лиги"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Season).filter(Season.league_id == league_id)
            )
            return result.scalars().all()