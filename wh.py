from selenium import webdriver
import time
from classes import msgresponse


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ------------------------------------------chrome options declaration for selenium driver -------------------------
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=browser/")
driver = webdriver.Chrome(
    executable_path="./chromedriver",
    options=options,
)
# driver = webdriver.Firefox()
driver.get("https://web.whatsapp.com")


# ----------------------------function to type msg in msg box ----------------------------------------------------------
def response(data):
    message_box = driver.find_element_by_css_selector("._2x4bz > div:nth-child(2)")
    message_box.send_keys(data)


i = 0
count = 0
if input() == "start":
    while 1:
        # ---------scroll element for list of contacts -----------------
        scroll = driver.find_element_by_xpath('//*[@id="pane-side"]')
        # ---------get current sroll height in chats div --------------------
        current_y = driver.execute_script("return arguments[0].scrollTop", scroll)

        if count > 0:  # if count>0 scroll chats to next 16 elements---------
            i += 1
            driver.execute_script("arguments[0].scrollTop = 1152*%s" % i, scroll)
            count = 0

        # --------------if scrolled to bottom, scroll to top-------------------
        if (
            driver.execute_script("return arguments[0].scrollTop", scroll) + 701
        ) == driver.execute_script("return arguments[0].scrollHeight", scroll):
            driver.execute_script("arguments[0].scrollTop = 0", scroll)
            count = 0
            i = 0

            # ----------------------check if a new msg received at opened chat box, by checking te nunber of msg divisions-------------------
            while 1:
                try:
                    # ----get current div count in chat box-------------------------
                    div_count1 = driver.find_elements_by_xpath(
                        '//*[@id="main"]/div[3]/div/div/div[last()-1]/div'
                    )

                    # -----------------if number of messages in a chat exceeds 45, clear the chat-------------------
                    if len(div_count1) >= 45:
                        driver.find_element_by_xpath(
                            '//*[@id="main"]/header/div[3]/div/div[2]/div/div'
                        ).click()
                        WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable(
                                (
                                    By.XPATH,
                                    '//*[@id="app"]/div[1]/span[4]/div/ul/div/div/li[4]',
                                )
                            )
                        ).click()
                        while 1:
                            try:
                                WebDriverWait(driver, 3).until(
                                    EC.element_to_be_clickable(
                                        (
                                            By.XPATH,
                                            '//*[@id="app"]/div[1]/span[2]/div[1]/div/div/div/div/div/div[2]/div[2]',
                                        )
                                    )
                                ).click()
                                break
                            except Exception as e:
                                print(e)
                        div_count2 = [0, 0]
                        time.sleep(2)
                    if len(div_count1) > len(div_count2):
                        # ----if new division found, execute response for that-----------
                        try:
                            rgb = driver.find_element_by_xpath(
                                '//*[@id="main"]/div[3]/div/div/div[last()-1]/div[last()]/div/div'
                            ).value_of_css_property("background-color")
                            print(rgb)
                            if rgb == "rgba(255, 255, 255, 1)":
                                msg = driver.find_element_by_xpath(
                                    '//*[@id="main"]/div[3]/div/div/div[last()-1]/div[last()]/div/div/div/div[last()-1]/div[last()]/span[1]/span'
                                ).text
                                num = driver.find_element_by_xpath(
                                    "/html/body/div/div[1]/div[1]/div[4]/div[1]/header/div[2]/div[1]/div/span"
                                ).text
                                print(num + ":" + msg)
                                if (
                                    (msg.lower().find("thank") == -1)
                                    and (msg.lower() != "ok")
                                    and (msg.lower() != "okay")
                                    and (msg.lower() != "k")
                                ):
                                    resp = msgresponse().check_func(
                                        number=num, message=msg
                                    )  # ----method from classes.py to process the msg
                                    print(resp)
                                    response(data=resp)
                                    driver.find_element_by_css_selector(
                                        "._1E0Oz"
                                    ).click()  # ------click on send button
                                    time.sleep(0.2)
                                div_count2 = driver.find_elements_by_xpath(
                                    '//*[@id="main"]/div[3]/div/div/div[last()-1]/div'
                                )
                            else:
                                pass
                        except Exception as e:
                            print(e)
                except:
                    pass
                # ----------try checking the notification dot on chats, if yes, break the loop and go to see the msg
                try:
                    d = driver.find_element_by_css_selector("._38M1B")
                    break
                except:
                    pass
        # -------------------------if count=0, stay there without scrolling and wait for notification dot(new msg) to appear----------------------------
        while count < 1:
            try:
                # -----------if notification dot has come, click on it to open that chart------------------------------
                d = driver.find_element_by_css_selector("._38M1B")
                d.click()
                time.sleep(0.1)
                try:
                    # ----------get the msg content and the phone number associated to that chat -----------------------------------
                    msg = driver.find_element_by_xpath(
                        '//*[@id="main"]/div[3]/div/div/div[last()-1]/div[last()]/div/div/div/div[last()-1]/div[last()]/span[1]/span'
                    ).text
                    num = driver.find_element_by_xpath(
                        "/html/body/div/div[1]/div[1]/div[4]/div[1]/header/div[2]/div[1]/div/span"
                    ).text
                    # ---------------------------------------------------------------------------------------------------------------
                except Exception as e:
                    print(e)
                print(num + ":" + msg)

                # ------------if the msg content was any of 'thank','ok','okay','k', do not send it to processing
                if (
                    (msg.lower().find("thank") == -1)
                    and (msg.lower() != "ok")
                    and (msg.lower() != "okay")
                    and (msg.lower() != "k")
                ):
                    resp = msgresponse().check_func(
                        number=num, message=msg
                    )  # --method from classes.py to process msg
                    print(resp)
                    response(data=resp)
                    driver.find_element_by_css_selector("._1E0Oz").click()
                    time.sleep(0.2)

                # --------------update div_count2 variable with the new div in chat box
                div_count2 = driver.find_elements_by_xpath(
                    '//*[@id="main"]/div[3]/div/div/div[last()-1]/div'
                )
            except Exception as e:
                # ---------------if no new notification was found in present scroll, update count to 1, to start scrolling down------------
                count += 1
                print(e)
