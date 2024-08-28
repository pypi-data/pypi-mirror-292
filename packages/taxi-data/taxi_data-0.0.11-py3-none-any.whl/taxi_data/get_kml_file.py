import os, pydantic, pathlib
from typing import List, Tuple
from datetime import datetime, time, timedelta, date
from classes import RawEvent, ProcessedEvent, GpsTrackerEvent, PlaybackSpeed
from constants import GpsTrackerWebSiteConstants as Constants
from . import automate_gps_tracker_web_site as WebSite

def process_raw_events(raw_events: RawEvent) -> List[ProcessedEvent]:
    
    processed_events: List[ProcessedEvent] = []

    for raw_event in raw_events:
        match raw_event.event_type:
            case "Stay": 
                event_type: GpsTrackerEvent = GpsTrackerEvent.STAY  
        
        shift_date: date = datetime.date(datetime.strptime(raw_event.from_time, '%Y-%m-%d %H:%M:%S'))
        from_time: time = datetime.time(datetime.strptime(raw_event.from_time, '%Y-%m-%d %H:%M:%S'))
        to_time: time = datetime.time(datetime.strptime(raw_event.to_time, '%Y-%m-%d %H:%M:%S'))
        duration: timedelta = datetime.combine(shift_date, to_time) - datetime.combine(shift_date, from_time)

        processed_event: ProcessedEvent = ProcessedEvent(event_type=event_type,
                                         from_time=from_time,
                                         to_time=to_time,
                                         duration=duration)
        processed_events.append(processed_event)
    
    
    return processed_events

def process_raw_info_text(raw_text):
    # Step 1: Split the string into lines
    lines = raw_text.splitlines()

    # Step 2: Extract the second line
    second_line = lines[1]

    # Step 3: Split the second line to get the time part
    date, start_time = second_line.split()  # This splits "2024-08-16 07:46:37" into date and time
    return start_time

def get_kml_file(shift_date: str | None) -> Tuple[pathlib.Path, ProcessedEvent]:

    if shift_date is not None:
        shift_date = datetime.strptime(shift_date, str('%d/%m/%Y'))
    else:
        shift_date = date.today()
    shift_date = datetime.strftime(shift_date, str('%Y-%m-%d'))

    try:
        driver = WebSite.login()
        driver.switch_to.default_content()
        WebSite.switch_to_main_box_iframe(driver)
        tracker = WebSite.click_on_tracker(driver)
        WebSite.nav_to_tracking_report(driver, tracker)
        WebSite.set_tracking_report_date_and_go(driver, date=shift_date)
        driver.switch_to.default_content()
        WebSite.open_playback(driver, tracker)
        WebSite.set_playback_date(driver, date=shift_date)
        WebSite.set_plaback_speed(driver, speed=PlaybackSpeed.SLOW)
        playback_buttons = WebSite.get_playback_buttons(driver)
        playback_buttons.Play.click()
        raw_text = WebSite.get_info_pane_text(driver, playback_buttons)
        WebSite.set_plaback_speed(driver, PlaybackSpeed.FAST)
        WebSite.play_to_end(driver, playback_buttons)
        raw_events: RawEvent = WebSite.get_raw_events(driver)
    finally:
        driver.quit()

    events: ProcessedEvent = process_raw_events(raw_events)
    start_time = process_raw_info_text(raw_text)

    # Rename the KML file
    old_file = os.path.join(Constants.DOWNLOADS_FOLDER,f"{Constants.FILE_NAME_STRING}{shift_date}.kml")
    new_file = os.path.join(Constants.DOWNLOADS_FOLDER,f"{Constants.FILE_NAME_STRING}{shift_date}-{start_time}.kml")
    os.rename(old_file, new_file)
        
    file_path: pydantic.FilePath = pathlib.Path(f"{Constants.DOWNLOADS_FOLDER}{Constants.FILE_NAME_STRING}{shift_date}-{start_time}.kml")
    return file_path, events

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Retrives GPS trace from web portal')
    parser.add_argument('-d',type=str,required=False,help="date to pull records from",default=None)
    args, unknown = parser.parse_known_args()

    if args.d is None:
        shift_date = str(input("Enter date (Leave blank for today): "))
    else:
        shift_date = args.d

    path, events = get_kml_file(shift_date)
    print(f"Downloaded to '{path}'")    

if __name__ == "__main__":
    main()