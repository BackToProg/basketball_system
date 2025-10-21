from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

class League(Base):
    __tablename__ = 'leagues'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50))
    logo = Column(String(255))
    country_id = Column(Integer)
    country_name = Column(String(100))
    country_code = Column(String(10))
    country_flag = Column(String(255))
    
    # Связи
    seasons = relationship("Season", back_populates="league")
    games = relationship("Game", back_populates="league")

class Season(Base):
    __tablename__ = 'seasons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    season = Column(String(20), nullable=False)  # "2023-2024"
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Coverage fields
    has_teams_stats = Column(Boolean, default=False)
    has_players_stats = Column(Boolean, default=False)
    has_standings = Column(Boolean, default=False)
    has_odds = Column(Boolean, default=False)
    
    # Связи
    league = relationship("League", back_populates="seasons")
    games = relationship("Game", back_populates="season")
    team_stats = relationship("TeamSeasonStats", back_populates="season")

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10))
    country = Column(String(100))
    founded = Column(Integer)
    logo = Column(String(255))
    national = Column(Boolean, default=False)
    
    # Связи
    home_games = relationship("Game", foreign_keys="Game.home_team_id", back_populates="home_team")
    away_games = relationship("Game", foreign_keys="Game.away_team_id", back_populates="away_team")
    team_stats = relationship("TeamSeasonStats", back_populates="team")
    player_stats = relationship("PlayerGameStats", back_populates="team")

class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    home_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    away_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Основная информация
    date = Column(DateTime, nullable=False)
    timestamp = Column(Integer)
    timezone = Column(String(50))
    status = Column(String(20))  # "NS", "Q1", "FT", etc.
    stage = Column(String(50))
    week = Column(String(20))
    venue = Column(String(100))
    
    # Счет
    home_score_total = Column(Integer)
    away_score_total = Column(Integer)
    home_score_q1 = Column(Integer)
    home_score_q2 = Column(Integer)
    home_score_q3 = Column(Integer)
    home_score_q4 = Column(Integer)
    home_score_ot = Column(Integer)
    away_score_q1 = Column(Integer)
    away_score_q2 = Column(Integer)
    away_score_q3 = Column(Integer)
    away_score_q4 = Column(Integer)
    away_score_ot = Column(Integer)
    
    # Метаданные
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Связи
    league = relationship("League", back_populates="games")
    season = relationship("Season", back_populates="games")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_games")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_games")
    team_stats = relationship("TeamGameStats", back_populates="game")
    player_stats = relationship("PlayerGameStats", back_populates="game")

class TeamSeasonStats(Base):
    __tablename__ = 'team_season_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)
    
    # Статистика игр
    games_played = Column(Integer, default=0)
    games_played_home = Column(Integer, default=0)
    games_played_away = Column(Integer, default=0)
    
    # Победы/поражения
    wins_total = Column(Integer, default=0)
    wins_home = Column(Integer, default=0)
    wins_away = Column(Integer, default=0)
    losses_total = Column(Integer, default=0)
    losses_home = Column(Integer, default=0)
    losses_away = Column(Integer, default=0)
    
    # Проценты побед
    win_percentage_total = Column(Float, default=0.0)
    win_percentage_home = Column(Float, default=0.0)
    win_percentage_away = Column(Float, default=0.0)
    
    # Очки
    points_for_total = Column(Integer, default=0)
    points_against_total = Column(Integer, default=0)
    points_for_avg = Column(Float, default=0.0)
    points_against_avg = Column(Float, default=0.0)
    
    # Метаданные
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Связи
    team = relationship("Team", back_populates="team_stats")
    season = relationship("Season", back_populates="team_stats")
    league = relationship("League")

class TeamGameStats(Base):
    __tablename__ = 'team_game_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    
    # Броски
    field_goals_made = Column(Integer, default=0)
    field_goals_attempted = Column(Integer, default=0)
    field_goals_percentage = Column(Float, default=0.0)
    
    three_point_made = Column(Integer, default=0)
    three_point_attempted = Column(Integer, default=0)
    three_point_percentage = Column(Float, default=0.0)
    
    free_throws_made = Column(Integer, default=0)
    free_throws_attempted = Column(Integer, default=0)
    free_throws_percentage = Column(Float, default=0.0)
    
    # Другие статистики
    rebounds_total = Column(Integer, default=0)
    rebounds_offensive = Column(Integer, default=0)
    rebounds_defensive = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    personal_fouls = Column(Integer, default=0)
    
    # Связи
    game = relationship("Game", back_populates="team_stats")
    team = relationship("Team")

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    firstname = Column(String(50))
    lastname = Column(String(50))
    age = Column(Integer)
    birth_date = Column(DateTime)
    country = Column(String(100))
    height = Column(String(20))
    weight = Column(String(20))
    college = Column(String(100))
    position = Column(String(50))
    
    # Связи
    game_stats = relationship("PlayerGameStats", back_populates="player")

class PlayerGameStats(Base):
    __tablename__ = 'player_game_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    
    # Основная информация
    player_type = Column(String(20))  # "starters", "bench"
    minutes_played = Column(String(10))  # "25:30"
    
    # Броски
    field_goals_made = Column(Integer, default=0)
    field_goals_attempted = Column(Integer, default=0)
    field_goals_percentage = Column(Float, default=0.0)
    
    three_point_made = Column(Integer, default=0)
    three_point_attempted = Column(Integer, default=0)
    three_point_percentage = Column(Float, default=0.0)
    
    free_throws_made = Column(Integer, default=0)
    free_throws_attempted = Column(Integer, default=0)
    free_throws_percentage = Column(Float, default=0.0)
    
    # Другие статистики
    rebounds_total = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    steals = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    personal_fouls = Column(Integer, default=0)
    points = Column(Integer, default=0)
    
    # Метаданные
    created_at = Column(DateTime, server_default=func.now())
    
    # Связи
    game = relationship("Game", back_populates="player_stats")
    team = relationship("Team", back_populates="player_stats")
    player = relationship("Player", back_populates="game_stats")

class Odds(Base):
    __tablename__ = 'odds'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)
    bookmaker = Column(String(50), nullable=False)  # "betcity", "etc"
    
    # Основные коэффициенты
    odds_home = Column(Float)
    odds_away = Column(Float)
    odds_draw = Column(Float)
    
    # Тоталы
    total_over = Column(Float)
    total_under = Column(Float)
    total_points = Column(Float)
    
    # Форы
    handicap_home = Column(Float)
    handicap_away = Column(Float)
    handicap_value = Column(Float)
    
    # Время обновления
    timestamp = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Связи
    game = relationship("Game")

class TeamAlias(Base):
    __tablename__ = 'team_aliases'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)  # Ссылка на нашу команду
    betcity_name = Column(String(200), nullable=False)  # Название в Betcity
    source_api = Column(String(50), default='basketball-api')  # Откуда данные
    confidence = Column(Float, default=1.0)  # Уверенность в совпадении (0-1)
    
    # Метаданные
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Связи
    team = relationship("Team")

class LeagueMapping(Base):
    __tablename__ = 'league_mappings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    league_id = Column(Integer, ForeignKey('leagues.id'), nullable=False)  # Наша лига
    betcity_league_id = Column(Integer, nullable=False)  # ID лиги в Betcity
    betcity_league_name = Column(String(200))  # Название в Betcity
    
    # Метаданные
    created_at = Column(DateTime, server_default=func.now())
    
    # Связи
    league = relationship("League")

# Асинхронный менеджер БД
class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        # Заменяем sync на async драйвер
        async_database_url = self.database_url.replace('postgresql+psycopg2', 'postgresql+asyncpg')
        
        self.engine = create_async_engine(async_database_url, echo=True)
        self.async_session_maker = async_sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Создание всех таблиц (асинхронно)"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    def get_async_session(self):
        """Возвращает асинхронный контекстный менеджер для сессии"""
        return self.async_session_maker()

# Создаем экземпляр менеджера БД
db_manager = DatabaseManager()