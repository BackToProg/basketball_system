from .league_repository import LeagueRepository, SeasonRepository
from .team_repository import TeamRepository, TeamSeasonStatsRepository
from .game_repository import GameRepository
from .player_repository import PlayerRepository, PlayerGameStatsRepository

class AsyncRepositoryFacade:
    """Асинхронный фасад для работы со всеми репозиториями"""
    
    def __init__(self):
        self.leagues = LeagueRepository()
        self.seasons = SeasonRepository()
        self.teams = TeamRepository()
        self.team_stats = TeamSeasonStatsRepository()
        self.games = GameRepository()
        self.players = PlayerRepository()
        self.player_stats = PlayerGameStatsRepository()

# Создаем глобальный экземпляр фасада
repositories = AsyncRepositoryFacade()