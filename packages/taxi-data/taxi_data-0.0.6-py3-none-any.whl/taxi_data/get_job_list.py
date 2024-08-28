from typing import List
from taxi_data.classes import Job

def get_job_list(shift_date: str | None = None) -> List[Job]:

    from datetime import date, datetime
    import automate_bwc_web_site as BwcSite
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    from constants import BwcWebSiteConstants as Constants

    if shift_date is not None:
        shift_date = datetime.strptime(shift_date, str('%d/%m/%Y'))
    else:
        shift_date = date.today()
    shift_date = datetime.strftime(shift_date, str('%m/%d/%Y'))

    driver = BwcSite.login()

    BwcSite.close_last_login_window(driver)

    BwcSite.nav_to_vehicles_for_operator(driver)

    BwcSite.select_operator_from_drop_down(driver)

    BwcSite.click_on_car(driver)

    BwcSite.shifts_for_vehicle_set_date_range(driver=driver, from_date=shift_date, to_date=shift_date)

    try:
       
        # Iterate over each shift and extract job data
        jobs_data = []
        shift_rows = driver.find_elements(By.XPATH, Constants.XPATH_SHIFT_ROW)

        for i in range(0, len(shift_rows)):
            # Click on the driver ID link for each shift
            shift_rows[i].find_element(By.TAG_NAME, Constants.TAG_ANCHOR).click()

            # Wait for job list to load
            WebDriverWait(driver, Constants.TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_JOBS_FOR_SHIFT)))

            # Extract the job data
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs_table = soup.find('table', {'id': Constants.ID_JOBS_FOR_SHIFT})

            for row in jobs_table.find_all('tr')[1:-1]:  # Skip header  & Footer row
                cols = row.find_all('td')
                job = Job(booking_id=int(cols[0].text.strip()),
                        driver=int(cols[1].text.strip()),
                        status=cols[2].text.strip(),
                        accepted=cols[3].text.strip(),
                        meter_on=cols[4].text.strip(),
                        meter_off=cols[5].text.strip(),
                        pick_up_suburb=cols[6].text.strip(),
                        destination_suburb=cols[7].text.strip(),
                        fare=float(str.replace(cols[8].text.strip(), '$', '')),
                        toll=float(str.replace(cols[9].text.strip(), '$', '')),
                        account=cols[10].text.strip())
                jobs_data.append(job)

            # Go back to the shift list page to process the next shift
            driver.back()
            WebDriverWait(driver, Constants.TIMEOUT).until(EC.presence_of_element_located((By.ID, Constants.ID_SHIFTS_FOR_VEHICLE)))
            shift_rows = driver.find_elements(By.XPATH, Constants.XPATH_SHIFT_ROW)
    
    except Exception as e:
        raise e
    
    finally:

        driver.quit()
        
    return jobs_data

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Retrives job listing from BWC web portal')
    parser.add_argument('-d',type=str,required=False,help="date to pull records from",default=None)
    args, unknown = parser.parse_known_args()

    if args.d is None:
        shift_date = str(input("Enter date (Leave blank for today): "))
    else:
        shift_date = args.d

    jobs_list = get_job_list(shift_date)
    print(len(jobs_list))

if __name__ == "__main__":
    main()