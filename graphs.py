import requests
import csv
import pandas as pd
import datetime
import time

from classes import vid2jpg, barchart, barchart_total
from selenium import webdriver
import urllib
import locale

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# -----------------------chrome options initialization for selenium-------------------
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=browser/")
# ------------------------------------------------------------------------------------

# -----------initialize locale to convert integers to indian number system -------------
locale.setlocale(locale.LC_MONETARY, "en_IN")


# -----variable to store state wide new confirmed, recovered and deceased cases
state_data = [{}, {}, {}]
# -----variable to store count of all cases in india, state wide
states_info = {}
# ----variable to store districts of a state
dist = []
# ----variables to store cases count
dist_confirmed = []
dist_recovered = []
dist_deceased = []

flag = False  # -------flag to set if district wise cases were not released

# ------state variable that initializes with 'Andaman and Nicobar Islands'
#         and chages according to state in the data
state = "Andaman and Nicobar Islands"


date_yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime(
    "%Y-%m-%d"
)
date_day_bef_yesterday = (datetime.date.today() - datetime.timedelta(days=2)).strftime(
    "%Y-%m-%d"
)

print(date_yesterday)
print(date_day_bef_yesterday)


url = "https://api.covid19india.org/csv/latest/districts.csv"  # ----API link for data
response = requests.get(url)

if response.status_code != 200:
    print("Failed to get data:", response.status_code)

else:
    # ---- csv reader object as data is csv form
    CSV_DATA = csv.reader(response.text.strip().split("\n"))
    for record in CSV_DATA:

        # ----------work on the data from yesterday timestamp-----------
        if record[0] == str(date_yesterday) and record[2] != "Gamla":
            print(state)

            #  -----if state transistion occours in the loop, proceed for drawing graphs for previous state-----
            if record[1] != state:
                # --------method from classes.py to draw graphs
                print(len(dist))
                print(len(dist_confirmed))
                for i in range(len(dist_confirmed)):
                    print(str(dist[i]) + ":" + str(dist_confirmed[i]))

                barchart().draw(
                    state=state,
                    dist=dist,
                    dist_confirmed=dist_confirmed,
                    dist_deceased=dist_deceased,
                    dist_recovered=dist_recovered,
                    date_yesterday=date_yesterday,
                )
                # ------mp4 to jpg converter method from classes.py
                vid2jpg().convert(state=state)

                # -------loop to sum up the new district wide cases of a state
                add1 = 0
                add2 = 0
                add3 = 0
                for i in range(len(dist)):
                    add1 = add1 + int(dist_confirmed[i])
                    add2 = add2 + int(dist_recovered[i])
                    add3 = add3 + int(dist_deceased[i])
                state_data[0].update({state: add1})
                state_data[1].update({state: add2})
                state_data[2].update({state: add3})

                # -----reset all the essential variables for next state data set
                state = record[1]
                dist = []
                dist_confirmed = []
                dist_recovered = []
                dist_deceased = []

            # -----append the district name from APIs data for every iteration
            dist.append(record[2])

            # --------- another csv reader object to iterate over day before yesterday data
            CSV_DATA2 = csv.reader(response.text.strip().split("\n"))
            for record2 in CSV_DATA2:

                # --work on ROWS with day before yesterday date and same state as of in preceeding loop
                if (record2[0] == str(date_day_bef_yesterday)) and (
                    record2[1] == record[1]
                ):
                    print("running loop2")
                    # --if distrcit name was unkown and was the only district in that state,
                    # --remove preceeding data set of cases
                    if (record[2] == "Unknown") and (flag):
                        try:
                            dist_confirmed.pop()
                            dist_recovered.pop()
                            dist_deceased.pop()
                        except Exception as e:
                            print(str(e) + "-------------------------------------")

                    # -------if district was same as that of main loop,
                    # --subtract yesterday's data with day before yesterday's data
                    if record2[2] == record[2]:
                        dist_confirmed.append(int(record[3]) - int(record2[3]))
                        dist_recovered.append(int(record[4]) - int(record2[4]))
                        dist_deceased.append(int(record[5]) - int(record2[5]))
                        flag = False
                        break
                    # --------if yesterday's data has an unknown data,
                    # --but day before yesterday's do not have such
                    if (record[2] == "Unknown") and (record2[2] != "Unknown"):
                        dist_confirmed.append(int(record[3]))
                        dist_recovered.append(int(record[4]))
                        dist_deceased.append(int(record[5]))
                        flag = True

            # ---since above loop stops at west bengal, same code as above to cover west bengal
            if (record[1] == "West Bengal") and ((record[2] == "Uttar Dinajpur")):
                barchart().draw(
                    state=state,
                    dist=dist,
                    dist_confirmed=dist_confirmed,
                    dist_deceased=dist_deceased,
                    dist_recovered=dist_recovered,
                    date_yesterday=date_yesterday,
                )
                vid2jpg().convert(state=state)
                add1 = 0
                add2 = 0
                add3 = 0
                for i in range(len(dist)):
                    add1 = add1 + int(dist_confirmed[i])
                    add2 = add2 + int(dist_recovered[i])
                    add3 = add3 + int(dist_deceased[i])
                state_data[0].update({state: add1})
                state_data[1].update({state: add2})
                state_data[2].update({state: add3})
                dist = []
                dist_confirmed = []
                dist_recovered = []
                dist_deceased = []

# ----method to draw graphs for india wide sates data
barchart_total().draw(state_data=state_data, date_yesterday=date_yesterday)
print("-----------------------done with graphs--------------------------------------")

# -------------------code to calculate total new cases all over india-------------------
total_new_cases = 0
total_new_recovered = 0
total_new_deceased = 0
for i in state_data[0].values():
    total_new_cases = total_new_cases + i
for i in state_data[1].values():
    total_new_recovered = total_new_recovered + i
for i in state_data[2].values():
    total_new_deceased = total_new_deceased + i

print("total_new_cases :" + str(total_new_cases))
print("total_new_recovered :" + str(total_new_recovered))
print("total_new_deceaved :" + str(total_new_deceased))
# --------------------------------------------------------------------------------------

time.sleep(1)

# -----------------collect all cases count in india from the second API-------------------------
url = "https://api.covid19india.org/csv/latest/states.csv"
while 1:
    response2 = requests.get(url)
    if response2.status_code == 200:
        break
    else:
        print("Failed to get data:", response2.status_code)

CSV_DATA = csv.reader(response2.text.strip().split("\n"))
for record in CSV_DATA:
    if record[0] == str(date_yesterday):
        states_info.update({record[1]: [record[2], record[3], record[4]]})

print(states_info)
# ----------------------------------------------------------------------------------------------


link = "https://web.whatsapp.com/send?phone=%s&text=%s"  # ---dynamic whatsapp chat link

# -----------------create pandas dataframe with the users data-------------
df = pd.read_csv("users.csv", header=0)

# ---------loop across each user to send messages----------------------------------------------------------------------
for i in df.index:
    # ----declare a dynamic message to be sent formatted with variables----------
    msg = "active cases in %s : *%s*\r\ntotal deaths in %s : *%s*\r\ntotal recovered in %s : *%s*\r\n\nactive cases in india : *%s*\r\ntotal deaths in india : *%s*\r\ntotal recovered in india : *%s*" % (
        df["state"][i],
        # ---active cases = confirmed-recovered-deceased
        locale.format_string(
            "%d",
            (
                int(states_info[df["state"][i]][0])
                - int(states_info[df["state"][i]][1])
                - int(states_info[df["state"][i]][2])
            ),
            grouping=True,
            monetary=True,
        ),
        df["state"][i],
        # ------conert integer form of number to india number system
        locale.format_string(
            "%d", int(states_info[df["state"][i]][2]), grouping=True, monetary=True
        ),
        df["state"][i],
        locale.format_string(
            "%d", int(states_info[df["state"][i]][1]), grouping=True, monetary=True
        ),
        locale.format_string(
            "%d",
            (
                int(states_info["India"][0])
                - int(states_info["India"][1])
                - int(states_info["India"][2])
            ),
            grouping=True,
            monetary=True,
        ),
        locale.format_string(
            "%d", int(states_info["India"][2]), grouping=True, monetary=True
        ),
        locale.format_string(
            "%d", int(states_info["India"][1]), grouping=True, monetary=True
        ),
    )
    print(msg)

    # --------------initialize driver object for selenium-------------------------------------
    while 1:
        try:
            driver = webdriver.Chrome(
                executable_path="<complete path for chromedriver>",
                options=options,
            )
            # ---url encode the message with whatsapp link
            urlconv = urllib.parse.quote(msg, safe="")
            url = link % (df["mobile_number"][i], urlconv)

            # ----run the url
            driver.get(url)

            # -------loop on the webpage to find send button and click it

            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "_1E0Oz"))
                ).click()
            except:
                driver.refresh()

            # --------------send news feed--------------------------------------------
            news = ""
            with open("data/%s/news.csv" % df["state"][i], "r") as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=";")
                for row in csv_reader:
                    news = (
                        news
                        + "*"
                        + row[0]
                        + "*                                "
                        + row[1]
                        + "\n"
                    )
            message_box = driver.find_element_by_css_selector(
                "._2x4bz > div:nth-child(2)"
            )
            message_box.send_keys(news)
            # ---------------------------------------------------------------------------

            # --- find attach button and attach the images and their decription-----------------------------------------------------
            attach = driver.find_element_by_css_selector(
                "._2C9f1 > div:nth-child(1) > div:nth-child(1)"
            )
            attach.click()
            img_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@id='main']/footer/div[1]/div[1]/div[2]/div/span/div[1]/div/ul/li[1]/button/input",
                    )
                )
            )
            img_box.send_keys(
                "/home/surya/covid-wh_bot/Covid_bot_V2/data/%s/new_confirmed.jpg"
                % df["state"][i]
            )
            time.sleep(0.2)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div[1]/span/div/div[2]/div/div[3]/div[1]/div[2]",
                        )
                    )
                ).send_keys(
                    "new confirmed cases in %s as of %s"
                    % (df["state"][i], date_yesterday)
                )
                time.sleep(0.1)
            except Exception as e:
                print(e)
                pass

            img_box = driver.find_element_by_xpath(
                '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/input'
            )
            img_box.send_keys(
                "/home/surya/covid-wh_bot/Covid_bot_V2/data/%s/new_deceased.jpg"
                % df["state"][i]
            )
            time.sleep(0.5)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div[1]/span/div/div[2]/div/div[3]/div[1]/div[2]",
                        )
                    )
                ).send_keys(
                    "new death cases in %s as of %s" % (df["state"][i], date_yesterday)
                )
                time.sleep(0.1)
            except Exception as e:
                print(e)
                pass

            img_box = driver.find_element_by_xpath(
                '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/input'
            )
            img_box.send_keys(
                "/home/surya/covid-wh_bot/Covid_bot_V2/data/%s/new_recovered.jpg"
                % df["state"][i]
            )
            time.sleep(0.5)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div[1]/span/div/div[2]/div/div[3]/div[1]/div[2]",
                        )
                    )
                ).send_keys(
                    "new recovered cases in %s as of %s"
                    % (df["state"][i], date_yesterday)
                )
                time.sleep(0.1)
            except Exception as e:
                print(e)
                pass

            img_box = driver.find_element_by_xpath(
                '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/input'
            )
            img_box.send_keys(
                "/home/surya/covid-wh_bot/Covid_bot_V2/data/india_new_confirmed.jpg"
            )
            time.sleep(0.5)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div[1]/span/div/div[2]/div/div[3]/div[1]/div[2]",
                        )
                    )
                ).send_keys("new confirmed cases in india as of %s" % date_yesterday)
                time.sleep(0.1)
            except Exception as e:
                print(e)
                pass

            img_box = driver.find_element_by_xpath(
                '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/input'
            )
            img_box.send_keys(
                "/home/surya/covid-wh_bot/Covid_bot_V2/data/india_new_recovered.jpg"
            )
            time.sleep(0.5)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div[1]/span/div/div[2]/div/div[3]/div[1]/div[2]",
                        )
                    )
                ).send_keys("new recovered cases in india as of %s" % date_yesterday)
                time.sleep(0.1)
            except Exception as e:
                print(e)
                pass

            img_box = driver.find_element_by_xpath(
                '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/input'
            )
            img_box.send_keys(
                "/home/surya/covid-wh_bot/Covid_bot_V2/data/india_new_deceased.jpg"
            )
            time.sleep(0.5)
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/div[1]/span/div/div[2]/div/div[3]/div[1]/div[2]",
                        )
                    )
                ).send_keys("new death cases in india as of %s" % date_yesterday)
                time.sleep(0.1)
            except Exception as e:
                print(e)
                pass
            # ---------------------------------------------------------------------------------------------------------------------------------------------------

            # ----click the send button------------------------
            while 1:
                try:
                    driver.find_element_by_xpath(
                        '//*[@id="app"]/div[1]/div[1]/div[2]/div[2]/span/div[1]/span/div[1]/div/div[2]/span/div/div'
                    ).click()
                    break
                except:
                    pass

            # -----wait for images to be sent--------------------
            time.sleep(5)
            # ----close the driver object once done--------------
            driver.close()
            break
        except Exception as e:
            print(e)
            driver.close()
