from typing import Any, List, Optional, Dict
from models.basketball_models import Player

def find_player_by_id(players: List[Player], player_id: int) -> Optional[Player]:
    """Поиск игрока по ID"""
    return next((player for player in players if player.id == player_id), None)

def find_players_by_team(players: List[Player], team_id: int) -> List[Player]:
    """Поиск игроков по команде (нужно передавать team параметр в API)"""
    return players  # Фильтрация по команде делается на уровне API

def find_players_by_position(players: List[Player], position: str) -> List[Player]:
    """Фильтрация игроков по позиции"""
    position_lower = position.lower()
    return [player for player in players if player.position and player.position.lower() == position_lower]

def find_players_by_country(players: List[Player], country: str) -> List[Player]:
    """Фильтрация игроков по стране"""
    country_lower = country.lower()
    return [player for player in players if player.country and player.country.lower() == country_lower]

def group_players_by_position(players: List[Player]) -> Dict[str, List[Player]]:
    """Группировка игроков по позициям"""
    positions = {}
    for player in players:
        position = player.position or "Unknown"
        if position not in positions:
            positions[position] = []
        positions[position].append(player)
    return positions

def get_players_with_numbers(players: List[Player]) -> List[Player]:
    """Получение только игроков с номерами"""
    return [player for player in players if player.number]

def get_players_by_age_range(players: List[Player], min_age: int, max_age: int) -> List[Player]:
    """Фильтрация игроков по возрастному диапазону"""
    return [player for player in players if player.age and min_age <= player.age <= max_age]

def calculate_average_age(players: List[Player]) -> Optional[float]:
    """Расчет среднего возраста команды"""
    ages = [player.age for player in players if player.age is not None]
    if ages:
        return sum(ages) / len(ages)
    return None

def get_team_roster_stats(players: List[Player]) -> Dict[str, Any]:
    """Статистика состава команды"""
    positions_count = {}
    countries_count = {}
    ages = []
    
    for player in players:
        # Подсчет позиций
        position = player.position or "Unknown"
        positions_count[position] = positions_count.get(position, 0) + 1
        
        # Подсчет стран
        country = player.country or "Unknown"
        countries_count[country] = countries_count.get(country, 0) + 1
        
        # Сбор возрастов
        if player.age:
            ages.append(player.age)
    
    return {
        "total_players": len(players),
        "positions_distribution": positions_count,
        "countries_distribution": countries_count,
        "average_age": sum(ages) / len(ages) if ages else None,
        "youngest_player": min(ages) if ages else None,
        "oldest_player": max(ages) if ages else None
    }