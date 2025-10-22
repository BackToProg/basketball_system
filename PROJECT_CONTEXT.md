# Basketball Data System - Контекст проекта

## 🎯 Цель

Система сбора и анализа баскетбольных данных для беттинга

## 🏗️ Архитектура

basketball_system/
├── 🏗️ data-collector/ # Сбор данных
│ ├── 📁 src/
│ │ ├── 📁 api/
│ │ │ └── basketball_api.py # API клиенты
│ │ ├── 📁 models/
│ │ │ └── basketball_models.py # Модели БД
│ │ ├── 📁 storage/
│ │ │ ├── database.py # Настройки БД
│ │ │ └── 📁 repositories/
│ │ │ ├── base.py # Базовый репозиторий
│ │ │ ├── async_base.py # Асинхронная база
│ │ │ ├── league_repository.py
│ │ │ ├── team_repository.py
│ │ │ ├── game_repository.py
│ │ │ ├── player_repository.py
│ │ │ └── alias_repository.py # Для псевдонимов команд?
│ │ ├── 📁 services/
│ │ │ └── data_orchestrator.py # Оркестратор сбора
│ │ ├── 📁 utils/ # Утилиты обработки
│ │ │ ├── league_utils.py
│ │ │ ├── team_utils.py
│ │ │ ├── game_utils.py
│ │ │ ├── player_utils.py
│ │ │ ├── season_utils.py
│ │ │ ├── country_utils.py
│ │ │ ├── h2h_utils.py # Head-to-head
│ │ │ ├── statistics_utils.py
│ │ │ ├── team_stats_utils.py
│ │ │ └── player_stats_utils.py
│ │ ├── main.py # Основное приложение
│ │ └── test_api.py # Тесты API
│ ├── requirements.txt
│ ├── Dockerfile
│ └── alembic.ini # Миграции БД
│
├── 📊 analytics-engine/ # Аналитика и ML
│ ├── 📁 src/
│ │ └── main.py
│ ├── requirements.txt
│ └── Dockerfile
│
├── 📈 visualization-api/ # Визуализация
│ ├── 📁 src/
│ │ └── main.py
│ ├── requirements.txt
│ └── Dockerfile
│
├── 🔗 shared/ # Общие модули
│ ├── models.py # Общие модели Pydantic?
│ └── utils.py # Общие утилиты
│
├── docker-compose.yml
├── README.md
└── project_structure.txt

## 🏛️ АРХИТЕКТУРНЫЕ РЕШЕНИЯ

### Разделение моделей:

- **SQLAlchemy модели** (`database.py`) - для БД
- **Pydantic схемы** (`basketball_models.py`) - для API

### Асинхронность:

- Все репозитории и API вызовы асинхронные
- Используется asyncpg для PostgreSQL

### Модели API (Pydantic)

**Файл:** `data-collector/src/models/basketball_models.py`

Схемы для валидации API ответов

Дайджест: basketball_models.py

🏗️ Базовые структуры
python
class APIResponse(BaseModel):
"""Базовая модель всех API ответов"""
get: str # Метод API
parameters: Any # Параметры запроса  
 errors: Any # Ошибки (список/словарь)
results: int # Кол-во результатов
response: Any # Данные (список/словарь)

class PagedAPIResponse(APIResponse):
"""Для пагинации"""
paging: Dict[str, int]

🌍 Страны и лиги
python
class Country(BaseModel): # Данные страны
class CountriesResponse(APIResponse) # Ответ со странами

class LeagueCountry(BaseModel): # Страна в контексте лиги
class Season(BaseModel): # Сезон лиги (с coverage)
class League(BaseModel): # Данные лиги + сезоны
class LeaguesResponse(APIResponse) # Ответ с лигами

⚽ Команды и статистика
python
class TeamCountry(BaseModel): # Страна в контексте команды  
class Team(BaseModel): # Данные команды
class TeamsResponse(APIResponse) # Ответ с командами

class TeamStatistics(BaseModel): # Полная статистика команды за сезон
class StatisticsResponse(APIResponse) # Ответ со статистикой

👥 Игроки
python
class Player(BaseModel): # Данные игрока
class PlayersResponse(APIResponse) # Ответ с игроками

🏀 Игры и матчи
python
class GameTeam(BaseModel): # Команда в игре
class GameTeams(BaseModel): # Две команды (home/away)
class GameScores(BaseModel): # Счет по четвертям
class GameStatus(BaseModel): # Статус игры
class GameLeague(BaseModel): # Лига игры
class GameCountry(BaseModel): # Страна игры
class Game(BaseModel): # Полные данные игры
class GamesResponse(APIResponse) # Ответ с играми

📊 Детальная статистика
python
class ShootingStats(BaseModel): # Статистика бросков
class ReboundsStats(BaseModel): # Статистика подборов

class TeamGameStats(BaseModel): # Статистика команды в конкретной игре
class TeamsStatisticsResponse(APIResponse) # Ответ со статистикой команд

class PlayerGameStats(BaseModel): # Статистика игрока в конкретной игре  
class PlayersStatisticsResponse(APIResponse) # Ответ со статистикой игроков

🔧 Утилиты валидации
handle_null_strings() - обработка null в строках
handle_null_dates() - обработка null в датах
normalize_season() - нормализация сезона в строку
handle_null_country() - обработка отсутствующей страны

**Файл:** `data-collector/src/main.py`

📋 Дайджест: main.py - FastAPI приложение
🚀 Инициализация
python
app = FastAPI() # Основное приложение
basketball_api = None # Глобальный клиент API
data_orchestrator = None # Оркестратор сбора данных
🔧 Жизненный цикл
python
@app.on_event("startup") # Инициализация API клиента
@app.on_event("shutdown") # Очистка ресурсов

📊 Эндпоинты сбора данных
python

# Управление сбором

POST /collection/start # Запуск сбора
POST /collection/stop # Остановка сбора  
GET /collection/status # Статус сбора
POST /collection/historical # Ручной сбор исторических данных

🌐 Прокси-эндпоинты к Basketball API
python

# Получение данных из внешнего API

GET /seasons # Все сезоны
GET /countries # Страны с фильтрацией
GET /leagues # Лиги (с фильтром по статистике)
GET /teams # Команды с фильтрацией
GET /statistics # Статистика команды за сезон
GET /players # Игроки с фильтрацией
GET /games # Матчи с фильтрацией

📈 Статистика игр
python
GET /games/statistics/teams # Статистика команд по играм (до 20 игр)
GET /games/statistics/players # Статистика игроков по играм
⚔ Head-to-Head анализ
python
GET /games/h2h # История встреч двух команд
GET /games/h2h/analysis # Расширенный анализ встреч # Включает: базовую статистику, последние встречи, # анализ преимуществ, статистику по аренам

🗄️ Работа с БД
python
GET /data/leagues # Просмотр лиг/сезонов/команд из БД
🩺 Системные эндпоинты
python
GET / # Корневой endpoint
GET /health # Проверка здоровья (API подключение)

🧪 Тестовые эндпоинты
python
GET /test/database # Тест БД и репозиториев
GET /test/database/simple # Простой тест БД
GET /test/database/basic # Базовый тест подключения
GET /test/repositories/simple # Тест репозиториев

🔍 Ключевые особенности:
Валидация параметров - проверка обязательных параметров, лимитов
Обработка ошибок API - проверка errors в ответах
Фильтрация лиг - по coverage статистики (filter_by_stats)
Лимиты - максимум 20 game_ids для статистики
Временные зоны - поддержка разных таймзон

📝 Зависимости:
BasketballAPI - клиент внешнего API
DataOrchestrator - оркестратор сбора данных
db_manager - менеджер БД
repositories - репозитории для работы с данными

**Файл:** `data-collector/src/api/basketball_api.py`

Дайджест: basketball_api.py - API клиент

🏗️ Основной класс
python
class BasketballAPI:
"""Клиент для работы с Basketball API (api-sports.io)"""
def **init**(self, api_key: str, base_url: str = "https://v1.basketball.api-sports.io")
🔌 Подключение
python
async def test_connection(self) -> bool
"""Проверка подключения к API (/status)"""
📊 Основные методы API
📅 Метаданные
python
async def get_seasons(self) -> Optional[SeasonsResponse]
"""Все доступные сезоны"""

async def get_countries(self, country_id, name, code, search) -> Optional[CountriesResponse]
"""Страны с фильтрацией"""
🏆 Лиги
python
async def get_leagues(self, league_id, name, country_id, country, type, season, search, code, filter_by_stats_coverage=True) -> Optional[LeaguesResponse]
"""Лиги с фильтрацией + фильтр по coverage статистики""" # Особенность: фильтрует лиги по наличию полной статистики
⚽ Команды
python
async def get_teams(self, team_id, name, country_id, country, league, season, search) -> Optional[TeamsResponse]
"""Команды с фильтрацией (требует хотя бы 1 параметр)"""
📈 Статистика
python
async def get_team_statistics(self, league, season, team, date) -> Optional[StatisticsResponse]
"""Статистика команды за сезон"""

async def get_teams_statistics(self, game_id, game_ids) -> Optional[TeamsStatisticsResponse]
"""Статистика команд по играм (макс. 20 game_ids)"""

async def get_players_statistics(self, game_id, game_ids, player, season) -> Optional[PlayersStatisticsResponse]
"""Статистика игроков по играм (player требует season)"""
👥 Игроки
python
async def get_players(self, player_id, team, season, search) -> Optional[PlayersResponse]
"""Игроки с фильтрацией"""
🏀 Игры
python
async def get_games(self, game_id, date, league, season, team, timezone) -> Optional[GamesResponse]
"""Матчи с фильтрацией (league требует season)"""

async def get_head_to_head(self, team1_id, team2_id, date, league, season, timezone) -> Optional[GamesResponse]
"""История встреч двух команд (через параметр h2h)"""
⚙️ Управление
python
async def close(self)
"""Закрытие HTTP клиента"""
🔍 Ключевые особенности:
Валидация параметров:

Обязательные параметры для endpoints

Максимум 20 game_ids для статистики

Взаимозависимые параметры (league → season, player → season)

Фильтрация лиг:

filter_by_stats_coverage=True - оставляет только лиги с полной статистикой
Проверяет coverage.games.statistics.teams и coverage.games.statistics.players

Обработка ошибок:
Логирование через structlog
Возврат None при ошибках (вместо исключений)
Подробное логирование параметров и ошибок

Типизация:
Использует Pydantic модели из basketball_models.py
Опциональные возвраты для обработки ошибок

📝 Зависимости:
httpx.AsyncClient - асинхронные HTTP запросы

structlog - логирование

**Файл:** `data-collector/src/storage/database.py`

📋 Дайджест: database.py - Модели БД
🏗️ Базовые структуры
python
class Base(DeclarativeBase): # Базовый класс для всех моделей
class DatabaseManager: # Менеджер асинхронной БД
🗄️ Основные сущности
🏆 Лиги и сезоны
python
class League(Base):
"""Лиги: id, name, type, logo, country_data""" # Связи: seasons, games

class Season(Base):  
 """Сезоны: league_id, season, dates, coverage_flags""" # Связи: league, games, team_stats # Coverage: has_teams_stats, has_players_stats, has_standings, has_odds
⚽ Команды
python
class Team(Base):
"""Команды: id, name, code, country, founded, logo, national""" # Связи: home_games, away_games, team_stats, player_stats
🏀 Игры и матчи
python
class Game(Base):
"""Игры: league_id, season_id, teams, date, scores, status""" # Детальный счет по четвертям + OT # Связи: league, season, home_team, away_team, team_stats, player_stats
📊 Статистика
📈 Статистика команд
python
class TeamSeasonStats(Base):
"""Статистика команды за сезон: игры, победы, очки, проценты""" # Агрегированная статистика за весь сезон

class TeamGameStats(Base):
"""Статистика команды в конкретной игре: броски, подборы, передачи""" # Детальная статистика за игру: FG%, 3P%, FT%, rebounds, assists, etc.
👥 Игроки и их статистика
python
class Player(Base):
"""Игроки: id, name, personal_data, position""" # Связи: game_stats

class PlayerGameStats(Base):
"""Статистика игрока в игре: минуты, броски, очки, другие показатели""" # player_type: "starters" или "bench"
💰 Беттинг данные
python
class Odds(Base):
"""Коэффициенты: game_id, bookmaker, основные коэфы, тоталы, форы""" # odds_home, odds_away, total_over, total_under, handicap
🔄 Система сопоставления
🎯 Сопоставление команд
python
class TeamAlias(Base):
"""Сопоставление наших команд с внешними системами (Betcity)""" # team_id (наша команда), betcity_name, confidence (0-1)
🏆 Сопоставление лиг
python
class LeagueMapping(Base):
"""Сопоставление наших лиг с внешними системами""" # league_id (наша лига), betcity_league_id, betcity_league_name
⚙️ Управление БД
python
class DatabaseManager:
"""Асинхронный менеджер PostgreSQL БД"""
async def create_tables(self) # Создание всех таблиц
def get_async_session(self) # Контекстный менеджер сессии
🔍 Ключевые особенности:
Асинхронная архитектура - используется asyncpg для PostgreSQL

Связи SQLAlchemy - отношения между таблицами через relationship

Детальная статистика - разделение на сезонную и поквартальную

Система сопоставления - TeamAlias и LeagueMapping для связи с беттинг-провайдерами

Метаданные - created_at, updated_at для отслеживания изменений

Coverage система - флаги доступной статистики в Season

📊 Структура данных:
Основные сущности: League → Season → Team → Game

Статистика: TeamSeasonStats (агрегированная), TeamGameStats/PlayerGameStats (детальная)

Беттинг: Odds (коэффициенты)

Сопоставление: TeamAlias, LeagueMapping (для интеграции)

### Ключевые репозитории

**Папка:** `data-collector/src/storage/repositories/`

- `league_repository.py`, `team_repository.py`, `game_repository.py`
- `alias_repository.py` - текущая система сопоставления

## 📊 ТЕКУЩИЙ СТАТУС ПРОЕКТА

**✅ ЗАВЕРШЕНО:**

- Data-collector с полным API клиентом
- Модели БД (не все) и Pydantic схемы
- Базовые репозитории и эндпоинты

**🔨 В РАЗРАБОТКЕ:**

- Система сопоставления команд/лиг с беттинг-провайдерами
- Внедрение парсера и соединение данных по API и парсера
- Сбор всех исторических данных по всем доступным лигам
- Настройка заданий по сбору мачтей и кэфов на текущую дату
- Настройка заданий по сбору лайв статистики по четвертям

**📋 В ПЛАНИРОВАНИИ:**

- ML модуль для аналитики
- Визуализация данных
- Продвинутая аналитика
