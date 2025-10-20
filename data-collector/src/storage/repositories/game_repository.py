from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from storage.database import Game, Team, League, Odds, db_manager
from storage.repositories.async_base import AsyncBaseRepository

class GameRepository(AsyncBaseRepository[Game]):
    def __init__(self):
        super().__init__(Game)

    async def get_by_api_id(self, api_id: int) -> Optional[Game]:
        """Получение игры по API ID"""
        return await self.get_by_id(api_id)

    async def get_games_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Game]:
        """Получение игр за период дат"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Game).filter(
                    Game.date >= start_date,
                    Game.date <= end_date
                )
            )
            return result.scalars().all()

    async def get_games_by_league_and_season(self, league_id: int, season_id: int) -> List[Game]:
        """Получение игр лиги за сезон"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Game).filter(
                    Game.league_id == league_id,
                    Game.season_id == season_id
                )
            )
            return result.scalars().all()

    async def get_games_by_team(self, team_id: int, season_id: Optional[int] = None) -> List[Game]:
        """Получение игр команды"""
        query = select(Game).filter(
            or_(Game.home_team_id == team_id, Game.away_team_id == team_id)
        )
        
        if season_id:
            query = query.filter(Game.season_id == season_id)
        
        async with db_manager.get_async_session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def get_head_to_head(self, team1_id: int, team2_id: int, season_id: Optional[int] = None) -> List[Game]:
        """Получение истории встреч между двумя командами"""
        query = select(Game).filter(
            or_(
                and_(Game.home_team_id == team1_id, Game.away_team_id == team2_id),
                and_(Game.home_team_id == team2_id, Game.away_team_id == team1_id)
            )
        )
        
        if season_id:
            query = query.filter(Game.season_id == season_id)
        
        async with db_manager.get_async_session() as session:
            result = await session.execute(query.order_by(Game.date.desc()))
            return result.scalars().all()

    async def get_live_games(self) -> List[Game]:
        """Получение текущих лайв-игр"""
        live_statuses = ["Q1", "Q2", "Q3", "Q4", "OT", "BT", "HT"]
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Game).filter(Game.status.in_(live_statuses))
            )
            return result.scalars().all()

    async def get_upcoming_games(self, hours: int = 24) -> List[Game]:
        """Получение предстоящих игр"""
        now = datetime.now()
        future = now + timedelta(hours=hours)
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Game).filter(
                    Game.date >= now,
                    Game.date <= future,
                    Game.status == "NS"
                )
            )
            return result.scalars().all()

    async def get_recent_finished_games(self, days: int = 7) -> List[Game]:
        """Получение недавно завершенных игр"""
        since = datetime.now() - timedelta(days=days)
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Game).filter(
                    Game.date >= since,
                    Game.status.in_(["FT", "AOT"])
                )
            )
            return result.scalars().all()

    async def get_games_with_odds(self, bookmaker: str) -> List[Game]:
        """Получение игр с коэффициентами от указанного букмекера"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Game).join(Odds).filter(Odds.bookmaker == bookmaker)
            )
            return result.scalars().all()