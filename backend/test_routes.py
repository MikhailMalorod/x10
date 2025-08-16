"""
Простой тест роутов FastAPI
"""

from app.main import app

def test_routes():
    """Проверяем все роуты приложения"""
    print("🔍 Проверка роутов FastAPI:")
    
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")
    
    print(f"\n📊 Всего роутов: {len([r for r in app.routes if hasattr(r, 'path')])}")

if __name__ == "__main__":
    test_routes() 