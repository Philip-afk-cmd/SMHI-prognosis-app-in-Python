import requests
from datetime import datetime
from collections import defaultdict

CITIES = {
    "Vallentuna": (59.5386, 18.0833),
    "Upplands Väsby": (59.5250, 17.9500),
    "Stockholm": (59.3293, 18.0686),
    "Göteborg": (57.7089, 11.9746),
    "Malmö": (55.6050, 13.0038),
    "Uppsala": (59.8586, 17.6389),
    "Linköping": (58.4108, 15.6214),
    "Örebro": (59.2753, 15.2134),
    "Västerås": (59.6099, 16.5448),
    "Umeå": (63.8258, 20.2630),
    "Luleå": (65.5848, 22.1547),
    "Kiruna": (67.8558, 20.2253),
    "Östersund": (63.1792, 14.6357),
}

WEATHER_SYMBOLS = {
    1: ("☀️", "Klart"),
    2: ("🌤️", "Lätt molnighet"),
    3: ("⛅", "Halvklart"),
    4: ("🌥️", "Molnigt"),
    5: ("☁️", "Mycket moln"),
    6: ("☁️", "Mulet"),
    7: ("🌫️", "Dimma"),
    8: ("🌦️", "Lätt regnskur"),
    9: ("🌧️", "Regnskur"),
    10: ("⛈️", "Kraftig regnskur"),
    11: ("⛈️", "Åskskur"),
    12: ("🌨️", "Lätt by av regn och snö"),
    13: ("🌨️", "By av regn och snö"),
    14: ("🌨️", "Kraftig by av regn och snö"),
    15: ("❄️", "Lätt snöby"),
    16: ("❄️", "Snöby"),
    17: ("❄️", "Kraftig snöby"),
    18: ("🌦️", "Lätt regn"),
    19: ("🌧️", "Regn"),
    20: ("🌧️", "Kraftigt regn"),
    21: ("⚡", "Åska"),
    22: ("🌨️", "Lätt snöblandat regn"),
    23: ("🌨️", "Snöblandat regn"),
    24: ("🌨️", "Kraftigt snöblandat regn"),
    25: ("❄️", "Lätt snöfall"),
    26: ("❄️", "Snöfall"),
    27: ("❄️", "Ymnigt snöfall"),
}

WEEKDAYS_SV = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]

def get_symbol_info(code):
    return WEATHER_SYMBOLS.get(int(code), ("🌡️", "Okänt väder"))

def fetch_weather(lat, lon):
    url = (
        f"https://opendata-download-metfcst.smhi.se/api/category/snow1g/"
        f"version/1/geotype/point/lon/{round(lon, 4)}/lat/{round(lat, 4)}/data.json"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    raw_data = response.json()

    time_series = raw_data.get("timeSeries", [])
    hourly_forecast = []
    daily_groups = defaultdict(list)

    for entry in time_series:
        time_str = entry.get("time")
        data = entry.get("data", {})

        temp = data.get("air_temperature")
        wind = data.get("wind_speed")
        precip = data.get("precipitation_amount_mean", 0.0)
        symbol = data.get("symbol_code", 1)

        if temp is None or temp == 9999:
            continue

        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00")).astimezone()
        icon, desc = get_symbol_info(symbol)

        item = {
            "dt": dt,
            "hour": dt.strftime("%H:%M"),
            "date_key": dt.strftime("%Y-%m-%d"),
            "weekday": WEEKDAYS_SV[dt.weekday()],
            "temp": round(temp),
            "temp_exact": round(temp, 1),
            "wind": round(wind, 1) if wind not in (None, 9999) else 0.0,
            "precip": round(precip, 1) if precip not in (None, 9999) else 0.0,
            "symbol": int(symbol) if symbol != 9999 else 1,
            "icon": icon,
            "desc": desc,
        }
        hourly_forecast.append(item)
        daily_groups[item["date_key"]].append(item)

    daily_forecast = []
    for idx, (date_key, items) in enumerate(list(daily_groups.items())[:10]):
        temps = [x["temp"] for x in items]
        total_precip = round(sum(x["precip"] for x in items), 1)
        max_wind = max(x["wind"] for x in items)

        mid_item = next((x for x in items if x["dt"].hour in (12, 13, 14)), items[len(items) // 2])
        day_label = "Idag" if idx == 0 else ("Imorgon" if idx == 1 else mid_item["weekday"])

        daily_forecast.append({
            "day": day_label,
            "date": mid_item["dt"].strftime("%d/%m"),
            "icon": mid_item["icon"],
            "desc": mid_item["desc"],
            "min_temp": min(temps),
            "max_temp": max(temps),
            "precip": total_precip,
            "wind": max_wind,
        })

    return {
        "current": hourly_forecast[0] if hourly_forecast else None,
        "hourly": hourly_forecast[:24],
        "daily": daily_forecast,
    }
