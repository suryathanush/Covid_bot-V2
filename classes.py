import bar_chart_race as bcr  # ---library to draw charts
import csv
from fuzzywuzzy import fuzz  # --library to check misspelled words
import pandas as pd
import os
import cv2


# ---------------------------- CLASS TO PROCESS USER'S MESSAGE ---------------------------------------------------------------------------------------------------------------
# class with method check_func() to process the messages from users
# act accorrding to the messages from users
class msgresponse:
    def check_func(self, number, message):
        try:
            self.number = str(number.replace(" ", ""))
            self.number = str(
                self.number.replace("+", "")
            )  # --correctly phrase the phone numbers
            self.msg = str(message)
            self.prob_state_prev = 0

            # ---------------if message was 'hi' or 'hello'------------------------------------------------
            if ((fuzz.ratio(message.lower(), "hi")) > 85) or (
                (fuzz.ratio(message.lower(), "hello")) > 80
            ):
                return "hi\r\nGood to see you\r\nif you haven't subscribed yet, please message your state name"

            # ----------------if the message was stop, delete the user subscription------------------------
            if (fuzz.ratio(message.lower(), "stop")) > 80:

                self.df = pd.read_csv("users.csv", header=0)
                # --check for the user's subscription by looping accross user's data
                for ind in self.df.index:
                    print(self.df["mobile_number"][ind])
                    if str(self.df["mobile_number"][ind]) == self.number:
                        # ---if subcription was found, try deleting it--------
                        try:
                            self.df.drop([ind], inplace=True)
                            self.df.to_csv("users.csv", index=False)
                            return "you have unsubscribed from the further updates. \r\n you can resume the service anytime by sending your state name"
                        except Exception as e:
                            print(e)
                        break
                    else:
                        pass

            # ------------------if message was india--------------------------------------------------------
            if (fuzz.ratio(message.lower(), "india")) > 85:
                return "you will be recieving india wide updates too by default if subscribed for any state"

            # ----------------if message was not "stop" nor "india",execute else block------------------------
            else:
                self.new_user = True  # --flag to set False if user already exists
                try:
                    # --compare state name in message with saved names----------
                    with open("states_dist.csv", "r") as csvFile:
                        self.reader = csv.reader(csvFile)
                        self.df = pd.read_csv("users.csv", header=0)
                        for row in self.reader:
                            self.prob_state = fuzz.ratio(
                                self.msg.lower(), row[0].lower()
                            )
                            # check for state name which is most relevant to message
                            if self.prob_state > self.prob_state_prev:
                                self.state_info = row
                                self.prob_state_prev = self.prob_state

                        # ---if state name in message was close to any of in saved names--
                        if self.prob_state_prev >= 80:
                            for ind in self.df.index:
                                # --if user already exists, update the existing subscrition-----
                                if str(self.df["mobile_number"][ind]) == self.number:
                                    self.df.loc[ind] = [
                                        self.number,
                                        self.state_info[0],
                                        "None",
                                    ]
                                    self.df.to_csv("users.csv", index=False)
                                    self.new_user = False  # set new_user flag to False
                                    break
                            # --if message was from new user, create new subscription---------
                            if self.new_user:
                                self.df.loc[len(self.df.index)] = [
                                    self.number,
                                    self.state_info[0],
                                    "None",
                                ]
                                self.df.to_csv("users.csv", index=False)
                            return (
                                "*your subscription was successful for %s*\r\nYou will be receiving daily COVID updates every early morning\r\nTo stop the service send *stop*\r\nNo reply needed\r\n*.... BE MASKED, STAY SAFE ....*"
                                % self.state_info[0]
                            )

                        # --if probability was less, send confirmation msg-----
                        if self.prob_state_prev > 45 and self.prob_state_prev < 80:
                            return (
                                "did you mean *%s*\r\nplease check your state spelling and resend again"
                                % self.state_info[0]
                            )
                        else:
                            return "i did'nt get you\r\nplease check you state spelling and resend again"
                except:
                    return "i cound not undersand\n please check the spelling and resend again \n example : *Tamil Nadu*"
        except:
            return "something went wrong, please try again"


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# -------------------------------- cLASS TO CONVERT .MP4 TO JPG -------------------------------------------------------------------------------------------------------------------------------------
#   since bar_chart_race returns .mp4 files of graphs,
#    the converrt() method of this class convert them to jpg
class vid2jpg:
    def __init__(self):
        self.description = ["new_confirmed", "new_recovered", "new_deceased"]

    def convert(self, state):
        # --loop across all 3 graphs "new_confirmed", "new_recovered", "new_deceased"--
        for self.i in range(3):
            self.cam = cv2.VideoCapture(
                "data/%s/%s.mp4" % (state, self.description[self.i])
            )
            # ---read the 1st frame of each vedio and save it as jpg---------
            _, self.frame = self.cam.read()
            cv2.imwrite(
                "data/%s/%s.jpg" % (state, self.description[self.i]), img=self.frame
            )
            self.cam.release()
            # ----------------------------------------------------------------
            cv2.destroyAllWindows()

            # ---after converting to jpg, delete the .mp4
            os.remove("data/%s/%s.mp4" % (state, self.description[self.i]))


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# ------------------------------ CLASS TO DRAW GRAPHS FROM STATE WISE DATA ------------------------------------------------------------------------------------------------------------------------------
#   draw() method is used to draw graphs
#     bcr is a matplotlib based library
class barchart:
    def __init__(self):
        self.description = ["new_confirmed", "new_recovered", "new_deceased"]

    # ------------summary() function to add summary lines to graphs-------------------------------------------------------------
    #   add state name, graph info and total cases from graph
    def summary(self, values, ranks):
        self.total = int(values.sum())
        s = f"{self.state} \n {self.description[self.i]} cases \n\n Total {self.description[self.i]} cases \n: {self.total:,.0f}"

        # ----------based on number of districts, use appropriate summary parameters----------
        if len(self.dist) > 70:
            return {
                "x": 0.99,
                "y": 0.15,
                "s": s,
                "ha": "right",
                "color": "red",
                "size": 40,
            }
        if 70 >= len(self.dist) >= 45:
            return {
                "x": 0.99,
                "y": 0.15,
                "s": s,
                "ha": "right",
                "color": "red",
                "size": 30,
            }
        if len(self.dist) < 45:
            return {
                "x": 0.99,
                "y": 0.15,
                "s": s,
                "ha": "right",
                "color": "red",
                "size": 30,
            }

        # ------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------------------------------------

    # ------------draw() function to draw graphs from list of data----------------------------------------------------------------
    def draw(
        self, state, dist, dist_confirmed, dist_deceased, dist_recovered, date_yesterday
    ):
        self.data = [{}, {}, {}]
        self.state = state
        self.dist = dist
        # ----create dictionaries of confirmed,recovered and deceased cases count with district name as key
        for self.i in range(len(self.dist)):
            self.data[0].update({dist[self.i]: int(dist_confirmed[self.i])})
            self.data[1].update({dist[self.i]: int(dist_recovered[self.i])})
            self.data[2].update({dist[self.i]: int(dist_deceased[self.i])})

        # ------------based on the number of districts in present state, use appropriate tuned graph parameters-----------------
        if len(dist) > 70:
            for self.i in range(3):
                self.df = pd.DataFrame(self.data[self.i], index=[date_yesterday])
                bcr.bar_chart_race(
                    df=self.df,
                    filename="data/%s/%s.mp4" % (self.state, self.description[self.i]),
                    figsize=(15, 30),
                    dpi=144,
                    tick_label_size=18,
                    bar_label_size=18,
                    period_label={
                        "x": 0.99,
                        "y": 0.3,
                        "ha": "right",
                        "size": 40,
                    },
                    period_summary_func=self.summary,  # ---function to add summary lines on graph
                    shared_fontdict={
                        "family": "DejaVu Sans",
                        "size": 15,
                        "weight": "bold",
                    },
                )
        if 45 <= len(self.dist) <= 70:
            for self.i in range(3):
                self.df = pd.DataFrame(self.data[self.i], index=[date_yesterday])
                bcr.bar_chart_race(
                    df=self.df,
                    filename="data/%s/%s.mp4" % (self.state, self.description[self.i]),
                    figsize=(10, 20),
                    dpi=144,
                    tick_label_size=18,
                    bar_label_size=18,
                    period_label={
                        "x": 0.99,
                        "y": 0.32,
                        "ha": "right",
                        "size": 30,
                    },
                    period_summary_func=self.summary,
                    shared_fontdict={
                        "family": "DejaVu Sans",
                        "size": 15,
                        "weight": "bold",
                    },
                )
        if 30 <= len(self.dist) < 45:
            for self.i in range(3):
                self.df = pd.DataFrame(self.data[self.i], index=[date_yesterday])
                bcr.bar_chart_race(
                    df=self.df,
                    filename="data/%s/%s.mp4" % (self.state, self.description[self.i]),
                    figsize=(12, 17),
                    dpi=240,
                    tick_label_size=18,
                    bar_label_size=18,
                    period_label={
                        "x": 0.99,
                        "y": 0.34,
                        "ha": "right",
                        "size": 30,
                    },
                    period_summary_func=self.summary,
                    shared_fontdict={
                        "family": "DejaVu Sans",
                        "size": 15,
                        "weight": "bold",
                    },
                )
        if 20 <= len(self.dist) < 30:
            for self.i in range(3):
                self.df = pd.DataFrame(self.data[self.i], index=[date_yesterday])
                bcr.bar_chart_race(
                    df=self.df,
                    filename="data/%s/%s.mp4" % (self.state, self.description[self.i]),
                    figsize=(12, 17),
                    dpi=240,
                    tick_label_size=20,
                    bar_label_size=20,
                    period_label={
                        "x": 0.99,
                        "y": 0.34,
                        "ha": "right",
                        "size": 30,
                    },
                    period_summary_func=self.summary,
                    shared_fontdict={
                        "family": "DejaVu Sans",
                        "size": 15,
                        "weight": "bold",
                    },
                )
        if (len(self.dist) < 20) and (self.dist[0] != "Unknown"):
            for self.i in range(3):
                self.df = pd.DataFrame(self.data[self.i], index=[date_yesterday])
                bcr.bar_chart_race(
                    df=self.df,
                    filename="data/%s/%s.mp4" % (self.state, self.description[self.i]),
                    figsize=(12, 17),
                    dpi=240,
                    tick_label_size=25,
                    bar_label_size=25,
                    period_label={
                        "x": 0.99,
                        "y": 0.34,
                        "ha": "right",
                        "size": 30,
                    },
                    period_summary_func=self.summary,
                    shared_fontdict={
                        "family": "DejaVu Sans",
                        "size": 15,
                        "weight": "bold",
                    },
                )
        # ----if district was unknown and no other district was present-----
        if (len(self.dist) == 1) and (self.dist[0] == "Unknown"):
            self.data[0] = {"Total": int(dist_confirmed[self.i])}
            self.data[1] = {"Total": int(dist_recovered[self.i])}
            self.data[2] = {"Total": int(dist_deceased[self.i])}
            for self.i in range(3):
                self.df = pd.DataFrame(self.data[self.i], index=[date_yesterday])
                bcr.bar_chart_race(
                    df=self.df,
                    filename="data/%s/%s.mp4" % (self.state, self.description[self.i]),
                    dpi=240,
                    title="%s cases in %s \n(district wise data not announced by Govt.)"
                    % (self.description[self.i], self.state),
                    shared_fontdict={
                        "family": "DejaVu Sans",
                        "size": 15,
                        "weight": "bold",
                    },
                )

    # ---------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# ------------------------------ CLASS TO DRAW GRAPHS FOR INDIA WISE DATA ------------------------------------------------------------------------------------------------------------------------------
class barchart_total:
    def __init__(self):
        self.description = ["new_confirmed", "new_recovered", "new_deceased"]

    # ------------summary() function to add summary lines to graphs-------------------------------------------------------------
    #   add graph info and total cases from graph
    def summary(self, values, ranks):
        self.total = int(values.sum())
        s = f"India \n {self.description[self.i]} cases \n\n Total {self.description[self.i]} cases \n: {self.total:,.0f}"
        return {
            "x": 0.99,
            "y": 0.2,
            "s": s,
            "ha": "right",
            "color": "red",
            "size": 40,
        }

    # ---------------------------------------------------------------------------------------------------------------------------

    # ------------draw() function to draw graphs from list of data----------------------------------------------------------------
    def draw(self, state_data, date_yesterday):
        for self.i in range(3):
            df = pd.DataFrame(state_data[self.i], index=[date_yesterday])
            bcr.bar_chart_race(
                df=df,
                filename="data/india_%s.mp4" % self.description[self.i],
                title="%s cases allover india" % self.description[self.i],
                figsize=(12, 17),
                dpi=240,
                tick_label_size=20,
                bar_label_size=20,
                period_label={
                    "x": 0.99,
                    "y": 0.40,
                    "ha": "right",
                    "size": 30,
                },
                period_summary_func=self.summary,
                shared_fontdict={
                    "family": "DejaVu Sans",
                    "size": 15,
                    "weight": "bold",
                },
            )

            # -----------convert the produced graphs from .mp4 to jpg----------------------
            #   bcr returns the graphs in vedio format
            #     we extract the first frame of  each vedio and for jpg
            #       later delte the vedio file
            self.cam = cv2.VideoCapture("data/india_%s.mp4" % self.description[self.i])
            _, self.frame = self.cam.read()
            cv2.imwrite("data/india_%s.jpg" % self.description[self.i], img=self.frame)
            self.cam.release()
            cv2.destroyAllWindows()
            os.remove("data/india_%s.mp4" % self.description[self.i])

    # -------------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
