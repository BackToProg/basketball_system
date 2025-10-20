from typing import List, Optional
from sqlalchemy import select, func
from storage.database import Player, PlayerGameStats, Team, Game, db_manager
from storage.repositories.async_base import AsyncBaseRepository

class PlayerRepository(AsyncBaseRepository[Player]):
    def __init__(self):
        super().__init__(Player)

    async def get_by_api_id(self, api_id: int) -> Optional[Player]:
        """Получение игрока по API ID"""
        return await self.get_by_id(api_id)

    async def get_players_by_team(self, team_id: int) -> List[Player]:
        """Получение игроков команды"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Player).join(PlayerGameStats).filter(
                    PlayerGameStats.team_id == team_id
                ).distinct()
            )
            return result.scalars().all()

    async def search_players(self, search_term: str) -> List[Player]:
        """Поиск игроков по имени"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(Player).filter(Player.name.ilike(f"%{search_term}%"))
            )
            return result.scalars().all()

class PlayerGameStatsRepository(AsyncBaseRepository[PlayerGameStats]):
    def __init__(self):
        super().__init__(PlayerGameStats)

    async def get_player_game_stats(self, player_id: int, game_id: int) -> Optional[PlayerGameStats]:
        """Получение статистики игрока в конкретной игре"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(PlayerGameStats).filter(
                    PlayerGameStats.player_id == player_id,
                    PlayerGameStats.game_id == game_id
                )
            )
            return result.scalar_one_or_none()

    async def get_player_season_stats(self, player_id: int, season_id: int) -> List[PlayerGameStats]:
        """Получение статистики игрока за сезон"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(PlayerGameStats).join(Game).filter(
                    PlayerGameStats.player_id == player_id,
                    Game.season_id == season_id
                )
            )
            return result.scalars().all()

    async def get_team_game_stats(self, team_id: int, game_id: int) -> List[PlayerGameStats]:
        """Получение статистики всех игроков команды в игре"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(PlayerGameStats).filter(
                    PlayerGameStats.team_id == team_id,
                    PlayerGameStats.game_id == game_id
                )
            )
            return result.scalars().all()

    async def get_top_scorers(self, season_id: int, limit: int = 10) -> List[dict]:
        """Получение лучших бомбардиров сезона"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(
                    PlayerGameStats.player_id,
                    Player.name,
                    PlayerGameStats.team_id,
                    Team.name.label('team_name'),
                    func.sum(PlayerGameStats.points).label('total_points'),
                    func.count(PlayerGameStats.game_id).label('games_played')
                ).join(Player).join(Team).join(Game).filter(
                    Game.season_id == season_id
                ).group_by(
                    PlayerGameStats.player_id,
                    Player.name,
                    PlayerGameStats.team_id,
                    Team.name
                ).order_by(func.sum(PlayerGameStats.points).desc()).limit(limit)
            )
            
            return [
                {
                    'player_id': row.player_id,
                    'player_name': row.name,
                    'team_id': row.team_id,
                    'team_name': row.team_name,
                    'total_points': row.total_points,
                    'games_played': row.games_played
                }
                for row in result
            ]