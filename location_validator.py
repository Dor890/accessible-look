import os
import requests

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.distance import geodesic


def get_exif_data(image_path):
    """
    Extracts and returns the EXIF data from an image file as a dictionary,
    mapping EXIF tags to their respective values. If no EXIF data is found,
    an empty dictionary is returned.
    """
    image = Image.open(image_path)
    exif_data = image._getexif()
    if not exif_data:
        return {}
    exif = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    return exif


def get_gps_info(exif_data):
    """
    Extracts GPS information from EXIF data.
    """
    if 'GPSInfo' not in exif_data:
        return None
    gps_info = exif_data['GPSInfo']
    gps_data = {}
    for key in gps_info.keys():
        decode = GPSTAGS.get(key, key)
        gps_data[decode] = gps_info[key]
    return gps_data


def convert_to_degrees(value):
    """
    Converts GPS coordinates from decimal degrees format to floating-point degrees.
    """
    d = float(value[0])
    m = float(value[1]) / 60.0
    s = float(value[2]) / 3600.0
    return d + m + s


def get_lat_lon(gps_data):
    """
    Extracts latitude and longitude from GPS data. Returns a tuple of (latitude, longitude) or None if not found.
    """
    lat = None
    lon = None
    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
        lat = convert_to_degrees(gps_data['GPSLatitude'])
        lon = convert_to_degrees(gps_data['GPSLongitude'])
        if gps_data['GPSLatitudeRef'] != 'N':
            lat = -lat
        if gps_data['GPSLongitudeRef'] != 'E':
            lon = -lon
    return lat, lon


def geocode_location_google(location_name):
    """
    Geocodes a location using Google Maps API. Returns a tuple of (latitude, longitude) or None if geocoding fails.
    """
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("Google Maps API key not found. Set the environment variable GOOGLE_MAPS_API_KEY.")
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = response.json().get("results")
        if results:
            location = results[0]["geometry"]["location"]
            return (location["lat"], location["lng"])
        else:
            print("Geocoding API response was successful but no results found.")
            print("Response:", response.json())
    else:
        print(f"Geocoding API request failed with status code: {response.status_code}")
        print("Response:", response.json())
    return None


def is_within_margin(coord1, coord2, margin_km=10):
    """
    Checks if two coordinates are within a specified distance in kilometers. Returns True if within margin, False otherwise.
    """
    distance = geodesic(coord1, coord2).kilometers
    return distance <= margin_km


def validate_photo_in_place(image_path, business_location):
    """
    Validates if a photo was taken near a specified location. Returns True if likely taken at the location, False otherwise.
    """
    exif_data = get_exif_data(image_path)
    gps_data = get_gps_info(exif_data)
    if gps_data:
        image_coords = get_lat_lon(gps_data)

        geocoded_coords = geocode_location_google(business_location)

        if geocoded_coords:
            # print(f"Geocoded Coordinates: {geocoded_coords}")

            # Check if the coordinates are within 1 km margin
            if is_within_margin(image_coords, geocoded_coords):
                # The image was likely taken at the specified location.
                return True
            else:
                # The image was likely not taken at the specified location.
                return False
        else:
            # Location name could not be geocoded.
            return True
    else:
        # No GPS data found in the image.
        return True


def main():  # POC
    # Example image path
    image_path = r"C:\Users\dmessica\Downloads\IMG_20240616_144700.jpg"
    exif_data = get_exif_data(image_path)
    gps_data = get_gps_info(exif_data)
    if gps_data:
        image_coords = get_lat_lon(gps_data)
        print(f"Extracted Image Coordinates: {image_coords}")

        # Example location name
        location_name = "ארומה, האוניברסיטה העברית, ירושלים"
        geocoded_coords = geocode_location_google(location_name)

        if geocoded_coords:
            print(f"Geocoded Coordinates: {geocoded_coords}")

            # Check if the coordinates are within 1 km margin
            if is_within_margin(image_coords, geocoded_coords):
                print("The image was likely taken at the specified location.")
            else:
                print("The image was likely not taken at the specified location.")
        else:
            print("Location name could not be geocoded.")
    else:
        print("No GPS data found in the image.")


if __name__ == '__main__':
    main()
