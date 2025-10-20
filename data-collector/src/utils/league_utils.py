from typing import List, Optional
from models.basketball_models import League, Season

def get_leagues_with_full_stats(leagues: List[League], season: Optional[str] = None) -> List[League]:
    """Получение лиг с полной статистикой coverage"""
    filtered_leagues = []
    
    for league in leagues:
        # Фильтруем сезоны по coverage
        valid_seasons = []
        for season_data in league.seasons:
            coverage = season_data.coverage
            has_full_stats = (
                coverage.games and 
                coverage.games.statistics and 
                coverage.games.statistics.teams and 
                coverage.games.statistics.players
            )
            
            # Дополнительная фильтрация по сезону если указан
            if has_full_stats and (not season or season_data.season == season):
                valid_seasons.append(season_data)
        
        if valid_seasons:
            league_copy = league.model_copy()
            league_copy.seasons = valid_seasons
            filtered_leagues.append(league_copy)
    
    return filtered_leagues

def get_league_by_id(leagues: List[League], league_id: int) -> Optional[League]:
    """Поиск лиги по ID"""
    return next((league for league in leagues if league.id == league_id), None)

def get_leagues_by_country(leagues: List[League], country_code: str) -> List[League]:
    """Получение лиг по коду страны"""
    return [league for league in leagues if league.country.code == country_code.upper()]

def get_available_seasons(leagues: List[League]) -> List[str]:
    """Получение всех доступных сезонов из лиг"""
    seasons = set()
    for league in leagues:
        for season_data in league.seasons:
            seasons.add(season_data.season)
    return sorted(list(seasons))