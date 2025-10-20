from typing import Dict, Any, Optional
from models.basketball_models import TeamStatistics

def calculate_team_strength(stats: TeamStatistics) -> Dict[str, Any]:
    """Расчет силы команды на основе статистики"""
    games = stats.games
    points = stats.points
    
    # Общий винрейт
    win_rate = float(games.wins.all.percentage)
    
    # Среднее количество очков за игру
    points_for_avg = float(points.for_.average.all)
    points_against_avg = float(points.against.average.all)
    
    # Разница очков (показатель доминирования)
    point_differential = points_for_avg - points_against_avg
    
    # Эффективность дома и на выезде
    home_win_rate = float(games.wins.home.percentage)
    away_win_rate = float(games.wins.away.percentage)
    
    return {
        "team_name": stats.team.name,
        "win_rate": win_rate,
        "points_for_avg": points_for_avg,
        "points_against_avg": points_against_avg,
        "point_differential": point_differential,
        "home_win_rate": home_win_rate,
        "away_win_rate": away_win_rate,
        "home_advantage": home_win_rate - away_win_rate,
        "total_games": games.played.all
    }

def compare_teams_stats(stats1: TeamStatistics, stats2: TeamStatistics) -> Dict[str, Any]:
    """Сравнение статистики двух команд"""
    strength1 = calculate_team_strength(stats1)
    strength2 = calculate_team_strength(stats2)
    
    return {
        "team1": strength1,
        "team2": strength2,
        "comparison": {
            "win_rate_difference": strength1["win_rate"] - strength2["win_rate"],
            "point_differential_difference": strength1["point_differential"] - strength2["point_differential"],
            "home_advantage_difference": strength1["home_advantage"] - strength2["home_advantage"]
        }
    }

def get_team_form(stats: TeamStatistics, last_n_games: int = 10) -> Dict[str, Any]:
    """Анализ формы команды (упрощенно)"""
    # В реальном приложении здесь был бы анализ последних игр
    # Сейчас используем общую статистику как индикатор формы
    
    recent_performance = {
        "win_rate": float(stats.games.wins.all.percentage),
        "points_for_avg": float(stats.points.for_.average.all),
        "points_against_avg": float(stats.points.against.average.all),
        "form_indicator": "good" if float(stats.games.wins.all.percentage) > 0.6 else "average"
    }
    
    return recent_performance