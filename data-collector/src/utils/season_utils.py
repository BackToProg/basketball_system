from typing import List, Union

def get_latest_season(seasons: List[Union[int, str]]) -> str:
    """Получение самого актуального сезона"""
    # Фильтруем строковые сезоны (формат "2023-2024")
    string_seasons = [s for s in seasons if isinstance(s, str) and '-' in s]
    
    if not string_seasons:
        return None
    
    # Сортируем по убыванию (последний сезон первый)
    string_seasons.sort(reverse=True)
    return string_seasons[0]

def get_season_years(season: str) -> tuple[int, int]:
    """Извлечение годов из строки сезона"""
    if isinstance(season, str) and '-' in season:
        start_year, end_year = season.split('-')
        return int(start_year), int(end_year)
    return None, None

def is_current_season(season: str) -> bool:
    """Проверка, является ли сезон текущим"""
    from datetime import datetime
    current_year = datetime.now().year
    
    start_year, end_year = get_season_years(season)
    if start_year and end_year:
        return start_year <= current_year <= end_year
    return False