from typing import List, Dict, Any, Optional, Tuple
from models.basketball_models import Game

def analyze_head_to_head(games: List[Game], team1_id: int, team2_id: int) -> Dict[str, Any]:
    """Анализ истории встреч между двумя командами"""
    if not games:
        return {"error": "No head-to-head games found"}
    
    team1_wins = 0
    team2_wins = 0
    total_games = len(games)
    total_points_team1 = 0
    total_points_team2 = 0
    
    # Анализ завершенных игр
    finished_games = [game for game in games if game.status.short in ["FT", "AOT"]]
    
    for game in finished_games:
        home_score = game.scores.home.total or 0
        away_score = game.scores.away.total or 0
        
        # Определение победителя
        if home_score > away_score:
            if game.teams.home.id == team1_id:
                team1_wins += 1
            else:
                team2_wins += 1
        elif away_score > home_score:
            if game.teams.away.id == team1_id:
                team1_wins += 1
            else:
                team2_wins += 1
        
        # Подсчет очков
        if game.teams.home.id == team1_id:
            total_points_team1 += home_score
            total_points_team2 += away_score
        else:
            total_points_team1 += away_score
            total_points_team2 += home_score
    
    # Статистика
    finished_count = len(finished_games)
    if finished_count > 0:
        team1_win_rate = team1_wins / finished_count
        team2_win_rate = team2_wins / finished_count
        avg_points_team1 = total_points_team1 / finished_count
        avg_points_team2 = total_points_team2 / finished_count
    else:
        team1_win_rate = team2_win_rate = avg_points_team1 = avg_points_team2 = 0
    
    return {
        "team1_id": team1_id,
        "team2_id": team2_id,
        "total_games": total_games,
        "finished_games": finished_count,
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "team1_win_rate": team1_win_rate,
        "team2_win_rate": team2_win_rate,
        "avg_points_team1": avg_points_team1,
        "avg_points_team2": avg_points_team2,
        "point_differential": avg_points_team1 - avg_points_team2,
        "dominance_ratio": team1_win_rate - team2_win_rate if finished_count > 0 else 0
    }

def get_recent_meetings(games: List[Game], limit: int = 5) -> List[Dict[str, Any]]:
    """Получение последних встреч (новые сначала)"""
    # Сортируем по timestamp (новые сначала)
    sorted_games = sorted(games, key=lambda x: x.timestamp, reverse=True)
    
    recent_meetings = []
    for game in sorted_games[:limit]:
        home_score = game.scores.home.total
        away_score = game.scores.away.total
        
        # Определение результата
        result = "Unknown"
        if home_score is not None and away_score is not None:
            if home_score > away_score:
                result = f"{game.teams.home.name} wins"
            elif away_score > home_score:
                result = f"{game.teams.away.name} wins"
            else:
                result = "Draw"
        
        recent_meetings.append({
            "game_id": game.id,
            "date": game.date,
            "home_team": game.teams.home.name,
            "away_team": game.teams.away.name,
            "home_score": home_score,
            "away_score": away_score,
            "result": result,
            "status": game.status.long
        })
    
    return recent_meetings

def calculate_team_advantage(h2h_stats: Dict[str, Any]) -> str:
    """Определение доминирующей команды на основе статистики"""
    dominance = h2h_stats.get("dominance_ratio", 0)
    point_diff = h2h_stats.get("point_differential", 0)
    
    if dominance > 0.3 and point_diff > 5:
        return "Team 1 strongly dominates"
    elif dominance > 0.1 and point_diff > 2:
        return "Team 1 has advantage"
    elif abs(dominance) < 0.1 and abs(point_diff) < 2:
        return "Evenly matched"
    elif dominance < -0.1 and point_diff < -2:
        return "Team 2 has advantage"
    elif dominance < -0.3 and point_diff < -5:
        return "Team 2 strongly dominates"
    else:
        return "Inconclusive"

def get_venue_analysis(games: List[Game], team1_id: int, team2_id: int) -> Dict[str, Any]:
    """Анализ результатов по аренам"""
    home_games_team1 = [game for game in games if game.teams.home.id == team1_id and game.status.short in ["FT", "AOT"]]
    home_games_team2 = [game for game in games if game.teams.home.id == team2_id and game.status.short in ["FT", "AOT"]]
    
    # Статистика дома для team1
    team1_home_wins = sum(1 for game in home_games_team1 if game.scores.home.total > game.scores.away.total)
    team1_home_win_rate = team1_home_wins / len(home_games_team1) if home_games_team1 else 0
    
    # Статистика дома для team2
    team2_home_wins = sum(1 for game in home_games_team2 if game.scores.home.total > game.scores.away.total)
    team2_home_win_rate = team2_home_wins / len(home_games_team2) if home_games_team2 else 0
    
    return {
        "team1_home_record": {
            "games": len(home_games_team1),
            "wins": team1_home_wins,
            "win_rate": team1_home_win_rate
        },
        "team2_home_record": {
            "games": len(home_games_team2),
            "wins": team2_home_wins,
            "win_rate": team2_home_win_rate
        },
        "home_court_advantage": {
            "team1": team1_home_win_rate > 0.6,
            "team2": team2_home_win_rate > 0.6
        }
    }

def predict_next_meeting(h2h_stats: Dict[str, Any], venue_analysis: Dict[str, Any], home_team_id: int) -> Dict[str, Any]:
    """Упрощенный прогноз следующей встречи"""
    team1_id = h2h_stats["team1_id"]
    team2_id = h2h_stats["team2_id"]
    
    # Базовые вероятности на основе истории
    base_prob_team1 = h2h_stats["team1_win_rate"]
    base_prob_team2 = h2h_stats["team2_win_rate"]
    
    # Корректировка на домашнее преимущество
    if home_team_id == team1_id:
        home_advantage = venue_analysis["team1_home_record"]["win_rate"]
        adjusted_prob_team1 = base_prob_team1 * (1 + home_advantage * 0.2)  # +20% за домашнее преимущество
        adjusted_prob_team2 = base_prob_team2 * (1 - home_advantage * 0.2)
    else:
        home_advantage = venue_analysis["team2_home_record"]["win_rate"]
        adjusted_prob_team1 = base_prob_team1 * (1 - home_advantage * 0.2)
        adjusted_prob_team2 = base_prob_team2 * (1 + home_advantage * 0.2)
    
    # Нормализация вероятностей
    total_prob = adjusted_prob_team1 + adjusted_prob_team2
    if total_prob > 0:
        prob_team1 = adjusted_prob_team1 / total_prob
        prob_team2 = adjusted_prob_team2 / total_prob
    else:
        prob_team1 = prob_team2 = 0.5
    
    return {
        "home_team_id": home_team_id,
        "predicted_winner": team1_id if prob_team1 > prob_team2 else team2_id,
        "probability_team1": prob_team1,
        "probability_team2": prob_team2,
        "confidence": abs(prob_team1 - prob_team2),
        "expected_point_differential": h2h_stats["point_differential"]
    }