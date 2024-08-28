import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List
from datetime import datetime, time
from parse_kml import parse_kml
from classes import Coordinates_with_timestamps, Coordinates_with_jobs, Job

def prettify(element):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def match_jobs_to_coordinates(coordinates: List[Coordinates_with_timestamps], jobs: List[Job]) -> List[Coordinates_with_jobs]:
    matched_data = []
    
    for job in jobs:
        # Convert the time objects in the Job class to datetime objects for matching
        meter_on_datetime = datetime.combine(datetime.today(), job.meter_on)
        meter_off_datetime = datetime.combine(datetime.today(), job.meter_off)
        
        # Find closest coordinates for meter on and meter off times
        closest_on = min(coordinates, key=lambda c: abs(c.timestamp - meter_on_datetime))
        closest_off = min(coordinates, key=lambda c: abs(c.timestamp - meter_off_datetime))
        
        

        matched_data.append({
            'job': job
        })
    
    return matched_data

def generate_kml(matched_data):
    kml = ET.Element('kml', xmlns='http://www.opengis.net/kml/2.2')
    document = ET.SubElement(kml, 'Document')
    
    for data in matched_data:
        job = data['job']
        for action, coord in [('Meter on', data['meter_on']), ('Meter off', data['meter_off'])]:
            placemark = ET.SubElement(document, 'Placemark')
            ET.SubElement(placemark, 'name').text = f"{action} - Job {job.booking_id}"
            ET.SubElement(placemark, 'description').text = (
                f"Job ID: {job.booking_id}\n"
                f"Driver ID: {job.driver}\n"
                f"Status: {job.status}\n"
                f"Pick-Up: {job.pick_up_suburb}\n"
                f"Destination: {job.destination_suburb}\n"
                f"Fare: ${job.fare:.2f}\n"
                f"Toll: ${job.toll:.2f}\n"
                f"Account: {job.account}\n"
                f"Time: {coord.timestamp}\n"
                f"Action: {action}"
            )
            point = ET.SubElement(placemark, 'Point')
            ET.SubElement(point, 'coordinates').text = f"{coord.longitude},{coord.latitude},0"
    
    return prettify(kml)

def write_kml_file(file_path, kml_content):
    with open(file_path, 'w') as file:
        file.write(kml_content)


if __name__ == "__main__":
    # Example job data (to be replaced with actual data parsing)
    jobs = [
        Job(
            booking_id=1,
            driver=123,
            status='Completed',
            accepted=time(7, 30),
            meter_on=time(7, 50),
            meter_off=time(8, 10),
            pick_up_suburb='SuburbA',
            destination_suburb='SuburbB',
            fare=25.00,
            toll=3.50,
            account='AccountA'
        ),
        Job(
            booking_id=2,
            driver=456,
            status='Completed',
            accepted=time(8, 0),
            meter_on=time(8, 15),
            meter_off=time(8, 45),
            pick_up_suburb='SuburbC',
            destination_suburb='SuburbD',
            fare=30.00,
            toll=4.00,
            account='AccountB'
        )
    ]

    # Parse KML and get coordinates (this would be replaced by your existing parsing logic)
    coordinates_with_timestamps = parse_kml('/home/wayne/Downloads/CC888-63677-2024-08-16-07:46:37.kml', 10)

    # Match jobs to coordinates
    matched_data = match_jobs_to_coordinates(coordinates_with_timestamps, jobs)

    # Generate KML
    kml_content = generate_kml(matched_data)

    # Write to file
    write_kml_file('/home/wayne/Downloads/taxi_jobs.kml', kml_content)
