import pydantic
from typing import Optional, NamedTuple
from datetime import time, timedelta, datetime
from enum import Enum
from selenium.webdriver.remote.webelement import WebElement

class Coordinates(pydantic.BaseModel):
    latitude: Optional[float]
    longitude: Optional[float]
    timestamp: datetime  # This will be overridden

class Job(pydantic.BaseModel):
    booking_id: int	
    driver: int
    status: str
    accepted: time
    meter_on: time
    meter_off: time
    pick_up_suburb: str
    destination_suburb: str
    fare: float
    toll: float
    account: str

class Coordinates_with_timestamps(Coordinates):
    timestamp: time
    gap: Optional[bool] = None

class GpsJob(Job):
    account: Optional[str] = None
    meter_on_gps: Optional[Coordinates_with_timestamps] = None
    meter_off_gps: Optional[Coordinates_with_timestamps] = None

class GpsTrackerEvent(str,Enum):
    STAY: str = "Stay"

class ProcessedEvent(pydantic.BaseModel):
    event_type: GpsTrackerEvent
    from_time: time
    to_time: time
    duration: timedelta

class RawEvent(pydantic.BaseModel):
    event_type: str
    from_time: str
    to_time: str
    duration: str

class Coordinates_with_jobs(Coordinates):
    job: Job

class PlaybackSpeed(str,Enum):
    FAST: str = "FAST"
    SLOW: str = "SLOW"

class PlaybackButtons(NamedTuple):
    Play: WebElement
    Pause: WebElement
    Continue: WebElement

class GpsData(Coordinates_with_timestamps):
        distance: Optional[float] 
        direction: Optional[str]
        speed: Optional[float]
