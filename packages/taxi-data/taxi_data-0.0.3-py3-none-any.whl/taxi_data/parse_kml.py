import xml.etree.ElementTree as ET
import logging, argparse, pydantic, os
from datetime import timedelta, time, datetime
from typing import List
import time as Time
from os.path import split as split_path
from os.path import basename
from taxi_data.get_kml_file import get_kml_file
from typing import Final as Constant
from classes import Coordinates_with_timestamps, ProcessedEvent, GpsTrackerEvent

# Parse the KML file and extract coordinates with generated timestamps
def parse_kml(file_path: pydantic.FilePath, update_interval: int, events: List[ProcessedEvent]):
    logging.info(f'Parsing KML file: {file_path}')
    with open(file_path, 'r') as file:
        kml_data = file.read()
    
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    root = ET.fromstring(kml_data)
    
    coordinates_with_timestamps: List[Coordinates_with_timestamps] = []

   # Convert start_time (struct_time) to datetime
    file_date = split_path(file_path)[-1]
    file_date = file_date.split('-')
    file_date = f"{file_date[2]}-{file_date[3]}-{file_date[4]}"
    file_date = file_date.split(".")[0]
#    start_time = Time.strptime(start_time, "%H:%M")

    # Extract the filename
    filename = basename(file_path)

    # Split the filename by hyphens and take the last part before the extension
    start_time = Time.strptime(filename.split('-')[-1].split('.')[0],"%H:%M:%S")

    current_time = datetime.combine(datetime.strptime(file_date, '%Y-%m-%d'), time(start_time.tm_hour, start_time.tm_min - 15, start_time.tm_sec))

    # Sort the events list by 'from_time'
    events.sort(key=lambda event: event.from_time)
    
    #    current_time = start_time
    for placemark in root.findall('.//kml:Placemark', namespace):
        for coord in placemark.findall('.//kml:coordinates', namespace):
            coord_text = coord.text.strip()
            coord_pairs = coord_text.split()
            for pair in coord_pairs:
                lon, lat, _ = map(float, pair.split(','))
                coordinates_with_timestamps.append(Coordinates_with_timestamps(longitude=lon, latitude=lat, timestamp=time(hour=current_time.hour, minute=current_time.minute, second=current_time.second)))
                current_time += timedelta(seconds=update_interval)
    
                    # Check if a "Stay" event should be processed
                gap = False
                while events and current_time.time() >= events[0].from_time and current_time.time() < events[0].to_time:
                    event = events.pop(0)
                    if event.event_type == GpsTrackerEvent.STAY:
                        gap = True
                        current_time += event.duration
                        logging.info(f'Stayed for {event.duration}, advancing time to {current_time.time()}')

                coordinates_with_timestamps.append(Coordinates_with_timestamps(
                    longitude=lon, 
                    latitude=lat, 
                    timestamp=time(current_time.hour, current_time.minute, current_time.second),
                    gap=gap
                ))
                current_time += timedelta(seconds=update_interval)

    logging.info(f'Extracted {len(coordinates_with_timestamps)} coordinates from the KML file')
    os.remove(file_path)
    return coordinates_with_timestamps

def main() -> None:
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    parser: argparse = argparse.ArgumentParser(description='Process KML file and calculate travel metrics.')
  #  parser.add_argument('--kml-file', required=False, help='Path to the KML file', default="/home/wayne/Downloads/CC888-63677-2024-08-14-08:44:57.kml")
    parser.add_argument('-d',type=str,required=False,help="date to pull records from",default=None)
    
    args, unknown = parser.parse_known_args()
    
    update_interval: Constant[int] = 10  # Update interval in seconds
    radius: Constant[int] = 15  # Search radius in meters from the point to look for an address
    stationary_threshold: Constant[float] = 0.001  # Threshold distance in km to consider as stationary

    logging.info('Starting the main script')
    
    if args.d is None:
        shift_date = str(input("Enter date (Leave blank for today): "))
    else:
        shift_date = args.d

    file_path, events = get_kml_file(shift_date)

    coordinates_with_timestamps = parse_kml(file_path, update_interval, events)
    for _ in coordinates_with_timestamps:
        print(f"{_.timestamp} {_.latitude},{_.longitude}")

# Main script execution
if __name__ == "__main__":
    main()