# Restaurant Selector

This script helps users decide on a restaurant based on a given address, distance, price level, and rating. It uses the Google Places API to fetch restaurant details.

## Prerequisites

1. You need to have Python3 installed.
2. Ensure you have the `requests` and `googlemaps` Python libraries. If not, install them using pip:

```bash
pip install requests googlemaps
```

3. Set up the Google Maps API key:
- Sign up for a Google Maps API key.
- Set it as an environment variable named `GOOGLE_MAPS_API_KEY`.

## Usage

To run the script, use the command:

```bash
./decide_restaurant.py -a <address> [-d <distance> -p <price_level> -r <rating> -l]
```

Arguments:
- `-a, --address`: Address where you are searching from (required).
- `-d, --distance`: Distance in miles from the address (optional, default is 5 miles).
- `-p, --price_level`: Price level to look for. Accepted input: 1-4 (optional, 1 being the cheapest, 4 being the most expensive).
- `-r, --rating`: Minimum rating to look for. Accepted input: 1-5 (optional, 1 being the lowest, 5 being the highest).
- `-l, --list`: Lists all restaurants found (optional).

## Features


- **Address to Coordinates Conversion**: Converts a given address into geocoordinates.
- **Dynamic Result Display**: Provides a chart of restaurants with dynamically adjusting column widths based on content.
- **Random Restaurant Selection**: Randomly picks one of the fetched restaurants to suggest.

## Troubleshooting

The script uses logging to provide detailed error messages in case of issues. Ensure your API key is correctly set up and has the necessary permissions for Google Maps and Google Places.


## Contributing

Contributions are welcome! Please open an issue or submit a pull request.