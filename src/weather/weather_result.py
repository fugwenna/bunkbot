from typing import List

"""
Model that maps the json result into a more readable object
"""
class WeatherResult:
    def __init__(self, result: dict):
        self.city: str = result["name"]
        self.weather: dict = result["weather"][0]
        self.main: dict = result["main"]
        self.coord_x: int = result["coord"]["lon"]
        self.coord_y: int = result["coord"]["lat"]


    @property
    def icon_url(self) -> str:
        return self.weather["icon"]


    @property
    def weather_temp(self) -> str:
        return self.main["temp"]

    
    @property
    def weather_feels_like(self) -> str:
        return self.main["feels_like"]


    @property
    def weather_min(self) -> str:
        return self.main["temp_min"]


    @property
    def weather_max(self) -> str:
        return self.main["temp_max"]


    @property
    def weather_humidity(self) -> str:
        return self.main["humidity"]
