from selenium import webdriver
import csv
from gensim.models.keyedvectors import KeyedVectors
from document_similarity_master.DocSim import DocSim

# -----------path to trained model-----------
googlenews_model_path = (
    "document_similarity_master/data/GoogleNews-vectors-negative300.bin"
)
# ------pre defined stop words to check for similarities-----------
stopwords_path = "document_similarity_master/data/stopwords_en.txt"


# -----------initializing model with stop words------------------------
model = KeyedVectors.load_word2vec_format(googlenews_model_path, binary=True)
with open(stopwords_path, "r") as fh:
    stopwords = fh.read().split(",")
ds = DocSim(model, stopwords=stopwords)


# ----------------REMOVE_SIMILARITIES() FUNCTION----------------------------------------------------------------
#  this function filters the list of strings(news) by deleting duplicate or similar news
def remove_similar(list):
    filtered_list = list.copy()
    for i in range(len(list)):
        for j in range(i, len(list)):
            # -------loop with try catch blocks to repeat if any execution errors occour
            for i in range(3):
                try:
                    # -----find the probability of similarity between every two selected news-----
                    sim_scores = ds.calculate_similarity(list[i], list[j])
                    if i != j and sim_scores[0]["score"] > 0.5:
                        try:
                            if len(list[i]) < len(list[j]):
                                filtered_list.remove(list[i])
                            else:
                                filtered_list.remove(list[j])
                            break
                        except:
                            pass
                except Exception as e:
                    print(e)
    # ---------filtered list of news as output-------
    return filtered_list


data = []  # -------list to store all the news collected
data_dict = {}  # ------dictionary to store news with thier article links

# -----------loop across all the states in the saves states list--------------------------------------------------
with open("states_dist.csv", "r") as csvFile:
    csv_reader = csv.reader(csvFile)
    for row in csv_reader:
        driver = webdriver.Chrome(executable_path="./chromedriver")
        # ----------search for the state news from google that were reported within last 24hrs
        driver.get("https://www.google.com")
        sreachbox = driver.find_element_by_xpath(
            "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input"
        )
        sreachbox.send_keys("covid news %s\n" % row[0])

        # ---------------collect all the news within last 24hrs and apprnd them to list and dictionary assigned -------------------
        #  this loop contains all the execution blocks to cover all the errors that may occour during execution
        while 1:
            try:
                news_elements = driver.find_elements_by_xpath(
                    '//*[@id="kp-wp-tab-Latest"]/div'
                )

                print(len(news_elements))
                if len(news_elements) == 0:
                    news_elements = 100
                for i in range(1, len(news_elements)):
                    while 1:
                        try:
                            try:
                                # ---check time satmp on each news
                                Time = driver.find_element_by_xpath(
                                    '//*[@id="kp-wp-tab-Latest"]/div[%s]/g-card/div/div/div[2]/a/div/div[2]/div[3]/div[2]/span/span/span'
                                    % i
                                ).text
                            except:
                                Time = driver.find_element_by_xpath(
                                    '//*[@id="kp-wp-tab-Latest"]/div[%s]/g-card/div/div/div[2]/a/div/div[3]/div[2]/span/span/span'
                                    % i
                                ).text
                            if (
                                ("week" in str(Time))
                                or ("month" in str(Time))
                                or ("day" in str(Time))
                            ):
                                pass

                            # ----if time stamp on news is not of weeks nor months nor days, store that news
                            else:
                                try:
                                    news = driver.find_element_by_xpath(
                                        '//*[@id="kp-wp-tab-Latest"]/div[%s]/g-card/div/div/div[2]/a/div/div[2]/div[2]'
                                        % i
                                    ).text
                                except:
                                    news = driver.find_element_by_xpath(
                                        '//*[@id="kp-wp-tab-Latest"]/div[%s]/g-card/div/div/div[2]/a/div/div[2]'
                                        % i
                                    ).text
                                link = driver.find_element_by_xpath(
                                    '//*[@id="kp-wp-tab-Latest"]/div[%s]/g-card/div/div/div[2]/a'
                                    % i
                                ).get_attribute("href")
                                print(news)
                                data_dict.update({news: link})
                                data.append(news)
                            break
                        except Exception as e:
                            print(e)
                            driver.refresh()
                break

            # -----------if google HTML elements changes in home page search, this block heads to news page----------
            except:
                driver.find_element_by_xpath(
                    '//*[@id="hdtb-msb"]/div[1]/div/div[2]/a'
                ).click()
                news_elements = driver.find_elements_by_xpath(
                    '//*[@id="rso"]/div[1]/div/g-card'
                )

                print(len(news_elements))
                for i in range(1, len(news_elements)):
                    while 1:
                        try:
                            Time = driver.find_element_by_xpath(
                                '//*[@id="rso"]/div[1]/div/g-card[%s]/div/div/a/div/div[2]/div[3]/span/span/span'
                                % i
                            ).text
                            if (
                                ("week" in str(Time))
                                or ("month" in str(Time))
                                or ("days" in str(Time))
                            ):
                                pass
                            else:
                                news = driver.find_element_by_xpath(
                                    '//*[@id="rso"]/div[1]/div/g-card[%s]/div/div/a/div/div[2]/div[2]'
                                    % i
                                ).text
                                link = driver.find_element_by_xpath(
                                    '//*[@id="rso"]/div[1]/div/g-card[%s]/div/div/a' % i
                                ).get_attribute("href")
                                print(news)
                                data_dict.update({news: link})
                                data.append(news)
                            break
                        except Exception as e:
                            print(e)
                            driver.refresh()
                break
        driver.close()
        print(data_dict)
        final_data = remove_similar(data)
        print(final_data)

        # ------finally store the filtered news of each state in respective directory
        with open("data/%s/news.csv" % row[0], "w") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=";")
            for news in final_data:
                csv_writer.writerow([news, data_dict[news]])
            csvfile.close()

        # ----empty the list and dictionary for next interation
        data = []
        data_dict = {}
