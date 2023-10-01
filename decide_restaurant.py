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

    logger.info("Search radius: " + str(round((meters / 1609.34), 2)) + " miles")

    restaurants = []
    next_page_token = None

    try:
        while True:

            endpoint = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": coordinates,
                "radius": meters,
                "type": "restaurant",
                "key": APIKEY,
                "open_now": True
            }

            # Excluded types
            excluded_types = ["shopping_mall", "gas_station", "lodging"]
            excluded = False

            if next_page_token:
                params['pagetoken'] = next_page_token
            
            response = requests.get(endpoint, params=params)
            data = response.json()

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

            # Check if there's a next_page_token for more results
            next_page_token = data.get("next_page_token")

            # If there's no next_page_token, exit the loop
            if not next_page_token:
                break

            # If there's a next_page_token, introduce a delay before the next request
            time.sleep(2)

        # After the loop
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
    parser.add_argument("-l", "--list", help="List all restaurants found", action="store_true")

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
    list = args.list

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

        # If list is True, print all restaurants found
        if list:
            if restaurants:
                # Compute maximum lengths for each column
                max_name_len = max(len(restaurant['Name']) for restaurant in restaurants)
                max_addr_len = max(len(restaurant['Address']) for restaurant in restaurants)
                max_rating_len = max(len(str(restaurant['Rating'])) for restaurant in restaurants)
                max_price_len = max(len(str(restaurant['Price Level'])) for restaurant in restaurants)

                # Add some padding (e.g., 5 extra spaces) for better readability
                padding = 5
                max_name_len += padding
                max_addr_len += padding
                max_rating_len += padding
                max_price_len += padding

                print("\nList of restaurants found:\n")

                # Header
                header_format = "{:<{}} | {:<{}} | {:<{}} | {:<{}}"
                print(header_format.format("Name", max_name_len, "Address", max_addr_len, "Rating", max_rating_len, "Price Level", max_price_len))
                print("-" * (max_name_len + max_addr_len + max_rating_len + max_price_len + 10))  # Line separator for clarity

                # Data rows
                row_format = "{:<{}} | {:<{}} | {:<{}} | {:<{}}"
                for restaurant in restaurants:
                    print(row_format.format(
                        restaurant['Name'], max_name_len,
                        restaurant['Address'], max_addr_len,
                        str(restaurant['Rating']), max_rating_len,
                        str(restaurant['Price Level']), max_price_len
                    ))

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