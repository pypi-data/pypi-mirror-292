from selenium import webdriver
from taxi_data.constants import GpsTrackerWebSiteConstants as Constants
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from taxi_data.classes import PlaybackSpeed, PlaybackButtons, RawEvent
from selenium.webdriver.common.action_chains import ActionChains
from typing import List
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoAlertPresentException
from os import rename, getenv
from typing import Final

def login() -> webdriver.Firefox:
    driver = webdriver.Firefox()

    # Open the login page
    driver.get(Constants.WEB_UI_URL)

    iframe = driver.find_element(By.ID, Constants.ID_LOGIN_IFRAME)
    driver.switch_to.frame(iframe)

    # Log in
    username = driver.find_element(By.ID, Constants.ID_USERNAME_FIELD)
    password = driver.find_element(By.ID, Constants.ID_PASSWORD_FIELD)

    username.send_keys(Constants.WEB_UI_USERNAME)
    password.send_keys(Constants.WEB_UI_PASSWORD)

    login_button = driver.find_element(By.ID, Constants.ID_LOGIN_BUTTON)
    login_button.click()
    return driver

def switch_to_main_box_iframe(driver: webdriver) -> None:
    WebDriverWait(driver, Constants.DEFAULT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_MAIN_BOX_IFRAME)))
    iframe = driver.find_element(By.ID, Constants.ID_MAIN_BOX_IFRAME)
    driver.switch_to.frame(iframe)
    
def click_on_tracker(driver) -> WebElement:

    #Wait for device list to load
    WebDriverWait(driver, Constants.LONG_TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_DEVICE_LIST)))
    tracker = driver.find_element(By.ID, Constants.ID_DEVICE_LIST)

    # Click on device
    element_to_click = tracker.find_element(By.XPATH, Constants.XPATH_GPS_TRACKER)
    WebDriverWait(tracker, 60).until(EC.presence_of_element_located((By.XPATH, Constants.XPATH_GPS_TRACKER)))
    element_to_click.click()

    return tracker

def nav_to_tracking_report(driver: webdriver, tracker: WebElement) -> None:
    #Click on more
    element_to_click = tracker.find_element(By.XPATH, Constants.XPATH_MORE_OPTIONS)
    WebDriverWait(tracker, 60).until(EC.presence_of_element_located((By.XPATH, Constants.XPATH_MORE_OPTIONS)))
    element_to_click.click()

    #Click on tracking report
    element_to_click = tracker.find_element(By.XPATH, Constants.XPATH_TRACKING_REPORT)
    WebDriverWait(tracker, 60).until(EC.presence_of_element_located((By.XPATH, Constants.XPATH_TRACKING_REPORT)))
    element_to_click.click()

    # Wait for report download window to load
    WebDriverWait(driver, Constants.DEFAULT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_REPORT_DOWNLOAD_WINDOW)))
    iframe = driver.find_element(By.ID, Constants.ID_REPORT_DOWNLOAD_WINDOW)
    driver.switch_to.frame(iframe)

    
def set_tracking_report_date_and_go(driver: webdriver, date: str) -> None:

        #Find date field and enter date
        WebDriverWait(driver, Constants.DEFAULT_TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, Constants.CLASS_DOWNLOAD_DATE)))
        date_box = driver.find_element(By.CLASS_NAME, Constants.CLASS_DOWNLOAD_DATE)
        date_box.clear()
        date_box.send_keys(date)
    
        driver.find_element(By.ID, Constants.ID_DOWNLOAD_GO_BUTTON).click()
        downloads_folder: Final[str] = f"{getenv('HOME')}/Downloads"
        parent_dir: Final[str] = f"{getenv('HOME')}/taxi_data"
        file_name: Final[str] = f"CC888-63677-{date}.kml"
        rename(f"{downloads_folder}/{file_name}",f"{parent_dir}/{file_name}")
   
def open_playback(driver: webdriver, tracker: WebElement) -> None:
        # Store the current window handle
        main_window = driver.current_window_handle
        # driver.switch_to.default_content()
        iframe = driver.find_element(By.ID, Constants.ID_MAIN_BOX_IFRAME)
        driver.switch_to.frame(iframe)

        # Click Playback
        tracker.find_element(By.XPATH, Constants.XPATH_PLAYBACK_BUTTON).click()

        #Wait for tab to load
        WebDriverWait(driver, Constants.DEFAULT_TIMEOUT).until(EC.new_window_is_opened([main_window]))

        # Get all window handles (there should be two now)
        window_handles = driver.window_handles
        # Switch to the new window handle
        for handle in window_handles:
            if handle != main_window:
                driver.switch_to.window(handle)
                break
        
        #Wait for playback page to load
        WebDriverWait(driver, Constants.DEFAULT_TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_PLAYBACK_START_DATE)))

    
def set_playback_date(driver: webdriver, date: str) -> None:

        #Find date boxes and enter date
        date_box = driver.find_element(By.ID, Constants.ID_PLAYBACK_START_DATE)
        date_box.clear()
        date_box.send_keys(f"{date} 00:00")   

        date_box = driver.find_element(By.ID, Constants.ID_PLAYBACK_END_DATE)
        date_box.clear()
        date_box.send_keys(f"{date} 23:59")
    

def set_plaback_speed(driver: webdriver, speed: PlaybackSpeed) -> None:

        # Play speed slow
        slider = driver.find_element(By.ID, Constants.ID_SLIDER)    
        # Initialize ActionChains
        actions = ActionChains(driver)

        match speed:
            case PlaybackSpeed.FAST:
                offset = -slider.size['width']
            case PlaybackSpeed.SLOW:
                offset = slider.size['width']
            case _:
                raise "Slider offset not correctly set"
        # Move the slider to the right by clicking and dragging
        actions.click_and_hold(slider).move_by_offset(offset, 0).release().perform()
    

def get_info_pane_text(driver: webdriver, 
                   playback_buttons: PlaybackButtons) -> str | None:

    def get_info_pane(driver: webdriver) -> WebElement:
        info_pane: WebElement = driver.find_element(By.XPATH, Constants.XPATH_INFO_PANE)
    
        if info_pane.text != None:
#                text = info_pane.text
            return info_pane    

    try:
        text = None
        WebDriverWait(driver, Constants.DEFAULT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, Constants.ID_PAUSE_BUTTON)))
        playback_buttons.Pause.click()

        info_pane: WebElement = get_info_pane(driver)

    except TimeoutException:
        try:
            driver.switch_to.alert.accept()
        except NoAlertPresentException:
            info_pane: WebElement = get_info_pane(driver)
            return info_pane.text         

    return info_pane.text

def get_playback_buttons(driver: webdriver) -> PlaybackButtons:
   
    play_button = driver.find_element(By.ID, Constants.ID_PLAY_BUTTON)
    pause_button = driver.find_element(By.ID, Constants.ID_PAUSE_BUTTON)
    continue_button = driver.find_element(By.ID, Constants.ID_CONTINUE_BUTTON)
    
    return PlaybackButtons(Play=play_button, Continue=continue_button, Pause=pause_button)

def play_to_end(driver: webdriver, playback_buttons: PlaybackButtons) -> None:

    playback_buttons.Play.click()
    WebDriverWait(driver, Constants.JUST_FUCKING_WAIT_TIMEOUT).until(EC.alert_is_present())
    driver.switch_to.alert.accept()
    driver.switch_to.default_content()

    
def get_raw_events(driver: webdriver) -> List[RawEvent]:

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    events_table = soup.find('table', {'id': Constants.ID_EVENT_LIST})
    raw_events = []

    for row in events_table.find_all('tr')[1:]:  # Skip header  & Footer row
        cols = row.find_all('td')
        event = RawEvent(event_type=cols[0].text.strip(),
                from_time=cols[1].text.strip(),
                to_time=cols[2].text.strip(),
                duration=cols[3].text.strip())
        raw_events.append(event)

    return raw_events

def setup_playback(driver: webdriver, shift_date: str) -> PlaybackButtons:

    set_playback_date(driver, date=shift_date)
    set_plaback_speed(driver, speed=PlaybackSpeed.SLOW)
    playback_buttons = get_playback_buttons(driver)

    return playback_buttons

def nav_to_playback(shift_date: str) -> webdriver:
    driver = login()
    driver.switch_to.default_content()
    switch_to_main_box_iframe(driver)
    tracker = click_on_tracker(driver)
    nav_to_tracking_report(driver, tracker)
    set_tracking_report_date_and_go(driver, date=shift_date)
    driver.switch_to.default_content()
    open_playback(driver, tracker)

    return driver

