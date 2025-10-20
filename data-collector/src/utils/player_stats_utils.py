from typing import List, Dict, Any, Optional, Tuple
from models.basketball_models import PlayerGameStats

def get_player_stats_by_game(statistics: List[PlayerGameStats], game_id: int) -> List[PlayerGameStats]:
    """Получение статистики игроков по конкретной игре"""
    return [stats for stats in statistics if stats.game['id'] == game_id]

def get_player_stats_by_player(statistics: List[PlayerGameStats], player_id: int) -> List[PlayerGameStats]:
    """Получение статистики конкретного игрока по всем играм"""
    return [stats for stats in statistics if stats.player['id'] == player_id]

def get_player_stats_by_team(statistics: List[PlayerGameStats], team_id: int) -> List[PlayerGameStats]:
    """Получение статистики игроков конкретной команды"""
    return [stats for stats in statistics if stats.team['id'] == team_id]

def minutes_to_float(minutes_str: str) -> float:
    """Конвертация строки минут (MM:SS) в float"""
    if not minutes_str or minutes_str == "00:00":
        return 0.0
    try:
        parts = minutes_str.split(':')
        minutes = int(parts[0])
        seconds = int(parts[1]) if len(parts) > 1 else 0
        return minutes + seconds / 60.0
    except (ValueError, IndexError):
        return 0.0

def calculate_player_efficiency(stats: PlayerGameStats) -> Dict[str, Any]:
    """Расчет эффективности игрока в игре"""
    # Конвертация минут
    minutes_played = minutes_to_float(stats.minutes)
    
    # Расчет процентов бросков (обработка null)
    fg_percentage = stats.field_goals.percentage or 0
    three_pt_percentage = stats.threepoint_goals.percentage or 0
    ft_percentage = stats.freethrows_goals.percentage or 0
    
    # Эффективность бросков
    fg_eff = fg_percentage / 100.0 if fg_percentage else 0
    three_pt_eff = three_pt_percentage / 100.0 if three_pt_percentage else 0
    ft_eff = ft_percentage / 100.0 if ft_percentage else 0
    
    # Показатель эффективности за минуту
    if minutes_played > 0:
        per_minute_stats = {
            "points_per_minute": stats.points / minutes_played,
            "rebounds_per_minute": stats.rebounds['total'] / minutes_played,
            "assists_per_minute": stats.assists / minutes_played,
        }
    else:
        per_minute_stats = {
            "points_per_minute": 0,
            "rebounds_per_minute": 0,
            "assists_per_minute": 0,
        }
    
    # Общий рейтинг эффективности (упрощенный)
    efficiency_rating = (
        stats.points +
        stats.rebounds['total'] +
        stats.assists +
        (stats.field_goals.total * fg_eff) +
        (stats.threepoint_goals.total * three_pt_eff * 1.5)  # Бонус за 3-очковые
    )
    
    return {
        "player_id": stats.player['id'],
        "player_name": stats.player['name'],
        "game_id": stats.game['id'],
        "minutes_played": minutes_played,
        "shooting_efficiency": {
            "field_goals": fg_eff,
            "three_point": three_pt_eff,
            "free_throws": ft_eff
        },
        "per_minute_stats": per_minute_stats,
        "efficiency_rating": efficiency_rating,
        "efficiency_per_minute": efficiency_rating / minutes_played if minutes_played > 0 else 0
    }

def analyze_team_lineup(statistics: List[PlayerGameStats], game_id: int, team_id: int) -> Dict[str, Any]:
    """Анализ состава команды в игре"""
    team_stats = [stats for stats in statistics if stats.game['id'] == game_id and stats.team['id'] == team_id]
    
    starters = [stats for stats in team_stats if stats.type == "starters"]
    bench = [stats for stats in team_stats if stats.type == "bench"]
    
    # Эффективность стартового состава
    starters_efficiency = [calculate_player_efficiency(stats) for stats in starters]
    bench_efficiency = [calculate_player_efficiency(stats) for stats in bench]
    
    # Общая статистика команды
    total_minutes = sum(minutes_to_float(stats.minutes) for stats in team_stats)
    total_points = sum(stats.points for stats in team_stats)
    total_rebounds = sum(stats.rebounds['total'] for stats in team_stats)
    total_assists = sum(stats.assists for stats in team_stats)
    
    return {
        "game_id": game_id,
        "team_id": team_id,
        "starters": {
            "players": starters_efficiency,
            "total_efficiency": sum(player["efficiency_rating"] for player in starters_efficiency),
            "average_efficiency": sum(player["efficiency_rating"] for player in starters_efficiency) / len(starters_efficiency) if starters_efficiency else 0
        },
        "bench": {
            "players": bench_efficiency,
            "total_efficiency": sum(player["efficiency_rating"] for player in bench_efficiency),
            "average_efficiency": sum(player["efficiency_rating"] for player in bench_efficiency) / len(bench_efficiency) if bench_efficiency else 0
        },
        "team_totals": {
            "total_minutes": total_minutes,
            "total_points": total_points,
            "total_rebounds": total_rebounds,
            "total_assists": total_assists,
            "points_per_minute": total_points / total_minutes if total_minutes > 0 else 0
        }
    }

def calculate_player_season_averages(statistics: List[PlayerGameStats], player_id: int) -> Dict[str, Any]:
    """Расчет средних показателей игрока за сезон"""
    player_stats = get_player_stats_by_player(statistics, player_id)
    
    if not player_stats:
        return {"error": "No statistics found for player"}
    
    total_games = len(player_stats)
    total_minutes = sum(minutes_to_float(stats.minutes) for stats in player_stats)
    total_points = sum(stats.points for stats in player_stats)
    total_rebounds = sum(stats.rebounds['total'] for stats in player_stats)
    total_assists = sum(stats.assists for stats in player_stats)
    total_field_goals_made = sum(stats.field_goals.total for stats in player_stats)
    total_field_goals_attempted = sum(stats.field_goals.attempts for stats in player_stats)
    total_three_points_made = sum(stats.threepoint_goals.total for stats in player_stats)
    total_three_points_attempted = sum(stats.threepoint_goals.attempts for stats in player_stats)
    total_free_throws_made = sum(stats.freethrows_goals.total for stats in player_stats)
    total_free_throws_attempted = sum(stats.freethrows_goals.attempts for stats in player_stats)
    
    # Расчет средних значений
    averages = {
        "player_id": player_id,
        "player_name": player_stats[0].player['name'] if player_stats else "Unknown",
        "games_played": total_games,
        "minutes_per_game": total_minutes / total_games if total_games > 0 else 0,
        "points_per_game": total_points / total_games if total_games > 0 else 0,
        "rebounds_per_game": total_rebounds / total_games if total_games > 0 else 0,
        "assists_per_game": total_assists / total_games if total_games > 0 else 0,
        "field_goal_percentage": (total_field_goals_made / total_field_goals_attempted * 100) if total_field_goals_attempted > 0 else 0,
        "three_point_percentage": (total_three_points_made / total_three_points_attempted * 100) if total_three_points_attempted > 0 else 0,
        "free_throw_percentage": (total_free_throws_made / total_free_throws_attempted * 100) if total_free_throws_attempted > 0 else 0,
    }
    
    return averages

def find_top_performers(statistics: List[PlayerGameStats], metric: str = "points", limit: int = 5) -> List[Dict[str, Any]]:
    """Поиск лучших исполнителей по указанному показателю"""
    performers = []
    
    for stats in statistics:
        efficiency = calculate_player_efficiency(stats)
        
        if metric == "points":
            value = stats.points
        elif metric == "rebounds":
            value = stats.rebounds['total']
        elif metric == "assists":
            value = stats.assists
        elif metric == "efficiency":
            value = efficiency["efficiency_rating"]
        else:
            value = stats.points
        
        performers.append({
            "player_id": stats.player['id'],
            "player_name": stats.player['name'],
            "team_id": stats.team['id'],
            "game_id": stats.game['id'],
            "value": value,
            "efficiency": efficiency
        })
    
    # Сортировка по убыванию значения
    performers.sort(key=lambda x: x["value"], reverse=True)
    return performers[:limit]