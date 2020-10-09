# try to post on slack
import requests
import json
import time
import datetime


def read_last_log(day, channels=[2, 5, 6], plotting=False):
    """ Read the log file of Blue fors. Make a nice plot of it."""

    log_files = [
        '{1}/CH{0} T {1}.log'.format(ch, day.strftime('%Y-%m-%d')[2:]) for ch in channels]
    labels = ['4K', 'Still', 'MCX']
    my_day = day
    log_data = {}

    # Reading the file line by line:
    for fname, label in zip(log_files, labels):
        with open(path + fname, "r") as f:
            data = [line.split(',') for line in f.read().splitlines() if line]
            log_data[label] = float(data[-1][2])
    return log_data


good_value = {'4K': 4., 'Still': 3., 'MCX': 0.01}

if __name__ == "__main__":
    slack_msg = {
        "text": " Monitoring of Bigfridge is initiated :)"
    }
    requests.post(web_hook_url, data=json.dumps(slack_msg))

    for k in range(2):
        today = datetime.datetime(2019, 8, 24)
        # today = datetime.datetime.now()
        log_data = read_last_log(today)
        all_is_good = [abs(log_data[key]-good_value[key]) /
                       good_value[key] < .02 for key in log_data.keys()]

        if not all(all_is_good):
            slack_msg = {
                "attachments": [
                    {
                        "color": "danger",
                        "pretext": "Something is wrong with BigFridge! Please check!",
                        "text": "4K plate: {0:.02f} K \n Still: {1:.02f} K \n MCX: {2:.04f} K".format(log_data['4K'], log_data['Still'], log_data['MCX']),
                    }
                ]
            }
            requests.post(web_hook_url, data=json.dumps(slack_msg))
        time.sleep(2*6)
