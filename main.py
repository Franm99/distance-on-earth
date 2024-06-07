import folium
import math
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from rich.prompt import Prompt


def get_coords_from_location(geolocator, location):
    """
    Retrieves latitude and longitude for a given location (city, address, country, etc).

    :param geolocator:
    :param location:
    :return:
    """
    data = geolocator.geocode(location)
    if not data:
        return None
    else:
        return data.latitude, data.longitude


def ask_location(geolocator, number: int) -> tuple[str, tuple[float, float]]:
    """
    Asks the user for a location (city, address, country).
    The user is asked until he gives a valid location.

    :param geolocator:
    :param number:
    :return:
    """
    while True:
        location = input(f"Location {number}: ")
        coords = get_coords_from_location(geolocator, location)
        if coords is None:
            print(f"Could not find '{location}'. Try again.")
        else:
            print(f" -> Location {number}: '{location}' - {coords}")
            return location, coords


def compute_distance(coords1: tuple[float, float], coords2: tuple[float, float], units: str) -> float:
    """
    Computes distance between two coordinates in the Earth surface.
    coords1 and coords2
    :param coords1:
    :param coords2:
    :param units:
    :return:
    """
    return eval(f"geodesic({coords1}, {coords2}).{units}")


def compute_midpoint(coords1: tuple[float, float], coords2: tuple[float, float]) -> tuple[float, float]:
    """
    Computes the midpoint on the Earth surface given two coordinates.

    Midpoint is computed by converting from Cartesian to Spherical coordinates.
    :param coords1:
    :param coords2:
    :return:
    """
    lat1, lon1 = coords1
    lat2, lon2 = coords2

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    d_lon = math.radians(lon2 - lon1)
    lon1 = math.radians(lon1)

    bx = math.cos(lat2) * math.cos(d_lon)
    by = math.cos(lat2) * math.sin(d_lon)

    lat3 = math.atan2(
        math.sin(lat1) * math.sin(lat2),
        math.sqrt((math.cos(lat1) + bx) * (math.cos(lat1) + bx) + by * by)
    )

    lon3 = lon1 + math.atan2(by, math.cos(lat1) + bx)

    return math.degrees(lat3), math.degrees(lon3)


def create_map_and_center(
        coords1: tuple[float, float],
        coords2: tuple[float, float],
        midpoint: tuple[float, float]
) -> folium.Map:
    """
    Retrieves a Folium map instance that is centered in the midpoint of the two given sets of coordinates,
    and adjusts the zoom so the distance is fully displayed.

    It also draws a line to join the two given points in the map.

    :param coords1:
    :param coords2:
    :param midpoint:
    :return:
    """
    map_ = folium.Map(midpoint)
    sw = min(coords1[0], coords2[0]), min(coords1[1], coords2[1])
    ne = max(coords1[0], coords2[0]), max(coords1[1], coords2[1])
    map_.fit_bounds(bounds=[sw, ne])

    line = folium.PolyLine([coords1, coords2], weight=3, color="#FF0000")
    map_.add_child(line)
    return map_


if __name__ == '__main__':
    geolocator = Nominatim(user_agent="Distance")

    loc1, loc1_coords = ask_location(geolocator, 1)
    loc2, loc2_coords = ask_location(geolocator, 2)
    units = Prompt.ask("Choose units", choices=["km", "ft", "m", "mi"], default="km")

    distance = compute_distance(loc1_coords, loc2_coords, units=units)
    midpoint = compute_midpoint(loc1_coords, loc2_coords)
    print(f"Distance between '{loc1}' and '{loc2}':", "%.2f %s" % (distance, units))

    map_ = create_map_and_center(loc1_coords, loc2_coords, midpoint)
    map_.save("map.html")

