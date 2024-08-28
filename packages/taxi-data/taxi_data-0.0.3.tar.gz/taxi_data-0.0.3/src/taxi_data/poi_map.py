from typing import List, Generator
from taxi_data.make_gps_jobs import make_gps_jobs
from classes import GpsJob
import os, calendar, datetime
from typing import List as Constant
import argparse

# Generator function to generate each day in a given date range within a specific month
def generate_days_in_month(year: int, month: int, start_day: int, end_day: int) -> Generator[str, None, None]:
    # Ensure that the start_day and end_day are valid
    _, num_days = calendar.monthrange(year, month)
    if start_day < 1 or end_day > num_days or start_day > end_day:
        raise ValueError("Invalid start or end day for the given month")

    # Generate dates from start_day to end_day
    current_date = datetime.date(year, month, start_day)
    end_date = datetime.date(year, month, end_day)

    while current_date <= end_date:
        yield current_date.strftime("%d/%m/%Y")
        current_date += datetime.timedelta(days=1)

def create_kml(jobs: List[GpsJob]) -> str:
    kml_data = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<kml xmlns="http://www.opengis.net/kml/2.2">',
                '<Document>']
    # Define styles for the pins
    kml_data.extend([
        '<Style id="meterOnStyle">',
        '<IconStyle>',
        '<color>ff00ff00</color>',  # Green color (KML color is in aabbggrr format)
        '<Icon>',
        '<href>http://maps.google.com/mapfiles/kml/paddle/grn-blank.png</href>',
        '</Icon>',
        '</IconStyle>',
        '</Style>',
        
        '<Style id="meterOffStyle">',
        '<IconStyle>',
        '<color>ff0000ff</color>',  # Red color (KML color is in aabbggrr format)
        '<Icon>',
        '<href>http://maps.google.com/mapfiles/kml/paddle/red-blank.png</href>',
        '</Icon>',
        '</IconStyle>',
        '</Style>'
    ])

    for job in jobs:
        if job.meter_on_gps and job.meter_on_gps.latitude and job.meter_on_gps.longitude:
            kml_data.extend([
                '<Placemark>',
                '<styleUrl>#meterOnStyle</styleUrl>',  # Apply the green style
                f'<name>{job.booking_id}</name>',
                f'<description>{job.pick_up_suburb}</description>',
                '<Point>',
                f'<coordinates>{job.meter_on_gps.longitude},{job.meter_on_gps.latitude},0</coordinates>',
                '</Point>',
                '</Placemark>'
            ])
        
        if job.meter_off_gps and job.meter_off_gps.latitude and job.meter_off_gps.longitude:
            kml_data.extend([
                '<Placemark>',
                '<styleUrl>#meterOffStyle</styleUrl>',  # Apply the red style
                f'<name>{job.booking_id}</name>',
                f'<description>{job.destination_suburb}</description>',
                '<Point>',
                f'<coordinates>{job.meter_off_gps.longitude},{job.meter_off_gps.latitude},0</coordinates>',
                '</Point>',
                '</Placemark>'
            ])
    
    kml_data.append('</Document>')
    kml_data.append('</kml>')
    
    return '\n'.join(kml_data)


def main() -> None:
    # year: Constant[int] = datetime.date.today().year
    # month: Constant[int] = datetime.date.today().month
    start_day: Constant[int] = 27
    end_day: Constant[int] = 27



    parser = argparse.ArgumentParser(description='Retrives GPS trace from web portal and creates accurate coordinates and adds GPS loctions to meter on and off')
    parser.add_argument('--year',type=int,required=False,help="year to generate dates from",default=datetime.date.today().year)
    parser.add_argument('--month',type=int,required=False,help="month to generate dates from",default=datetime.date.today().month)
    parser.add_argument('--start',type=int,required=True,help="start day to generate dates from",default=start_day)
    parser.add_argument('--end',type=int,required=True,help="end day to generate dates to",default=end_day)
    args, unknown = parser.parse_known_args()

    shift_dates = list(generate_days_in_month(args.year, args.month, args.start, args.end))

    parent_dir = f"{os.getenv('HOME')}/taxi_data"
    
    for shift_date in shift_dates:
        if datetime.datetime.strptime(shift_date, str("%d/%m/%Y")) <= datetime.datetime.today():
            jobs = make_gps_jobs(shift_date)
            kml_output = create_kml(jobs)

            # Saving the output to a file
            file_name: str = f"{parent_dir}/gps_jobs_{shift_date.replace('/','-')}.kml"
            with open(file_name, "w") as file:
                file.write(kml_output)

if __name__ == "__main__":
        main()
