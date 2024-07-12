import tkinter as tk
import customtkinter as ctk
import requests
from PIL import Image, ImageTk
import io
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

class GlowLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.glow_frames = []
        self.current_frame = 0
        self.is_glowing = False

    def start_glow(self):
        if not self.is_glowing:
            self.is_glowing = True
            self.glow_animation()

    def stop_glow(self):
        self.is_glowing = False

    def glow_animation(self):
        if self.is_glowing:
            self.current_frame = (self.current_frame + 1) % 20
            glow_intensity = abs((self.current_frame - 10) / 10)
            glow_color = self.rgb_to_hex((int(100 + 155 * glow_intensity), int(100 + 155 * glow_intensity), 255))
            self.configure(text_color=glow_color)
            self.after(50, self.glow_animation)

    @staticmethod
    def rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Weather Forecast")
        self.geometry("500x750")  # Increased height to accommodate copyright        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)  # Make weather frame expandable




        self.setup_ui()

    def setup_ui(self):
        # Search frame
        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.city_entry = ctk.CTkEntry(search_frame, placeholder_text="Enter City")
        self.city_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        search_button = ctk.CTkButton(search_frame, text="Search", command=self.search_weather)
        search_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        # Weather info frame
        self.weather_frame = ctk.CTkFrame(self.main_frame)
        self.weather_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.weather_frame.grid_columnconfigure(0, weight=1)

        self.location_label = GlowLabel(self.weather_frame, text="", font=("Helvetica", 24, "bold"))
        self.location_label.grid(row=0, column=0, padx=10, pady=(20, 10))

        self.weather_icon = ctk.CTkLabel(self.weather_frame, text="")
        self.weather_icon.grid(row=1, column=0, padx=10, pady=10)

        self.weather_label = GlowLabel(self.weather_frame, text="", font=("Helvetica", 18))
        self.weather_label.grid(row=2, column=0, padx=10, pady=5)

        self.temp_label = ctk.CTkLabel(self.weather_frame, text="", font=("Helvetica", 36, "bold"))
        self.temp_label.grid(row=3, column=0, padx=10, pady=5)

        self.wind_label = ctk.CTkLabel(self.weather_frame, text="", font=("Helvetica", 16))
        self.wind_label.grid(row=4, column=0, padx=10, pady=5)

        self.time_label = ctk.CTkLabel(self.weather_frame, text="", font=("Helvetica", 14))
        self.time_label.grid(row=5, column=0, padx=10, pady=(20, 10))

                # Copyright label
        copyright_label = ctk.CTkLabel(self.main_frame, text="© 2024 Daniel Monteiro", font=("Helvetica", 10))
        copyright_label.grid(row=2, column=0, pady=(0, 5), sticky="s")

        # Initially hide the weather frame
        self.weather_frame.grid_remove()

    def get_coordinates(self, city):
        params = {"name": city, "count": 1, "language": "en", "format": "json"}
        response = requests.get(GEOCODING_URL, params=params)
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return result["latitude"], result["longitude"], result["name"], result["country"]
        return None

    def get_weather(self, lat, lon):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "temperature_unit": "celsius",
            "windspeed_unit": "ms",
            "timezone": "auto"
        }
        response = requests.get(WEATHER_URL, params=params)
        data = response.json()
        
        if "current_weather" in data:
            weather = data["current_weather"]
            return {
                "temperature": f"{weather['temperature']}°C",
                "windspeed": f"{weather['windspeed']} m/s",
                "weathercode": weather['weathercode'],
                "time": weather['time']
            }
        return None

    def get_weather_description(self, code):
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")

    def get_weather_icon(self, code):
        if code == 0:
            icon_name = "01d"  # Clear sky
        elif code in [1, 2, 3]:
            icon_name = "02d"  # Partly cloudy
        elif code in [45, 48]:
            icon_name = "50d"  # Fog
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            icon_name = "10d"  # Rain
        elif code in [71, 73, 75, 77, 85, 86]:
            icon_name = "13d"  # Snow
        elif code in [95, 96, 99]:
            icon_name = "11d"  # Thunderstorm
        else:
            icon_name = "03d"  # Default to cloudy
        
        icon_url = f"http://openweathermap.org/img/wn/{icon_name}@2x.png"
        response = requests.get(icon_url)
        icon_data = response.content
        icon_image = Image.open(io.BytesIO(icon_data))
        return ImageTk.PhotoImage(icon_image)

    def search_weather(self):
        city = self.city_entry.get()
        if not city:
            self.show_error("Please enter a city name.")
            return

        coord_data = self.get_coordinates(city)
        if coord_data:
            lat, lon, city_name, country = coord_data
            weather_data = self.get_weather(lat, lon)
            if weather_data:
                self.update_weather_display(city_name, country, weather_data)
            else:
                self.show_error("Unable to fetch weather data. Please try again.")
        else:
            self.show_error("City not found. Please check the spelling and try again.")

    def update_weather_display(self, city_name, country, weather_data):
        self.weather_frame.grid()
        self.location_label.configure(text=f"{city_name}, {country}")
        self.location_label.start_glow()
        
        weather_icon_img = self.get_weather_icon(weather_data['weathercode'])
        self.weather_icon.configure(image=weather_icon_img)
        self.weather_icon.image = weather_icon_img
        
        weather_description = self.get_weather_description(weather_data['weathercode'])
        self.weather_label.configure(text=weather_description)
        self.weather_label.start_glow()
        
        self.temp_label.configure(text=weather_data['temperature'])
        self.wind_label.configure(text=f"Wind Speed: {weather_data['windspeed']}")
        
        time = datetime.fromisoformat(weather_data['time'])
        self.time_label.configure(text=f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.animate_weather_display()

    def animate_weather_display(self):
        def fade_in(widget, alpha=0):
            if alpha < 1:
                alpha += 0.1
                widget.configure(fg_color=self.blend_colors("#1a1a1a", "#2b2b2b", alpha))
                self.after(50, lambda: fade_in(widget, alpha))
        
        fade_in(self.weather_frame)

    @staticmethod
    def blend_colors(color1, color2, alpha):
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 * (1 - alpha) + r2 * alpha)
        g = int(g1 * (1 - alpha) + g2 * alpha)
        b = int(b1 * (1 - alpha) + b2 * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"

    def show_error(self, message):
        ctk.CTkMessagebox(title="Error", message=message, icon="cancel")

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
