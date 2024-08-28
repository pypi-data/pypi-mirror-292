from selenium import webdriver
from taxi_data.constants import BwcWebSiteConstants as Constants
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def login() -> webdriver.Firefox:
    
    from selenium.webdriver.common.by import By

    driver = webdriver.Firefox()

    try:
        # Open the login page
        driver.get(Constants.WEB_UI_URL)

        # Log in
        username = driver.find_element(By.ID, Constants.ID_USERNAME_FIELD)
        password = driver.find_element(By.ID, Constants.ID_PASSWORD_FIELD)

        username.send_keys(Constants.WEB_UI_USERNAME)
        password.send_keys(Constants.WEB_UI_PASSWORD)

        login_button = driver.find_element(By.ID, Constants.ID_LOGON_BUTTON)
        login_button.click()
    
    except Exception as e:
        raise e
    
    return driver

def close_last_login_window(driver: webdriver.Firefox) -> None:

    # Wait for the page to load and close last login dialog
    try:
        WebDriverWait(driver, Constants.TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, Constants.CLASS_LAST_LOGIN_MSG_CLOSE)))
        last_login_close = driver.find_element(By.CLASS_NAME, Constants.CLASS_LAST_LOGIN_MSG_CLOSE)
        last_login_close.click()
    except Exception as e:
        raise e
    
def nav_to_vehicles_for_operator(driver: webdriver) -> None:

    try:
        # Go to Vehicle for operator page
        jobs_link = driver.find_element(By.LINK_TEXT, Constants.LINK_TEXT_VEHICLES_FOR_OPERATOR)
        jobs_link.click()
    
    except Exception as e:
        raise e

def select_operator_from_drop_down(driver: webdriver) -> None:

    try:
        # Wait for operator page to load then select operator and click on car
        WebDriverWait(driver, Constants.TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_OPERATOR)))
        operator_menu = Select(driver.find_element(By.ID, Constants.ID_OPERATOR))
        operator_menu.select_by_visible_text(Constants.TEXT_WAYNE_BENNETT)
    except Exception as e:
        raise e

def click_on_car(driver: webdriver) -> None:

    try:
        #Wait for shift list to load and click on car
        WebDriverWait(driver, Constants.TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_VEHICLES_LIST)))
        car_list = driver.find_element(By.ID, Constants.ID_VEHICLES_LIST)
        car_list.find_element(By.LINK_TEXT, Constants.LINK_TEXT_CAR_NUMBER).click()
    
    except Exception as e:
        raise e
    
def shifts_for_vehicle_set_date_range(driver: webdriver, from_date, to_date) -> None:
    
    try:
    
        WebDriverWait(driver, Constants.TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_SHIFTS_FOR_VEHICLE)))
        from_date_field = driver.find_element(By.ID, Constants.ID_FROM_DATE)
        from_date_field.clear()
        from_date_field.send_keys(from_date)
        to_date_field = driver.find_element(By.ID, Constants.ID_TO_DATE)
        to_date_field.clear()
        to_date_field.send_keys(to_date)
        go_button = driver.find_element(By.XPATH, Constants.XPATH_GO_BUTTON)
        go_button.click()
    
        #Wait for filtered list to load and click on shift
        WebDriverWait(driver, Constants.TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_SHIFTS_FOR_VEHICLE)))

    except Exception as e:
        raise e