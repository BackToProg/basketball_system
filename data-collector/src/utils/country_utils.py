from typing import List, Optional
from models.basketball_models import Country

def find_country_by_code(countries: List[Country], code: str) -> Optional[Country]:
    """Поиск страны по коду"""
    return next((c for c in countries if c.code and c.code.upper() == code.upper()), None)

def find_country_by_name(countries: List[Country], name: str) -> Optional[Country]:
    """Поиск страны по названию"""
    return next((c for c in countries if c.name.lower() == name.lower()), None)

def get_countries_with_flags(countries: List[Country]) -> List[Country]:
    """Получение только стран с флагами"""
    return [c for c in countries if c.flag]

def group_countries_by_region(countries: List[Country]) -> dict:
    """Группировка стран по регионам (если есть в данных)"""
    regions = {}
    for country in countries:
        # Предполагаем, что страны без кода - это регионы
        region = "Other" if country.code else "Regions"
        if region not in regions:
            regions[region] = []
        regions[region].append(country)
    return regions