#!/usr/bin/env python 
from tkinter import Tk, Label, Button, StringVar, Entry
import requests
import json
import time
import datetime
import logging
logger = logging.getLogger('bluefors')


def read_last_log(day,path, channels = [2, 5, 6]):
    """ Read the log file of Blue fors. Make a nice plot of it."""
    
    log_files = ['{1}/CH{0} T {1}.log'.format(ch, day.strftime('%Y-%m-%d')[2:]) for ch in channels]
    labels = ['4K', 'still', 'MXC']
    my_day = day
    log_data = {}
    
    # Reading the file line by line:
    for fname, label in zip(log_files,labels):
        with open(path + fname, "r") as f:
            data = [line.split(',') for line in f.read().splitlines() if line]
            log_data[label] = float(data[-1][2])
    return log_data


class BlueforsMonitor:
    LABEL_TEXT = [
        "Monitoring the temperature of the Bluefors Fridge",
        "Send a notification on slack if something bad happen",
    ]

    def __init__(self, master):
        self.daily_update = True
        self.master = master
        master.title("BlueFors monitor")

        self.set_temp = {'4K': 3.4, 'still': 0.99, 'MXC': 0.0098}
        self.web_hook = 'https://hooks.slack.com/services/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'
        self.path = 'C:/BlueFors/logs/'
        self.tol = .1

        # closing the windows
        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.grid(column=1, row=6)

        # # start monitoring
        # self.start_monitoring_button = Button(master, text="Monitoring", command=self.start_monitoring)
        # self.start_monitoring_button.grid(column=1, row=5)

        # input token
        self.token_label = Label(master, text='address')
        self.token_label.grid(column=0, row=0)
        self.token = StringVar(root, value=self.web_hook)
        self.token_input = Entry(master, textvariable=self.token, width=25)
        self.token_input.grid(column=1, row=0)
        self.token_button = Button(master, text="Set token", command=self.set_token)
        self.token_button.grid(column=2, row=0)

        # input temperatures
        self.T_4K_label = Label(master, text='4K (K)')
        self.T_4K_label.grid(column=0, row=1)
        self.T_4K = StringVar(root, value=self.set_temp['4K'])
        self.T_4K_input = Entry(master, width=25, textvariable=self.T_4K)
        self.T_4K_input.grid(column=1, row=1)
        self.T_4K_button = Button(master, text="Set 4K", command=self.set_4K)
        self.T_4K_button.grid(column=2, row=1)

        self.T_still_label = Label(master, text='Still (K)')
        self.T_still_label.grid(column=0, row=2)
        self.T_still = StringVar(root, value=self.set_temp['still'])
        self.T_still_input = Entry(master, width=25, textvariable=self.T_still)
        self.T_still_input.grid(column=1, row =2)
        self.T_still_button = Button(master, text="Set Still", command=self.set_still)
        self.T_still_button.grid(column=2, row=2)

        self.T_MXC_label = Label(master, text='MXC (K)')
        self.T_MXC_label.grid(column=0, row=3)
        self.T_MXC = StringVar(root, value=self.set_temp['MXC'])
        self.T_MXC_input = Entry(master, width=25, textvariable=self.T_MXC)
        self.T_MXC_input.grid(column=1, row=3)
        self.T_MXC_button = Button(master, 
                                  text="Set MXC",
                                  command=self.set_still)
        self.T_MXC_button.grid(column=2, row=3)

        self.tol_label = Label(master, text='tolerance (%)')
        self.tol_label.grid(column=0, row=4)
        self.vartol = StringVar(root, value=self.tol*100)
        self.tol_input = Entry(master, width=25, textvariable=self.vartol)
        self.tol_input.grid(column=1, row =4)
        self.tol_button = Button(master, 
                                  text="Set tol",
                                  command=self.set_tol)
        self.tol_button.grid(column=2, row=4)

    def monitoring(self):
        # self.label.configure(text="monitoring now")
        self.today = datetime.datetime.today()
        if self.daily_update and (self.today.hour == 9) and (self.today.minute < 15):
            log_data = read_last_log(self.today, self.path)
            slack_msg = {
                "attachments": [
                    {
                        "color": "good",
                        "pretext": "Daily update! The temperature are currently:",
                        "text": "4K plate: {0:.02f} K \n Still: {1:.02f} K \n MXC: {2:.04f} K".format(log_data['4K'],
                                                                                                      log_data['still'],
                                                                                                      log_data['MXC']),
                    }
                ]
            }
            requests.post(self.web_hook, data=json.dumps(slack_msg))

        # try to find the data
        try:
            # fetch the data
            log_data = read_last_log(self.today, self.path)

            # convert the data into a boolean if the state is good or not
            all_is_good = [ abs(log_data[key]-self.set_temp[key])/self.set_temp[key]< self.tol for key in log_data.keys() ]

            # logging into the logger
            if all(all_is_good):
                logger.info(f'Fridge in working properly')

            # send a message to slack
            if not all(all_is_good):
                logger.warning(f'Temperature are out of tolerance')
                slack_msg = {
                            "attachments": [
                                {
                                "color": "danger",
                                "pretext": "@channel Something is wrong with BigFridge! Please check!",
                                "text": "4K plate: {0:.02f} K \n Still: {1:.02f} K \n MXC: {2:.04f} K".format(log_data['4K'], log_data['still'], log_data['MXC']),
                                }
                                ]
                            }
                requests.post(self.web_hook, data=json.dumps(slack_msg))

        except FileNotFoundError:
            logging.warning("File not found. This can be a bad timing issue")

        # wait for 15 min before rechecking the temperature
        root.after(15*60*1000, self.monitoring)

    def start_monitoring(self):
        #self.label.configure(text="monitoring now")
        today = datetime.datetime.today()
        # today = datetime.datetime.now()
        log_data = read_last_log(today, self.path)
        slack_msg = {
                    "attachments": [
                        {
                        "color": "good",
                        "pretext": "Monitoring of bigFridge started! The temperature are currently:",
                        "text": "4K plate: {0:.02f} K \n Still: {1:.02f} K \n MXC: {2:.04f} K".format(log_data['4K'], log_data['still'], log_data['MXC']),
                        }
                        ]
                       }
        requests.post(self.web_hook, data=json.dumps(slack_msg))

    def set_token(self):
        self.token = self.token_input.get()

    def set_4K(self):
        self.set_temp['4K'] = float(self.T_4K_input.get())

    def set_still(self):
        self.set_temp['still'] = float(self.T_still_input.get())

    def set_MXC(self):
        self.set_temp['MXC'] = float(self.T_MXC_input.get())

    def set_tol(self):
        self.tol = float(self.tol_input.get())/100.

root = Tk()
my_gui = BlueforsMonitor(root)
root.after(0, my_gui.start_monitoring)
root.after(60, my_gui.monitoring)
root.mainloop()