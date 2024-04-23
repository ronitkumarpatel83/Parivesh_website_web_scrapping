from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

url = "https://environmentclearance.nic.in/offlineproposal_status.aspx"
comName = "ltd"
csv_file_path = f"data/{comName}.csv"
if os.path.exists(csv_file_path):
    os.remove(csv_file_path)

driver = webdriver.Chrome()
driver.get(url)
driver.maximize_window()

driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_textbox2").click()
driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_textbox2").send_keys(comName)
driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btn").click()
driver.execute_script("window.scrollTo(0,300)")

time.sleep(2)

table_data = []


def pdf_Links():
    link_elements = driver.find_elements(By.XPATH,
                                         f'//span[@id="ctl00_ContentPlaceHolder1_GridView1_ctl03_attfile"]/div//span/a')
    links = [element.get_attribute("href") for element in link_elements]
    all_links_string = "\n".join(links)
    return all_links_string


def scrape_page():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    first_table = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_grdevents"})

    sl_no_xpath = '//*[@id="ctl00_ContentPlaceHolder1_grdevents"]/tbody/tr'
    tablesData = driver.find_elements(By.XPATH, sl_no_xpath)
    count2 = 3
    table_first_row = driver.find_elements(By.XPATH, f'{sl_no_xpath}[3]')
    if table_first_row:
        for row in tablesData[3:]:
            # Collecting headers and rows
            first_headers = first_table.find_all("th")
            first_titles = [i.text for i in first_headers]
            first_rows = first_table.find_all("tr")
            first_data = first_rows[count2].find_all("td")
            first_row_data = [tr.text for tr in first_data]
            print(count2)

            # Text for verify table types
            try:
                if count2 < 10:
                    proposal_status_xpath = driver.find_element(By.ID,
                                                                f'ctl00_ContentPlaceHolder1_grdevents_ctl0{str(count2)}_verify').text
                    print("proposal_status_xpath :- " + proposal_status_xpath)
                else:
                    proposal_status_xpath = driver.find_element(By.ID,
                                                                f'ctl00_ContentPlaceHolder1_grdevents_ctl{str(count2)}_verify').text
                    print("proposal_status_xpath :- " + proposal_status_xpath)
            except:
                print("=========== Reached 50th line 1 ============== ")

            # Clicking view column
            try:
                if count2 < 10:
                    clickOnView = driver.find_element(By.ID,
                                                      f'ctl00_ContentPlaceHolder1_grdevents_ctl0{str(count2)}_lnkDelete')
                    driver.execute_script("arguments[0].click()", clickOnView)
                else:
                    clickOnView = driver.find_element(By.ID,
                                                      f'ctl00_ContentPlaceHolder1_grdevents_ctl{str(count2)}_lnkDelete')
                    driver.execute_script("arguments[0].click()", clickOnView)
            except:
                print("=========== Reached 50th line 2 ============== ")

            # scrolldown
            driver.execute_script("window.scrollTo(0,300)")
            time.sleep(2)

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            # second_table = soup.find("table", {"id": "GridView1"})
            second_table = soup.find("table")

            # second table data
            second_data = []
            try:
                if second_table:
                    second_headers = second_table.find_all("th")
                    second_titles = [i.text for i in second_headers]
                    proposal_status = ["DList", "Rejected", "Closed", "Transfer"]
                    if proposal_status_xpath in proposal_status:
                        td_xpath1 = '//*[@id="GridView1"]/tbody/tr[2]/td'
                        td_size = driver.find_elements(By.XPATH, td_xpath1)
                        count3 = 1
                        for td in td_size[:-1]:
                            child_row_data = driver.find_element(By.XPATH, f'{td_xpath1}[{count3}]')
                            data = child_row_data.text
                            count3 += 1
                            second_data.append(data)
                        link_element = driver.find_element(By.XPATH, '//a[@href]')
                        Attached_file = link_element.get_attribute("href")
                        second_data.append(Attached_file)
                    else:
                        td_xpath2 = '//*[@id="ctl00_ContentPlaceHolder1_GridView1"]/tbody/tr[2]/td'
                        td_size2 = driver.find_elements(By.XPATH, td_xpath2)
                        count4 = 1
                        for td in td_size2[:-1]:
                            child_row_data2 = driver.find_element(By.XPATH, f'{td_xpath2}[{count4}]')
                            data = child_row_data2.text
                            count4 += 1
                            second_data.append(data)
                        links = pdf_Links()
                        second_data.append(links)

                row_data = first_row_data + second_data
                table_data.append(row_data)

                driver.back()
                count2 += 1
            except:
                print("=========== Reached 50th line 3 ============== ")
        headers = first_titles + second_titles
        df = pd.DataFrame(table_data, columns=headers)
        print(df)
        return df
    else:
        return pd.DataFrame(["No records found"])


def next_page():
    try:
        next_page_xpath = '//*[@id="ctl00_ContentPlaceHolder1_grdevents"]/tbody/tr[1]/td/table/tbody/tr/td'
        pagination_size = driver.find_elements(By.XPATH, next_page_xpath)
        count5 = 1
        for i in pagination_size:
            next_button = driver.find_element(By.XPATH, f'{next_page_xpath}[{count5}]')
            next_button.click()
        time.sleep(2)
        return True
    except:
        return False


if __name__ == "__main__":
    # while True:
    #     df = scrape_page()
    #     if not next_page():
    #         break
    df = scrape_page()
    df.to_csv(f'data/{comName}.csv', mode='a', index=False)
