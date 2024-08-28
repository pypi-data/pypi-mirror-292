import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from typing import Final as Constant
from taxi_data.get_job_list import get_job_list
from taxi_data.make_gps_data_from_playback import make_raw_data_from_playback, parse_raw_gps_data
from taxi_data.classes import GpsJob, Coordinates_with_timestamps, Job, GpsData

async def retrieve_jobs(shift_date: str) -> List[Job]:
    return await asyncio.to_thread(get_job_list, shift_date)

async def retrieve_coordinates(shift_date: str, update_interval: int) -> List[GpsData]:
#    file_path, events = await asyncio.to_thread(get_kml_file, shift_date)
#    return await asyncio.to_thread(parse_kml, file_path, update_interval, events)
    raw_data = await asyncio.to_thread(make_raw_data_from_playback, datetime.strptime(shift_date, '%d/%m/%Y'))
#    raw_data: List[str] = ['CC888-63677\n2024-08-18 10:40:04\nMileage:0.00km\nLat:-27.95421,Lon:153.35261\nPosition Type:GPS\nDirection:East,Speed:5.00km/h\n  ', 'CC888-63677\n2024-08-18 10:40:18\nMileage:0.05km\nLat:-27.95455,Lon:153.35288\nPosition Type:GPS\nDirection:South,Speed:34.00km/h\n  ', 'CC888-63677\n2024-08-18 10:40:29\nMileage:0.20km\nLat:-27.95589,Lon:153.35323\nPosition Type:GPS\nDirection:South,Speed:52.00km/h\n  ', 'CC888-63677\n2024-08-18 10:40:48\nMileage:0.34km\nLat:-27.95703,Lon:153.35291\nPosition T...PS\nDirection:Northwest ,Speed:30.00km/h\n  ', 'CC888-63677\n2024-08-18 10:40:59\nMileage:0.48km\nLat:-27.95670,Lon:153.35158\nPosition Type:GPS\nDirection:West,Speed:45.00km/h\n  ', 'CC888-63677\n2024-08-18 10:41:10\nMileage:0.61km\nLat:-27.95603,Lon:153.35053\nPosition T...PS\nDirection:Northwest ,Speed:50.00km/h\n  ', 'CC888-63677\n2024-08-18 10:41:21\nMileage:0.74km\nLat:-27.95498,Lon:153.34984\nPosition T...PS\nDirection:Northwest ,Speed:37.00km/h\n  ', 'CC888-63677\n2024-08-18 10:41:43\nMileage:1.00km\nLat:-27.95298,Lon:153.34853\nPosition Type:GPS\nDirection:North,Speed:34.00km/h\n  ', 'CC888-63677\n2024-08-18 10:43:03\nMileage:1.80km\nLat:-27.95126,Lon:153.34674\nPosition Type:GPS\nStop time:2Minute\n  ', 'CC888-63677\n2024-08-18 10:44:38\nMileage:2.80km\nLat:-27.95773,Lon:153.34541\nPosition Type:GPS\nDirection:South,Speed:75.00km/h\n  ', 'CC888-63677\n2024-08-18 10:46:18\nMileage:5.54km\nLat:-27.98111,Lon:153.34208\nPosition Type:GPS\nDirection:South,Speed:91.00km/h\n  ', 'CC888-63677\n2024-08-18 10:48:04\nMileage:8.36km\nLat:-28.00599,Lon:153.34168\nPosition T...PS\nDirection: Southeast,Speed:95.00km/h\n  ', 'CC888-63677\n2024-08-18 10:49:43\nMileage:11.04km\nLat:-28.02796,Lon:153.35138\nPosition Type:GPS\nDirection:South,Speed:91.00km/h\n  ', 'CC888-63677\n2024-08-18 10:52:46\nMileage:11.77km\nLat:-28.03303,Lon:153.35262\nPosition ...PS\nDirection: Southeast,Speed:30.00km/h\n  ', 'CC888-63677\n2024-08-18 10:54:19\nMileage:13.95km\nLat:-28.05219,Lon:153.35661\nPosition Type:GPS\nDirection:South,Speed:99.00km/h\n  ', 'CC888-63677\n2024-08-18 10:56:10\nMileage:16.15km\nLat:-28.07094,Lon:153.36350\nPosition Type:GPS\nStop time:2Minute\n  ', 'CC888-63677\n2024-08-18 10:57:48\nMileage:17.66km\nLat:-28.07198,Lon:153.37698\nPosition Type:GPS\nDirection:West,Speed:10.00km/h\n  ', 'CC888-63677\n2024-08-18 11:07:02\nMileage:17.95km\nLat:-28.07015,Lon:153.37683\nPosition Type:GPS\nDirection:East,Speed:16.00km/h\n  ', 'CC888-63677\n2024-08-18 11:08:21\nMileage:18.68km\nLat:-28.07147,Lon:153.38018\nPosition ...S\nDirection: Northeast ,Speed:48.00km/h\n  ', 'CC888-63677\n2024-08-18 11:09:47\nMileage:19.92km\nLat:-28.06763,Lon:153.39045\nPosition ...S\nDirection: Northeast ,Speed:59.00km/h\n  ', 'CC888-63677\n2024-08-18 11:11:13\nMileage:21.24km\nLat:-28.06036,Lon:153.39432\nPosition Type:GPS\nDirection:North,Speed:66.00km/h\n  ', 'CC888-63677\n2024-08-18 11:13:03\nMileage:23.15km\nLat:-28.04410,Lon:153.38838\nPosition ...PS\nDirection:Northwest ,Speed:37.00km/h\n  ', 'CC888-63677\n2024-08-18 11:14:43\nMileage:25.05km\nLat:-28.02742,Lon:153.38589\nPosition Type:GPS\nDirection:North,Speed:77.00km/h\n  ', 'CC888-63677\n2024-08-18 11:17:00\nMileage:27.27km\nLat:-28.01243,Lon:153.37494\nPosition Type:GPS\nDirection:West,Speed:75.00km/h\n  ', 'CC888-63677\n2024-08-18 11:18:29\nMileage:28.82km\nLat:-28.00331,Lon:153.37470\nPosition ...S\nDirection: Northeast ,Speed:68.00km/h\n  ', 'CC888-63677\n2024-08-18 11:20:23\nMileage:29.45km\nLat:-27.99883,Lon:153.37866\nPosition ...S\nDirection: Northeast ,Speed:48.00km/h\n  ', 'CC888-63677\n2024-08-18 11:22:10\nMileage:31.01km\nLat:-27.98662,Lon:153.38186\nPosition Type:GPS\nDirection:North,Speed:14.00km/h\n  ', 'CC888-63677\n2024-08-18 11:23:49\nMileage:32.11km\nLat:-27.97705,Lon:153.38102\nPosition Type:GPS\nStop time:2Minute\n  ', 'CC888-63677\n2024-08-18 11:26:33\nMileage:33.62km\nLat:-27.96478,Lon:153.37642\nPosition Type:GPS\nDirection:North,Speed:59.00km/h\n  ', 'CC888-63677\n2024-08-18 11:29:06\nMileage:34.29km\nLat:-27.95984,Lon:153.37912\nPosition ...PS\nDirection: Southeast,Speed:48.00km/h\n  ', 'CC888-63677\n2024-08-18 11:30:23\nMileage:34.60km\nLat:-27.95948,Lon:153.37995\nPosition Type:GPS\nStop time:15Minute\n  ', 'CC888-63677\n2024-08-18 11:45:53\nMileage:34.98km\nLat:-27.95746,Lon:153.38058\nPosition ...S\nDirection: Northeast ,Speed:36.00km/h\n  ', 'CC888-63677\n2024-08-18 11:48:23\nMileage:36.21km\nLat:-27.94760,Lon:153.38565\nPosition Type:GPS\nDirection:North,Speed:59.00km/h\n  ', 'CC888-63677\n2024-08-18 11:50:03\nMileage:37.81km\nLat:-27.93443,Lon:153.38982\nPosition Type:GPS\nDirection:West,Speed:54.00km/h\n  ', 'CC888-63677\n2024-08-18 11:51:54\nMileage:39.31km\nLat:-27.93158,Lon:153.37496\nPosition Type:GPS\nStop time:2Minute\n  ', 'CC888-63677\n2024-08-18 11:54:13\nMileage:40.63km\nLat:-27.92769,Lon:153.36238\nPosition Type:GPS\nDirection:West,Speed:14.00km/h\n  ', 'CC888-63677\n2024-08-18 11:58:26\nMileage:40.72km\nLat:-27.92730,Lon:153.36203\nPosition Type:GPS\nStop time:2Minute\n  ', 'CC888-63677\n2024-08-18 12:00:16\nMileage:42.94km\nLat:-27.91896,Lon:153.34205\nPosition Type:GPS\nDirection:West,Speed:59.00km/h\n  ', 'CC888-63677\n2024-08-18 12:01:45\nMileage:44.52km\nLat:-27.92674,Lon:153.32954\nPosition ...PS\nDirection:Northwest ,Speed:61.00km/h\n  ', 'CC888-63677\n2024-08-18 12:03:35\nMileage:47.39km\nLat:-27.90432,Lon:153.31629\nPosition ...pe:GPS\nDirection:North,Speed:104.00km/h\n  ', 'CC888-63677\n2024-08-18 12:05:06\nMileage:50.19km\nLat:-27.87940,Lon:153.31496\nPosition ...pe:GPS\nDirection:North,Speed:106.00km/h\n  ', 'CC888-63677\n2024-08-18 12:06:37\nMileage:52.36km\nLat:-27.86224,Lon:153.30806\nPosition Type:GPS\nDirection:West,Speed:48.00km/h\n  ', 'CC888-63677\n2024-08-18 12:08:17\nMileage:53.44km\nLat:-27.85760,Lon:153.30210\nPosition Type:GPS\nDirection:West,Speed:23.00km/h\n  ', 'CC888-63677\n2024-08-18 12:09:30\nMileage:53.91km\nLat:-27.85699,Lon:153.29899\nPosition Type:GPS\nStop time:2Minute\n  ', 'CC888-63677\n2024-08-18 18:40:25\nMileage:54.12km\nLat:-27.85793,Lon:153.30005\nPosition ...S\nDirection: Northeast ,Speed:32.00km/h\n  ', 'CC888-63677\n2024-08-18 18:41:42\nMileage:54.94km\nLat:-27.85787,Lon:153.30683\nPosition Type:GPS\nDirection:East,Speed:23.00km/h\n  ', 'CC888-63677\n2024-08-18 18:43:32\nMileage:55.76km\nLat:-27.86076,Lon:153.31184\nPosition Type:GPS\nDirection:South,Speed:46.00km/h\n  ', 'CC888-63677\n2024-08-18 18:45:16\nMileage:58.46km\nLat:-27.88471,Lon:153.31600\nPosition Type:GPS\nDirection:South,Speed:45.00km/h\n  ', 'CC888-63677\n2024-08-18 18:46:45\nMileage:58.81km\nLat:-27.88554,Lon:153.31883\nPosition Type:GPS\nDirection:East,Speed:18.00km/h\n  ', 'CC888-63677\n2024-08-18 18:49:28\nMileage:59.02km\nLat:-27.88615,Lon:153.31963\nPosition Type:GPS\nStop time:0Minute\n  ', 'CC888-63677\n2024-08-18 18:52:14\nMileage:59.21km\nLat:-27.88658,Lon:153.31909\nPosition Type:GPS\nDirection:West,Speed:21.00km/h\n  ', 'CC888-63677\n2024-08-18 18:53:45\nMileage:59.87km\nLat:-27.88826,Lon:153.31549\nPosition Type:GPS\nDirection:South,Speed:82.00km/h\n  ', 'CC888-63677\n2024-08-18 18:55:35\nMileage:63.15km\nLat:-27.91676,Lon:153.32123\nPosition ...S\nDirection: Southeast,Speed:104.00km/h\n  ', 'CC888-63677\n2024-08-18 18:57:11\nMileage:66.06km\nLat:-27.93867,Lon:153.33682\nPosition ...pe:GPS\nDirection:South,Speed:104.00km/h\n  ', 'CC888-63677\n2024-08-18 18:58:52\nMileage:68.95km\nLat:-27.96008,Lon:153.35050\nPosition ...S\nDirection: Northeast ,Speed:70.00km/h\n  ', 'CC888-63677\n2024-08-18 19:01:06\nMileage:69.97km\nLat:-27.95184,Lon:153.34670\nPosition ...GPS\nDirection:Northwest ,Speed:5.00km/h\n  ', 'CC888-63677\n2024-08-18 19:02:26\nMileage:70.84km\nLat:-27.95247,Lon:153.34829\nPosition ...PS\nDirection: Southeast,Speed:46.00km/h\n  ', 'CC888-63677\n2024-08-18 19:03:52\nMileage:71.89km\nLat:-27.95420,Lon:153.35270\nPosition Type:GPS\nDirection:North,Speed:9.00km/h\n  ']
    return await asyncio.to_thread(parse_raw_gps_data, raw_data)

async def gather_data(shift_date: str, update_interval: int):
    jobs, coordinates = await asyncio.gather(
        retrieve_jobs(shift_date),
        retrieve_coordinates(shift_date, update_interval)
        )
    return jobs, coordinates

def map_coordinates_by_timestamp(coordinates: List[Coordinates_with_timestamps]) -> Dict[str, Coordinates_with_timestamps]:
    """Map coordinates to their corresponding timestamp for quick lookup."""
    return {coordinate.timestamp.strftime('%H:%M'): coordinate for coordinate in coordinates}

def make_gps_jobs(shift_date: str):
    UPDATE_INTERVAL: Constant[int] = 10

    jobs, coordinates = asyncio.run(gather_data(shift_date, update_interval=UPDATE_INTERVAL))
    
    # Map coordinates by timestamp
    coordinates_dict = map_coordinates_by_timestamp(coordinates)
    gps_jobs: List[GpsJob] = []

    for job in jobs:
        # Handle meter_on time
        meter_on_gps = find_or_interpolate_gps(datetime.combine(datetime.strptime(shift_date, str('%d/%m/%Y')), job.meter_on), coordinates)

        # Handle meter_off time
        meter_off_gps = find_or_interpolate_gps(datetime.combine(datetime.strptime(shift_date, str('%d/%m/%Y')), job.meter_off), coordinates)

        gps_job: GpsJob = GpsJob(meter_off_gps=meter_off_gps, 
                                 meter_on_gps=meter_on_gps,
                                 **job.__dict__)

        gps_jobs.append(gps_job)

    return gps_jobs

def find_or_interpolate_gps(target_time: datetime, coordinates: List[Coordinates_with_timestamps]) -> Optional[Coordinates_with_timestamps]:
    previous_coord = None
    next_coord = None

    # Iterate through the coordinates to find the closest ones before and after the target_time
    for coord in coordinates:
        coord_time = datetime.combine(target_time.date(), coord.timestamp)

        if coord_time == target_time:
            return coord  # Exact match found

        if coord_time < target_time:
            previous_coord = coord
        elif coord_time > target_time:
            next_coord = coord
            break

    # If we have both previous and next coordinates and the previous one has a gap
    if previous_coord and next_coord and previous_coord.gap:
        # Interpolate between previous_coord and next_coord
        return interpolate_coordinates(target_time, previous_coord, next_coord)
    
    # If only one coordinate is found, return it
    return previous_coord if previous_coord else next_coord

def interpolate_coordinates(target_time: datetime, previous_coord: Coordinates_with_timestamps, next_coord: Coordinates_with_timestamps) -> Coordinates_with_timestamps:
    # Calculate the time difference
    total_time_diff = (datetime.combine(target_time.date(), next_coord.timestamp) - 
                       datetime.combine(target_time.date(), previous_coord.timestamp)).total_seconds()

    # Calculate the time difference between the target time and the previous coordinate's time
    elapsed_time = (target_time - datetime.combine(target_time.date(), previous_coord.timestamp)).total_seconds()

    # Calculate the ratio of time passed
    ratio = elapsed_time / total_time_diff if total_time_diff != 0 else 0

    # Interpolate the latitude and longitude
    interpolated_lat = previous_coord.latitude + ratio * (next_coord.latitude - previous_coord.latitude)
    interpolated_lon = previous_coord.longitude + ratio * (next_coord.longitude - previous_coord.longitude)

    # Return the interpolated coordinate
    return Coordinates_with_timestamps(
        longitude=interpolated_lon, 
        latitude=interpolated_lat, 
        timestamp=target_time.time()
    )

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description='Create jobs list with GPS location data')
    parser.add_argument('--date', required=False, help='Date to create data from', default="18/08/2024")
    args, unknown = parser.parse_known_args()

    gps_jobs = make_gps_jobs(shift_date=args.date)
    for job in gps_jobs:
        print(f"{job.booking_id}: Meter on: {job.meter_on}, Meter off: {job.meter_off}, meter on GPS: {job.meter_on_gps}, Meter off GPS: {job.meter_off_gps}")

if __name__ == "__main__":
    main()