from typing import List, Dict, Any, Optional
from models.basketball_models import TeamGameStats

def get_team_stats_by_game(statistics: List[TeamGameStats], game_id: int) -> List[TeamGameStats]:
    """Получение статистики команд по конкретной игре"""
    return [stats for stats in statistics if stats.game['id'] == game_id]

def get_team_stats_by_team(statistics: List[TeamGameStats], team_id: int) -> List[TeamGameStats]:
    """Получение статистики конкретной команды по всем играм"""
    return [stats for stats in statistics if stats.team['id'] == team_id]

def calculate_shooting_efficiency(stats: TeamGameStats) -> Dict[str, float]:
    """Расчет эффективности бросков"""
    fg_eff = stats.field_goals.percentage / 100.0
    three_pt_eff = stats.threepoint_goals.percentage / 100.0
    ft_eff = stats.freethrows_goals.percentage / 100.0
    
    # Общая эффективность (взвешенная)
    total_attempts = (stats.field_goals.attempts + stats.threepoint_goals.attempts)
    if total_attempts > 0:
        total_efficiency = (
            (stats.field_goals.total * fg_eff) + 
            (stats.threepoint_goals.total * three_pt_eff * 1.5)  # Вес для 3-очковых
        ) / total_attempts
    else:
        total_efficiency = 0
    
    return {
        "field_goal_efficiency": fg_eff,
        "three_point_efficiency": three_pt_eff,
        "free_throw_efficiency": ft_eff,
        "total_shooting_efficiency": total_efficiency
    }

def calculate_game_impact(stats: TeamGameStats) -> Dict[str, Any]:
    """Расчет общего влияния команды в игре"""
    # Эффективность бросков
    shooting_eff = calculate_shooting_efficiency(stats)
    
    # Эффективность подборов
    rebound_eff = stats.rebounds.total / (stats.rebounds.total + stats.rebounds.defense) if stats.rebounds.total > 0 else 0
    
    # Соотношение передач к потерям
    assist_to_turnover = stats.assists / stats.turnovers if stats.turnovers > 0 else stats.assists
    
    # Общий показатель эффективности
    efficiency_rating = (
        stats.field_goals.total +
        stats.threepoint_goals.total +
        stats.freethrows_goals.total +
        stats.rebounds.total +
        stats.assists +
        stats.steals +
        stats.blocks -
        stats.turnovers -
        stats.personal_fouls
    )
    
    return {
        "shooting_efficiency": shooting_eff["total_shooting_efficiency"],
        "rebound_efficiency": rebound_eff,
        "assist_to_turnover_ratio": assist_to_turnover,
        "steals_per_turnover": stats.steals / stats.turnovers if stats.turnovers > 0 else stats.steals,
        "efficiency_rating": efficiency_rating,
        "game_impact_score": efficiency_rating * shooting_eff["total_shooting_efficiency"]
    }

def compare_teams_in_game(statistics: List[TeamGameStats], game_id: int) -> Optional[Dict[str, Any]]:
    """Сравнение статистики двух команд в одной игре"""
    game_stats = get_team_stats_by_game(statistics, game_id)
    
    if len(game_stats) != 2:
        return None
    
    team1_stats = game_stats[0]
    team2_stats = game_stats[1]
    
    team1_impact = calculate_game_impact(team1_stats)
    team2_impact = calculate_game_impact(team2_stats)
    
    return {
        "game_id": game_id,
        "team1": {
            "team_id": team1_stats.team['id'],
            "stats": team1_stats.dict(),
            "impact": team1_impact
        },
        "team2": {
            "team_id": team2_stats.team['id'],
            "stats": team2_stats.dict(),
            "impact": team2_impact
        },
        "comparison": {
            "shooting_efficiency_diff": team1_impact["shooting_efficiency"] - team2_impact["shooting_efficiency"],
            "rebound_efficiency_diff": team1_impact["rebound_efficiency"] - team2_impact["rebound_efficiency"],
            "assist_turnover_ratio_diff": team1_impact["assist_to_turnover_ratio"] - team2_impact["assist_to_turnover_ratio"],
            "efficiency_rating_diff": team1_impact["efficiency_rating"] - team2_impact["efficiency_rating"]
        }
    }

def analyze_team_performance_trend(statistics: List[TeamGameStats], team_id: int) -> Dict[str, Any]:
    """Анализ трендов производительности команды"""
    team_stats = get_team_stats_by_team(statistics, team_id)
    
    if not team_stats:
        return {"error": "No statistics found for team"}
    
    # Сортируем по game_id (предполагая, что game_id увеличивается со временем)
    team_stats.sort(key=lambda x: x.game['id'])
    
    trends = []
    for stats in team_stats:
        impact = calculate_game_impact(stats)
        trends.append({
            "game_id": stats.game['id'],
            "shooting_efficiency": impact["shooting_efficiency"],
            "rebound_efficiency": impact["rebound_efficiency"],
            "assist_turnover_ratio": impact["assist_to_turnover_ratio"],
            "efficiency_rating": impact["efficiency_rating"]
        })
    
    # Расчет изменений
    if len(trends) > 1:
        first = trends[0]
        last = trends[-1]
        changes = {
            "shooting_efficiency_change": last["shooting_efficiency"] - first["shooting_efficiency"],
            "rebound_efficiency_change": last["rebound_efficiency"] - first["rebound_efficiency"],
            "assist_turnover_ratio_change": last["assist_turnover_ratio"] - first["assist_turnover_ratio"],
            "efficiency_rating_change": last["efficiency_rating"] - first["efficiency_rating"]
        }
    else:
        changes = {}
    
    return {
        "team_id": team_id,
        "games_analyzed": len(team_stats),
        "trends": trends,
        "changes": changes,
        "average_efficiency": sum(t["efficiency_rating"] for t in trends) / len(trends) if trends else 0
    }