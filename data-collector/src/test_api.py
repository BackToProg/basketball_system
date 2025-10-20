import asyncio
import os
import sys

# Добавляем путь для импортов
sys.path.append('/app/src')

from api.basketball_api import BasketballAPI

async def test_api():
    """Тестируем API подключение в Docker"""
    api_key = os.getenv("BASKETBALL_API_KEY")
    
    if not api_key:
        print("❌ BASKETBALL_API_KEY not found in environment variables")
        print("💡 Make sure config/.env file exists and contains BASKETBALL_API_KEY")
        return
    
    api = BasketballAPI(api_key)
    
    try:
        print("🔌 Testing API connection from Docker...")
        connection_ok = await api.test_connection()
        
        if connection_ok:
            print("✅ API connection successful from Docker!")
            
            # Тестируем получение данных
            print("🏀 Fetching leagues...")
            leagues = await api.get_leagues()
            if leagues:
                leagues_count = len(leagues.get('response', []))
                print(f"✅ Found {leagues_count} leagues")
                
            print("📅 Fetching recent games...")
            games = await api.get_games(league="12", season="2024-2025")
            if games:
                games_data = games.get('response', [])
                print(f"✅ Found {len(games_data)} games")
                if games_data:
                    for game in games_data[:3]:  # Показываем первые 3 матча
                        home_team = game.get('teams', {}).get('home', {}).get('name', 'Unknown')
                        away_team = game.get('teams', {}).get('away', {}).get('name', 'Unknown')
                        print(f"   🏆 {home_team} vs {away_team}")
        else:
            print("❌ API connection failed from Docker")
            
    except Exception as e:
        print(f"💥 Error during Docker testing: {e}")
    finally:
        await api.close()

if __name__ == "__main__":
    asyncio.run(test_api())