import requests
import json
from datetime import datetime #Импорт библиотек

API_TOKEN = "3ed0654ca8f65a12619b20e515b80555"
API_TOKEN2 = "7c280f4aed266e99b0b34ec56068281dfc95babef084a39a87dfb2446a6b1030"
URL = "http://api.openweathermap.org"
URL2 = "https://api.ambeedata.com/latest/by-lat-lng"
Coord_add_url = '/geo/1.0/direct'
Weather_add_url = '/data/2.5/weather'
Language = 'ru' # Объявления констант для работы с API


def fetch_coordinates(city_name, country_name, api_token): #Функция полученяи координат города
    params = {
        'q': f'{city_name},{country_name}',
        'limit': 1, # Первое совпадение результатов поиска
        'appid': api_token
    }
    url = f'{URL}{Coord_add_url}' # Полный url для поиска координат
    try: # Блок обработки ошибок при запросе данных
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            print("Ошибка: API вернул пустой ответ для координат.")
            return None
        return data[0]['lat'], data[0]['lon'] # Возвращаем долготу и широту
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе координат: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Ошибка обработки ответа координат API: {e}. Неверный формат данных.")
        return None


def fetch_weather_data(latitude, longitude, api_token, language=Language):

    params = { # Словарь параметров запрос API
        'lat': latitude,
        'lon': longitude,
        'units': 'metric',
        'appid': api_token,
        'lang': language
    }
    url = f'{URL}{Weather_add_url}' # Полный url для получения данных погоды
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Проверяем статус запроса, иначе выдаем сообщение об ошибке
        weather_data = response.json()
        if not weather_data:
            print("Ошибка: Сервис вернул пустой ответ")
            return None
        return weather_data # Возвращаем json формат
    except requests.exceptions.RequestException:
        print(f"Ошибка при запросе данных о погоде")
        return None
    except json.JSONDecodeError:
        print(f"Ошибка декодирования json ответа погоды")
        return None



def format_weather_output(weather_data): # Функция обработки полученной информации, полученной в формате словаря
    if not weather_data:
        return "Нет данных о погоде для форматирования."
    try:
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        condition_description = weather_data['weather'][0]['description'].capitalize() # Извлекаем температуру, влажность, давление, облачность

        output_result = ( # Отформатированный ответ
            f"Температура: {temperature}°C\n"
            f"Состояние: {condition_description}\n"
            f"Влажность: {humidity}%\n"
            f"Давление: {pressure} гПа"
        )
        return output_result
    except KeyError:
        return "Ошибка: Неполные или некорректные данные о погоде от API."


def fetch_air_quality_Ambee(lat, lng, api_key, base_url):

    headers = {'x-api-key': api_key}
    params = {'lat': lat, 'lng': lng}

    try:
        response = requests.get(base_url, headers=headers, params=params)
        #print(type(response))
        response.raise_for_status()  # Проверяем, что запрос успешен
        #print(type(response))
        #print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None


def format_air_quality_report_Ambee(air_data, lat, lng): #Формируем отчет качества воздуха

    if not air_data or 'stations' not in air_data or not air_data['stations']:
        return "Данные о качестве воздуха недоступны."

    station = air_data['stations'][0]

    report = [f"{'-'*50}",
        "ДАННЫЕ О КАЧЕСТВЕ ВОЗДУХА (Ambee)"]

    if station.get('CO'):
        report.append(f"CO: {station['CO']}")
    if station.get('NO2'):
        report.append(f"NO2: {station['NO2']}")
    if station.get('OZONE'):
        report.append(f"O3: {station['OZONE']}")
    if station.get('AQI'):
        category = station.get('aqiInfo', {}).get('category', '')
        report.append(f"Индекс AQI: {station['AQI']}" +
                      (f"({category})" if category else ""))

    return "\n".join(report)

if __name__ == "__main__":
    city_name = input(f"Введите название города: ")
    country_name = input(f"Введите название страны: ") # Ввод страны и города для запроса

    print(f"\nЗапрос погоды для: {city_name}, {country_name}")

    coordinates = fetch_coordinates(city_name, country_name, API_TOKEN) # Запрос координаты города
    if not coordinates:
        print("Не удалось получить координаты. Проверьте название города/страны и API-ключ.")

    latitude, longitude = coordinates  # Полученные широта и долгота
    weather_data = fetch_weather_data(latitude, longitude, API_TOKEN)
    if not weather_data:
        print("Не удалось получить данные о погоде. Проверьте API-ключ и интернет-соединение.")


    formatted_weather = format_weather_output(weather_data)
    print(formatted_weather)
    air_data = fetch_air_quality_Ambee(latitude, longitude, API_TOKEN2, URL2) #Получаем данные о качестве воздуха 

    if air_data:
        report = format_air_quality_report_Ambee(air_data, latitude, longitude)
        print(report)