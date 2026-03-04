import random
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Route:
    id: str
    name: str
    weekdays: List[int]  # 1=Пн, 2=Вт...
    exclude: bool = False

@dataclass
class Driver:
    id: str
    name: str
    routes: List[str]
    no_days: List[int] = None
    prefer_big_truck: bool = False

@dataclass
class Truck:
    id: str
    type: str  # 'big' | 'small'
    rate: float

@dataclass
class ScheduleSlot:
    day: int
    route_id: str
    driver_id: Optional[str] = None
    truck_id: Optional[str] = None
    is_manual: bool = False
    is_ai: bool = False

class RouteScheduler:
    def __init__(self, config_path: str = "data/config.json"):
        self.load_config(config_path)
        self.original_schedule = []
    
    def load_config(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.routes = [Route(**r) for r in config['routes'] if not r.get('exclude')]
        self.drivers = [Driver(**d) for d in config['drivers']]
        self.trucks = [Truck(**t) for t in config['trucks']]
        self.blocked_days = config.get('blocked_days', [])
        self.manual_assignments = [ScheduleSlot(**m) for m in config.get('manual_assignments', [])]
    
    def distribute(self, month_days: int = 31) -> List[List[ScheduleSlot]]:
        """Основной метод распределения"""
        self.original_schedule = self._create_base_schedule(month_days)
        
        # Блокируем ручные назначения
        schedule = self._block_manual_assignments(month_days)
        
        # Заполняем по правилам
        schedule = self._fill_schedule(schedule, month_days)
        
        # Балансируем
        schedule = self._balance_assignments(schedule, month_days)
        
        return schedule
    
    def reset(self) -> List[List[ScheduleSlot]]:
        """Вернуть исходное состояние"""
        return self.original_schedule
    
    def _create_base_schedule(self, days: int) -> List[List[ScheduleSlot]]:
        schedule = []
        for day in range(1, days + 1):
            schedule.append([])
        return schedule
    
    def _block_manual_assignments(self, days: int) -> List[List[ScheduleSlot]]:
        schedule = self._create_base_schedule(days)
        
        # Добавляем ручные назначения
        for slot in self.manual_assignments:
            if 1 <= slot.day <= days:
                schedule[slot.day - 1].append(slot)
        
        return schedule
    
    def _fill_schedule(self, schedule: List[List[ScheduleSlot]], days: int) -> List[List[ScheduleSlot]]:
        """Заполнение с учетом ограничений"""
        for day in range(days):
            real_day = day + 1
            if real_day in self.blocked_days:
                continue
                
            weekday = self._get_weekday(2026, 3, real_day)  # Март 2026
            
            # Маршруты на этот день
            day_routes = [r for r in self.routes if weekday in r.weekdays]
            
            for route in day_routes:
                slot = ScheduleSlot(day=real_day, route_id=route.id, is_ai=True)
                
                # Найти подходящего водителя
                driver = self._find_suitable_driver(route.id, real_day)
                if driver:
                    slot.driver_id = driver.id
                    slot.truck_id = self._select_truck(driver, weekday <= 2)
                
                schedule[day].append(slot)
        
        return schedule
    
    def _find_suitable_driver(self, route_id: str, day: int) -> Optional[Driver]:
        """Найти водителя для маршрута"""
        candidates = [
            d for d in self.drivers 
            if route_id in d.routes and day not in (d.no_days or [])
        ]
        return random.choice(candidates) if candidates else None
    
    def _select_truck(self, driver: Driver, prefer_big: bool) -> str:
        """Выбор машины"""
        trucks = [t for t in self.trucks if t.type == 'big'] if prefer_big or driver.prefer_big_truck else self.trucks
        return random.choice(trucks).id
    
    def _get_weekday(self, year: int, month: int, day: int) -> int:
        """День недели: 1=Пн...7=Вс"""
        dt = datetime(year, month, day)
        return dt.isoweekday()
    
    def _balance_assignments(self, schedule: List[List[ScheduleSlot]], days: int) -> List[List[ScheduleSlot]]:
        """Балансировка командировок (заглушка для v1)"""
        return schedule
