import asyncio
from typing import Optional
from fastapi import FastAPI, HTTPException
import uvicorn
from dotenv import load_dotenv
from sqlalchemy import text 
import os
from storage.database import db_manager
from storage.repositories import repositories

from api.basketball_api import BasketballAPI
from services.data_orchestrator import DataOrchestrator

# Загружаем переменные окружения
load_dotenv('config/.env')
data_orchestrator: Optional[DataOrchestrator] = None

app = FastAPI(
    title="Basketball Data Collector",
    description="Микросервис для сбора баскетбольных данных",
    version="1.0.0"
)

# Глобальный клиент API
basketball_api = None

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    global basketball_api, data_orchestrator
    
    api_key = os.getenv("BASKETBALL_API_KEY")
    if not api_key:
        raise Exception("BASKETBALL_API_KEY not found in environment variables")
    
    basketball_api = BasketballAPI(api_key)
    data_orchestrator = DataOrchestrator(basketball_api)
    
    print("🚀 Basketball Data Collector started!")

@app.on_event("shutdown")
async def shutdown_event():
    """Очистка при завершении"""
    global data_orchestrator
    if data_orchestrator and data_orchestrator.is_running:
        await data_orchestrator.stop_collection()
    
    if basketball_api:
        await basketball_api.close()

@app.post("/collection/start")
async def start_collection():
    """Запуск сбора данных"""
    if not data_orchestrator:
        raise HTTPException(status_code=500, detail="Data orchestrator not initialized")
    
    if data_orchestrator.is_running:
        raise HTTPException(status_code=400, detail="Data collection is already running")
    
    # Запускаем в фоне
    asyncio.create_task(data_orchestrator.start_collection())
    
    return {"status": "started", "message": "Data collection started"}

@app.post("/collection/stop")
async def stop_collection():
    """Остановка сбора данных"""
    if not data_orchestrator:
        raise HTTPException(status_code=500, detail="Data orchestrator not initialized")
    
    await data_orchestrator.stop_collection()
    
    return {"status": "stopped", "message": "Data collection stopped"}

@app.get("/collection/status")
async def get_collection_status():
    """Получение статуса сбора данных"""
    if not data_orchestrator:
        return {"status": "not_initialized"}
    
    return {
        "status": "running" if data_orchestrator.is_running else "stopped",
        "is_running": data_orchestrator.is_running
    }

@app.post("/collection/historical")
async def collect_historical_data():
    """Ручной запуск сбора исторических данных"""
    if not data_orchestrator:
        raise HTTPException(status_code=500, detail="Data orchestrator not initialized")
    
    await data_orchestrator.collect_historical_data()
    
    return {"status": "completed", "message": "Historical data collection completed"}

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Basketball Data Collector API",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    if basketball_api:
        connection_ok = await basketball_api.test_connection()
        return {
            "status": "healthy" if connection_ok else "unhealthy",
            "api_connection": connection_ok
        }
    return {"status": "unhealthy", "api_connection": False}

@app.get("/data/leagues")
async def get_leagues_data(skip: int = 0, limit: int = 50):
    """Просмотр лиг в БД"""
    leagues = await repositories.leagues.get_all(skip=skip, limit=limit)
    seasons = await repositories.seasons.get_all(skip=skip, limit=limit)
    teams = await repositories.teams.get_all(skip=skip, limit=limit)
    
    return {
        "leagues_count": len(leagues),
        "seasons_count": len(seasons),
        "teams_count": len(teams),
        "leagues": [
            {
                "id": league.id,
                "name": league.name,
                "type": league.type,
                "country": league.country_name
            }
            for league in leagues
        ],
        "seasons": [
            {
                "id": season.id,
                "league_id": season.league_id,
                "season": season.season,
                "has_stats": season.has_teams_stats
            }
            for season in seasons
        ]
    }

@app.get("/seasons")
async def get_seasons():
    """Получение всех доступных сезонов"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    seasons = await basketball_api.get_seasons()
    if seasons is None:
        raise HTTPException(status_code=500, detail="Failed to fetch seasons")
    
    return seasons

@app.get("/countries")
async def get_countries(
    country_id: Optional[int] = None,
    name: Optional[str] = None, 
    code: Optional[str] = None,
    search: Optional[str] = None
):
    """Получение списка стран с возможностью фильтрации"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    countries = await basketball_api.get_countries(
        country_id=country_id,
        name=name,
        code=code,
        search=search
    )
    if countries is None:
        raise HTTPException(status_code=500, detail="Failed to fetch countries")
    
    return countries

@app.get("/leagues")
async def get_leagues(
    league_id: Optional[int] = None,
    name: Optional[str] = None,
    country_id: Optional[int] = None, 
    country: Optional[str] = None,
    type: Optional[str] = None,
    season: Optional[str] = None,
    search: Optional[str] = None,
    code: Optional[str] = None,
    filter_by_stats: bool = True  # Фильтровать ли по coverage статистики
):
    """Получение списка лиг с фильтрацией"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    leagues = await basketball_api.get_leagues(
        league_id=league_id,
        name=name,
        country_id=country_id,
        country=country,
        type=type,
        season=season,
        search=search,
        code=code,
        filter_by_stats_coverage=filter_by_stats
    )
    if leagues is None:
        raise HTTPException(status_code=500, detail="Failed to fetch leagues")
    
    return leagues

@app.get("/teams")
async def get_teams(
    team_id: Optional[int] = None,
    name: Optional[str] = None,
    country_id: Optional[int] = None,
    country: Optional[str] = None,
    league: Optional[int] = None,
    season: Optional[str] = None,
    search: Optional[str] = None
):
    """Получение данных о командах с фильтрацией"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    teams = await basketball_api.get_teams(
        team_id=team_id,
        name=name,
        country_id=country_id,
        country=country,
        league=league,
        season=season,
        search=search
    )
    if teams is None:
        raise HTTPException(
            status_code=400, 
            detail="Teams endpoint requires at least one parameter (team_id, name, country_id, country, league, season, or search)"
        )
    
    return teams

@app.get("/statistics")
async def get_team_statistics(
    league: int,
    season: str,
    team: int,
    date: Optional[str] = None
):
    """Получение статистики команды за сезон"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    statistics = await basketball_api.get_team_statistics(
        league=league,
        season=season,
        team=team,
        date=date
    )
    if statistics is None:
        raise HTTPException(status_code=500, detail="Failed to fetch team statistics")
    
    # Проверяем, есть ли ошибки в ответе
    if statistics.errors:
        error_message = "API returned errors: "
        if isinstance(statistics.errors, list):
            error_message += ", ".join(statistics.errors)
        else:
            error_message += str(statistics.errors)
        
        raise HTTPException(status_code=400, detail=error_message)
    
    # Проверяем, что response содержит данные (а не пустой список)
    if isinstance(statistics.response, list) and not statistics.response:
        raise HTTPException(
            status_code=404, 
            detail="No statistics found for the given parameters. This might be due to API plan limitations or no data available."
        )
    
    return statistics

@app.get("/players")
async def get_players(
    player_id: Optional[int] = None,
    team: Optional[int] = None,
    season: Optional[str] = None,
    search: Optional[str] = None
):
    """Получение данных об игроках с фильтрацией"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    players = await basketball_api.get_players(
        player_id=player_id,
        team=team,
        season=season,
        search=search
    )
    if players is None:
        raise HTTPException(
            status_code=400, 
            detail="Players endpoint requires at least one parameter (player_id, team, season, or search)"
        )
    
    return players

@app.get("/games")
async def get_games(
    game_id: Optional[int] = None,
    date: Optional[str] = None,
    league: Optional[int] = None,
    season: Optional[str] = None,
    team: Optional[int] = None,
    timezone: Optional[str] = "Europe/Moscow"
):
    """Получение данных о матчах с фильтрацией"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    # Валидация: если указана лига, сезон обязателен
    if league and not season:
        raise HTTPException(
            status_code=400,
            detail="Season parameter is required when using league filter"
        )
    
    games = await basketball_api.get_games(
        game_id=game_id,
        date=date,
        league=league,
        season=season,
        team=team,
        timezone=timezone
    )
    if games is None:
        raise HTTPException(
            status_code=400, 
            detail="Games endpoint requires at least one parameter (game_id, date, league+season, or team)"
        )
    
    return games

@app.get("/games/statistics/teams")
async def get_teams_statistics(
    game_id: Optional[str] = None,
    game_ids: Optional[str] = None
):
    """Получение статистики команд по играм"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    # Валидация параметров
    if game_ids:
        ids_count = len(game_ids.split('-'))
        if ids_count > 20:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum 20 game ids allowed, got {ids_count}"
            )
    
    statistics = await basketball_api.get_teams_statistics(
        game_id=game_id,
        game_ids=game_ids
    )
    if statistics is None:
        raise HTTPException(
            status_code=400, 
            detail="Teams statistics endpoint requires at least one parameter (game_id or game_ids)"
        )
    
    return statistics

@app.get("/games/statistics/players")
async def get_players_statistics(
    game_id: Optional[str] = None,
    game_ids: Optional[str] = None,
    player: Optional[int] = None,
    season: Optional[str] = None
):
    """Получение статистики игроков по играм"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    # Валидация параметров
    if game_ids:
        ids_count = len(game_ids.split('-'))
        if ids_count > 20:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum 20 game ids allowed, got {ids_count}"
            )
    
    # Если указан player, season обязателен
    if player and not season:
        raise HTTPException(
            status_code=400,
            detail="Season parameter is required when using player filter"
        )
    
    statistics = await basketball_api.get_players_statistics(
        game_id=game_id,
        game_ids=game_ids,
        player=player,
        season=season
    )
    if statistics is None:
        raise HTTPException(
            status_code=400, 
            detail="Players statistics endpoint requires at least one parameter (game_id, game_ids, or player+season)"
        )
    
    return statistics

@app.get("/games/h2h")
async def get_head_to_head(
    team1_id: int,
    team2_id: int,
    date: Optional[str] = None,
    league: Optional[int] = None,
    season: Optional[str] = None,
    timezone: Optional[str] = "Europe/Moscow"
):
    """Получение истории встреч между двумя командами"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    h2h_games = await basketball_api.get_head_to_head(
        team1_id=team1_id,
        team2_id=team2_id,
        date=date,
        league=league,
        season=season,
        timezone=timezone
    )
    if h2h_games is None:
        raise HTTPException(status_code=500, detail="Failed to fetch head-to-head statistics")
    
    return h2h_games

@app.get("/games/h2h/analysis")
async def get_head_to_head_analysis(
    team1_id: int,
    team2_id: int,
    date: Optional[str] = None,
    league: Optional[int] = None,
    season: Optional[str] = None,
    timezone: Optional[str] = "Europe/Moscow"
):
    """Расширенный анализ встреч между двумя командами"""
    if not basketball_api:
        raise HTTPException(status_code=500, detail="API client not initialized")
    
    h2h_games = await basketball_api.get_head_to_head(
        team1_id=team1_id,
        team2_id=team2_id,
        date=date,
        league=league,
        season=season,
        timezone=timezone
    )
    if h2h_games is None:
        raise HTTPException(status_code=500, detail="Failed to fetch head-to-head statistics")
    
    # Импортируем утилиты
    from utils.h2h_utils import analyze_head_to_head, get_recent_meetings, calculate_team_advantage, get_venue_analysis
    
    # Анализ данных
    h2h_stats = analyze_head_to_head(h2h_games.response, team1_id, team2_id)
    recent_meetings = get_recent_meetings(h2h_games.response)
    advantage = calculate_team_advantage(h2h_stats)
    venue_stats = get_venue_analysis(h2h_games.response, team1_id, team2_id)
    
    return {
        "basic_stats": h2h_stats,
        "recent_meetings": recent_meetings,
        "advantage_analysis": advantage,
        "venue_analysis": venue_stats,
        "all_games": h2h_games.response
    }

@app.get("/test/database")
async def test_database():
    """Тестирование работы с базой данных"""
    try:
        # Создаем таблицы (в продакшене это должно быть через миграции)
        db_manager.create_tables()
        
        # Тестируем репозитории
        with repositories.leagues as league_repo:
            # Проверяем, есть ли уже тестовая лига
            test_league = league_repo.get_by_id(999)
            
            if not test_league:
                # Создаем тестовую лигу
                test_league = league_repo.create(
                    id=999,
                    name="Test League",
                    type="League", 
                    country_name="Test Country",
                    country_code="TC"
                )
                message = f"✅ Создана тестовая лига: {test_league.name}"
            else:
                message = f"✅ Найдена существующая лига: {test_league.name}"
        
        # Тестируем другие репозитории
        with repositories.teams as team_repo:
            teams_count = len(team_repo.get_all(limit=5))
            message += f" | Найдено команд: {teams_count}"
            
        return {
            "status": "success",
            "message": message,
            "test_league_id": 999
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Ошибка: {str(e)}"
        }

@app.get("/test/database/simple")
async def test_database_simple():
    """Простой тест базы данных"""
    try:
        # Создаем таблицы
        await db_manager.create_tables()
        
        # Используем text() для SQL выражений
        async with db_manager.get_async_session() as session:
            result = await session.execute(text("SELECT 1"))
            test_result = result.scalar()
            
        return {
            "status": "success",
            "message": "✅ База данных работает",
            "test_query": test_result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Ошибка: {str(e)}"
        }

@app.get("/test/database/basic")
async def test_database_basic():
    """Базовый тест подключения к БД"""
    try:
        # Просто проверяем подключение к движку с text()
        async with db_manager.engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            db_version = result.scalar()
            
        return {
            "status": "success",
            "message": "✅ База данных подключена",
            "version": db_version
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Ошибка: {str(e)}"
        }

@app.get("/test/repositories/simple")
async def test_repositories_simple():
    """Простой тест репозиториев"""
    try:
        results = {}
        
        # Тестируем создание тестовой лиги (теперь через ключевые слова)
        test_league = await repositories.leagues.get_by_id(999)
        if not test_league:
            test_league = await repositories.leagues.create(
                id=999,
                name="Test League",
                type="League"
            )
            results["create_league"] = f"✅ Тестовая лига создана: {test_league.name}"
        else:
            results["create_league"] = f"✅ Тестовая лига уже существует: {test_league.name}"
        
        # Тестируем простой запрос
        leagues = await repositories.leagues.get_all(limit=5)
        results["leagues_count"] = f"✅ Найдено лиг: {len(leagues)}"
        
        # Тестируем создание команды
        test_team = await repositories.teams.get_by_id(999)
        if not test_team:
            test_team = await repositories.teams.create(
                id=999,
                name="Test Team",
                country="Test Country"
            )
            results["create_team"] = f"✅ Тестовая команда создана: {test_team.name}"
        else:
            results["create_team"] = f"✅ Тестовая команда уже существует: {test_team.name}"
            
        return {
            "status": "success", 
            "results": results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Ошибка: {str(e)}"
        }
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)