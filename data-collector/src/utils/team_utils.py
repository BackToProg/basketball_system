from typing import List, Optional, Dict
from models.basketball_models import Team

def find_team_by_id(teams: List[Team], team_id: int) -> Optional[Team]:
    """Поиск команды по ID"""
    return next((team for team in teams if team.id == team_id), None)

def find_teams_by_country(teams: List[Team], country_code: str) -> List[Team]:
    """Поиск команд по коду страны"""
    return [team for team in teams if team.country.code == country_code.upper()]

def find_teams_by_league(teams: List[Team], league_id: int) -> List[Team]:
    """Поиск команд по лиге (нужно передавать league параметр в API)"""
    return teams  # Фильтрация по лиге делается на уровне API

def get_nba_teams(teams: List[Team]) -> List[Team]:
    """Получение NBA команд (фильтр по стране USA)"""
    return [team for team in teams if team.country.code == "US"]

def group_teams_by_country(teams: List[Team]) -> Dict[str, List[Team]]:
    """Группировка команд по странам"""
    countries = {}
    for team in teams:
        country_name = team.country.name
        if country_name not in countries:
            countries[country_name] = []
        countries[country_name].append(team)
    return countries

def get_teams_with_logos(teams: List[Team]) -> List[Team]:
    """Получение только команд с логотипами"""
    return [team for team in teams if team.logo]