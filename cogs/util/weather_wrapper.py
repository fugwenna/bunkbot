"""
Maintainable wrapper class
with dynamic properties that will parse
weather underground json results for weather
"""
class WeatherWrapper:
    def __init__(self, weather, forecast):
        self.credit = "Data provided by http://www.wunderground.com"
        self.set_meta_data(weather)
        self.set_weather(weather)
        self.set_forecast(forecast)

    """
    Discord embedd title to dispaly
    the current location and time
    """
    @property
    def title(self):
        return "Current conditions in {} - {}, {} ".format(self.location, self.week_day, self.time)

    """
    Formatted string to display
    the current conditions
    """
    @property
    def conditions(self):
        message = "Temperature: {}".format(self.temp_actual)
        message += "\nFeels like: {}".format(self.temp_feels)
        message += "\n\nCurrent winds {}".format(self.winds)

        if self.precip > -1:
            message += "\nPrecip accumulated today: {} inches".format(self.precip)

        message += "\n\n {}".format(self.forecast_message)
        
        return message

    """
    Parse the weather result into properties
    """
    def set_weather(self, weather):
        weather_obs = weather["current_observation"]
        self.thumb = weather_obs["icon_url"]
        self.temp_actual = "{} (F)".format(weather_obs["temp_f"])
        self.temp_feels = "{} (F)".format(weather_obs["feelslike_f"])
        self.winds = "{} at {} mph".format(weather_obs["wind_dir"], str(weather_obs["wind_mph"]))
        self.precip = -1

        if weather_obs["precip_today_in"] != "0.00":
            self.precip = str(weather_obs["precip_today_in"])

    """
    Parse the forecast result into properties
    """
    def set_forecast(self, forecast):
        forecast_txt = forecast["forecast"]["txt_forecast"]["forecastday"]
        forecast_simple = forecast["forecast"]["simpleforecast"]["forecastday"]
        self.forecast_message = ""

        for day in range(0, 4):
            fs = forecast_simple[day]
            ft = forecast_txt[day*2]
            ftt = forecast_txt[(day*2)+1]

                
            if day == 0:
                date = ""
                the_day = "Today:"
                the_night = "Tonight:"
                self.week_day = fs["date"]["weekday"]
            else:
                date = "{}, ({}/{})".format(fs["date"]["weekday"], fs["date"]["month"], fs["date"]["day"])
                the_day = ""
                the_night = ftt["title"]
                self.forecast_message += date + "\n-----\n"

            self.forecast_message += "{} {}\n{} {}".format(the_day, ft["fcttext"], the_night, ftt["fcttext"])

            if day < 3:
                self.forecast_message += "\n\n\n"

    """
    Parse the meta data result into properties
    """
    def set_meta_data(self, metadata):
        meta_obs = metadata["current_observation"]
        self.location = meta_obs["display_location"]["full"]
        self.time = " ".join(meta_obs["observation_time"].split(" ")[3:7])
        self.wu_icon = meta_obs["image"]["url"] 
