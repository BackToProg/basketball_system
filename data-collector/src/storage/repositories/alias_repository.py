from typing import List, Optional, Dict
from sqlalchemy import select, and_, or_
from storage.database import TeamAlias, LeagueMapping, db_manager
from storage.repositories.async_base import AsyncBaseRepository

class TeamAliasRepository(AsyncBaseRepository[TeamAlias]):
    def __init__(self):
        super().__init__(TeamAlias)

    async def find_by_betcity_name(self, betcity_name: str) -> Optional[TeamAlias]:
        """Поиск алиаса по названию в Betcity"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(TeamAlias).filter(TeamAlias.betcity_name.ilike(betcity_name))
            )
            return result.scalar_one_or_none()

    async def find_by_team_id(self, team_id: int) -> List[TeamAlias]:
        """Поиск всех алиасов команды"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(TeamAlias).filter(TeamAlias.team_id == team_id)
            )
            return result.scalars().all()

    async def bulk_create_aliases(self, aliases_data: List[Dict]) -> List[TeamAlias]:
        """Массовое создание алиасов"""
        aliases = []
        for alias_data in aliases_data:
            alias = TeamAlias(**alias_data)
            aliases.append(alias)
        
        async with db_manager.get_async_session() as session:
            session.add_all(aliases)
            await session.commit()
            return aliases

class LeagueMappingRepository(AsyncBaseRepository[LeagueMapping]):
    def __init__(self):
        super().__init__(LeagueMapping)

    async def find_by_betcity_id(self, betcity_league_id: int) -> Optional[LeagueMapping]:
        """Поиск маппинга по ID лиги в Betcity"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(LeagueMapping).filter(LeagueMapping.betcity_league_id == betcity_league_id)
            )
            return result.scalar_one_or_none()

    async def find_by_league_id(self, league_id: int) -> Optional[LeagueMapping]:
        """Поиск маппинга по ID нашей лиги"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(LeagueMapping).filter(LeagueMapping.league_id == league_id)
            )
            return result.scalar_one_or_none()