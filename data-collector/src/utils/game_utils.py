from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models.basketball_models import Game

def filter_live_games(games: List[Game]) -> List[Game]:
    """Фильтрация лайв-матчей"""
    live_statuses = ["Q1", "Q2", "Q3", "Q4", "OT", "BT", "HT"]
    return [game for game in games if game.status.short in live_statuses]

def filter_finished_games(games: List[Game]) -> List[Game]:
    """Фильтрация завершенных матчей"""
    finished_statuses = ["FT", "AOT", "AWD"]
    return [game for game in games if game.status.short in finished_statuses]

def filter_upcoming_games(games: List[Game]) -> List[Game]:
    """Фильтрация предстоящих матчей"""
    return [game for game in games if game.status.short == "NS"]

def get_games_by_date(games: List[Game], target_date: str) -> List[Game]:
    """Фильтрация матчей по дате"""
    return [game for game in games if game.date.startswith(target_date)]

def get_games_by_team(games: List[Game], team_id: int) -> List[Game]:
    """Фильтрация матчей по команде"""
    return [game for game in games if game.teams.home.id == team_id or game.teams.away.id == team_id]

def calculate_game_stats(game: Game) -> Dict[str, Any]:
    """Расчет статистики матча"""
    home_score = game.scores.home.total or 0
    away_score = game.scores.away.total or 0
    
    # Определение победителя
    winner = None
    if home_score > away_score:
        winner = "home"
    elif away_score > home_score:
        winner = "away"
    
    # Разница очков
    point_differential = abs(home_score - away_score)
    
    # Анализ по четвертям
    quarters_analysis = {}
    for i in range(1, 5):
        home_q = getattr(game.scores.home, f'quarter_{i}', None)
        away_q = getattr(game.scores.away, f'quarter_{i}', None)
        if home_q is not None and away_q is not None:
            quarters_analysis[f'quarter_{i}'] = {
                'home': home_q,
                'away': away_q,
                'difference': home_q - away_q
            }
    
    return {
        "game_id": game.id,
        "winner": winner,
        "home_score": home_score,
        "away_score": away_score,
        "point_differential": point_differential,
        "total_points": home_score + away_score,
        "quarters_analysis": quarters_analysis,
        "status": game.status.short
    }

def get_team_recent_games(games: List[Game], team_id: int, limit: int = 10) -> List[Game]:
    """Получение последних матчей команды"""
    team_games = get_games_by_team(games, team_id)
    # Сортируем по дате (новые сначала)
    team_games.sort(key=lambda x: x.timestamp, reverse=True)
    return team_games[:limit]

def analyze_team_form(games: List[Game], team_id: int) -> Dict[str, Any]:
    """Анализ формы команды по последним матчам"""
    recent_games = get_team_recent_games(games, team_id, 10)
    
    wins = 0
    losses = 0
    total_points_for = 0
    total_points_against = 0
    games_count = len(recent_games)
    
    for game in recent_games:
        stats = calculate_game_stats(game)
        if stats["winner"]:
            if (stats["winner"] == "home" and game.teams.home.id == team_id) or \
               (stats["winner"] == "away" and game.teams.away.id == team_id):
                wins += 1
            else:
                losses += 1
        
        # Подсчет очков
        if game.teams.home.id == team_id:
            total_points_for += game.scores.home.total or 0
            total_points_against += game.scores.away.total or 0
        else:
            total_points_for += game.scores.away.total or 0
            total_points_against += game.scores.home.total or 0
    
    return {
        "team_id": team_id,
        "games_analyzed": games_count,
        "wins": wins,
        "losses": losses,
        "win_rate": wins / games_count if games_count > 0 else 0,
        "points_for_avg": total_points_for / games_count if games_count > 0 else 0,
        "points_against_avg": total_points_against / games_count if games_count > 0 else 0,
        "point_differential_avg": (total_points_for - total_points_against) / games_count if games_count > 0 else 0
    }

def get_games_time_range(games: List[Game], days: int = 7) -> List[Game]:
    """Получение матчей за последние N дней"""
    cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
    return [game for game in games if game.timestamp >= cutoff_timestamp]