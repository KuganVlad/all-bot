from geopy.geocoders import Nominatim, options
from geopy.distance import geodesic
import certifi
import ssl


def find_nearest_city(target_city_name):
    ctx = ssl.create_default_context(cafile=certifi.where())
    options.default_ssl_context = ctx
    # Получение координат заданного города
    geolocator = Nominatim(user_agent="all_models")
    target_location = geolocator.geocode(target_city_name)
    target_coordinates = (target_location.latitude, target_location.longitude)

    # Список городов Беларуси с известными координатами
    cities = [
        {"name": "Минск", "coordinates": (53.9045, 27.5615)},
        {"name": "Гродно", "coordinates": (53.6698, 23.8223)},
        {"name": "Брест", "coordinates": (52.0976, 23.7340)},
        {"name": "Гомель", "coordinates": (52.4411, 30.9878)},
        {"name": "Могилев", "coordinates": (53.9007, 30.3313)},
        {"name": "Витебск", "coordinates": (55.1848, 30.2016)},
        {"name": "Пинск", "coordinates": (52.1124, 26.0634)},
        {"name": "Барановичи", "coordinates": (53.1255, 26.0091)},
        {"name": "Мозырь", "coordinates": (52.0322, 29.2223)},
    ]

    # Рассчитываем расстояние до каждого города и находим ближайший
    nearest_city = None
    min_distance = float("inf")
    for city in cities:
        distance = geodesic(target_coordinates, city["coordinates"]).kilometers
        if distance < min_distance:
            min_distance = distance
            nearest_city = city["name"]

    return nearest_city


