#!/bin/python3

import requests
import argparse
import sys
import logging
import time
import random
import googlemaps
import os
import traceback

def get_logger():
    """
    Configures and returns a logger object.
    """
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO
    )
    return logging.getLogger("Default")

def log_error(message, e):
    """
    Logs the detailed error message along with the traceback information.
    """
    # Generate traceback information
    tb_info = traceback.extract_tb(e.__traceback__)
    for entry in reversed(tb_info):
        file_name = entry.filename
        if os.path.basename(__file__) in file_name:
            line_number = entry.lineno
            func_name = entry.name
            break
    error_message = f"{type(e).__name__}: {e.args}"
    raise Exception(f"{message}\nFileName: {file_name}\nLineNumber: {line_number}\nFunction: {func_name}\nReason: {error_message}")

def get_current_location():
    """
    Obtains the current geolocation based on IP address.
    """
    try:
        current_location_url = "https://ipinfo.io/json"
        current_location_response = requests.get(current_location_url)
        current_location = current_location_response.json()
        return current_location["loc"]
    except Exception as e:
        log_error("Error getting current location", e)

def convert_address_to_coordinates(address):
    """
    Converts an address to geocoordinates and returns the coordinates and ZIP code.
    """
    try:
        gmaps = googlemaps.Client(key=APIKEY)
        geocode_result = gmaps.geocode(address)
        latitude = geocode_result[0]["geometry"]["location"]["lat"]
        longitude = geocode_result[0]["geometry"]["location"]["lng"]
        return f"{latitude},{longitude}", geocode_result[0]["address_components"][7]["long_name"]
    except Exception as e:
        log_error("Error converting address to coordinates", e)

def convert_miles_to_meters(miles):
    """
    Converts miles to meters.
    """
    try:
        return int(float(miles) * 1609.34)
    except Exception as e:
        log_error("Error converting miles to meters", e)

def find_restaurant(coordinates, meters, price_level, rating=None):
    """
    Finds nearby restaurants based on geocoordinates, radius in meters, and optional price level and rating.
    """

    restaurants = []
    next_page_token = None

    try:
        while True:
            endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": coordinates,
                "radius": 1000000,
                "type": "restaurant",
                "key": APIKEY,
                "open_now": True
            }

            # Excluded types
            excluded_types = ["shopping_mall", "gas_station", "lodging"]
            excluded = False
            
            response = requests.get(endpoint, params=params)
            data = response.json()

            if next_page_token:
                    params['pagetoken'] = next_page_token
                    next_page_token = params.get("pagetoken")

            for place in data["results"]:
                # Filter out excluded types
                for type in place['types']:
                    if type in excluded_types:
                        excluded = True

                if excluded == True:
                    continue
                
                # Extract price level and rating information
                place_price_level = place.get('price_level', None)
                place_rating = place.get('rating', None)

                # Apply filters based on the provided price level and rating
                if (price_level is None or (place_price_level is not None and place_price_level == int(price_level))) and \
                (rating is None or (place_rating is not None and place_rating >= float(rating))):
                    
                    restaurant = {
                        'Name': place['name'],
                        'Address': place['vicinity'],
                        'Rating': str(place_rating) + "/5" if place_rating is not None else 'N/A',
                        'Price Level': str(place_price_level) + "/4" if place_price_level is not None else 'N/A'
                    }
                    restaurants.append(restaurant)

                # If there are more than 20 results, get the next page of results
                next_page_token = data.get("next_page_token")

                if not next_page_token:
                    break


            if restaurants:
                logger.info("Restaurants found: " + str(len(restaurants)))
                random.shuffle(restaurants)
                return restaurants
            else:
                return "No restaurants found"

    except Exception as e:
        log_error("Error finding restaurants", e)



def select_random_restaurant(restaurants):
    """Select a random restaurant from the list of restaurants"""
    selected_restaurant = random.choice(restaurants)

    return selected_restaurant

def get_parameters():
    parser = argparse.ArgumentParser(description="Purpose: Help decide on a restaurant")
    parser.add_argument("-a", "--address",  help="Address where you are searching for", required=True)
    parser.add_argument("-d", "--distance", help="Distance in miles from address", required=False)
    parser.add_argument("-p", "--price_level", help="Price level to look for. Accepted input: 1-4 (1 being cheapest, 4 being most expensive)")
    parser.add_argument("-r", "--rating", help="Minimum rating to look for. Accepted input: 1-5 (1 being lowest, 5 being highest)")

    """If ran without arguments, print help menu"""
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    return args

def main():
    
    args = get_parameters()

    address = args.address
    distance = args.distance
    price_level = args.price_level
    rating = args.rating

    print("")

    try:
        coordinates = convert_address_to_coordinates(address)

        if distance:
            distance = convert_miles_to_meters(distance)
        else:
            distance = 8046.72 # Default distance is 5 miles (8046.72 meters)

        logger.info("Finding restaurants near: " + address)
        restaurants = find_restaurant(coordinates, distance, price_level, rating)
        
        if restaurants == "No restaurants found":
            logger.info("No restaurants found")
        else:
            selected_restaurant = select_random_restaurant(restaurants)
            print("\nYou should go to: " + selected_restaurant['Name'])
            print("Address: " + selected_restaurant['Address'])
            print("Rating: " + str(selected_restaurant['Rating']))
            print("Price Level: " + str(selected_restaurant['Price Level']))
    except Exception as e:
        log_error("Error in main", e)

if __name__ == "__main__":
    start_time = time.time()    
    """setup logging"""
    logger = get_logger()

    APIKEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")  # Get API Key from environment variable
    if not APIKEY:
        logger.error("API Key not found. Exiting...")
        sys.exit(1)
    main()
    print("")
    logger.info("Completed in: %s seconds" % (time.time() - start_time))