#!/usr/bin/env python

""" differents tools to reads bluefors log file """

import pandas as pd
import datetime

temperature_labels = {1: '50K', 2: '4K', 5: 'Still', 6: 'MXC'}

pressure_labels = ['P1: OVC', 'P2: Still return', 'P3: Injection',
                   'P4: before trap', 'P5: Tank',
                   'P6: OVC pumping lines']

# temperature functions


def load_BF_log_single_day(path_to_log, day, channels=[1, 2, 5, 6]):
    """ Construct a single dataframe out of the log file from BlueFors """
    dfs = []
    labels = [temperature_labels[k] for k in channels]

    # change day into a datetime format for easier manipulation
    if isinstance(day, str):
        day = datetime.date.fromisoformat(day)

    log_files = [path_to_log + '{1}/CH{0} T {1}.log'.format(
        ch, day.strftime('%Y-%m-%d')[2:]) for ch in channels]

    for fname, label in zip(log_files, labels):
        df = pd.read_csv(fname,
                         sep=",",
                         header=None)
        df.columns = ['date', 'time', label]
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'],
                                        format=' %d-%m-%y %H:%M:%S')
        df = df.drop('date', 1)
        df = df.drop('time', 1)
        dfs.append(df)

    # merging all the dframes into one
    from functools import reduce
    df_merged = reduce(lambda left, right: pd.merge(
        left, right, on=['datetime'], how='outer'), dfs)
    return df_merged


def load_BF_log(days, path_to_log='log/', channels=[1, 2, 5, 6]):
    """ load and concatenate several day fo BF logfiles"""
    if isinstance(days, list):
        days = [datetime.date.fromisoformat(day) for day in days]
    df = []

    # loop through the days
    for day in days:
        df.append(load_BF_log_single_day(path_to_log, day=day))

    # return the concatenated dataframe
    return pd.concat(df)


def read_time(day_str, time_str):
    """
    convert the day and time string of the BlueFors temperature
    log into datetime object
    """
    date = '20'+day_str[-2:] + day_str[3:7] + day_str[1:3]
    date = datetime.date.fromisoformat(date)
    time = datetime.time.fromisoformat(time_str)
    return datetime.datetime.combine(date, time)


def load_pressure_log_single_day(day):
    """
    Load the temperature log of the bluefors fridge
    """
    fname = f'log/{day[2:]}/maxigauge {day[2:]}.log'
    df = pd.read_csv(fname,
                     sep=",",
                     header=None)
    df = df[[0, 1, 5, 11, 17, 23, 29, 35]].rename(cnames, axis='columns')
    df.date = day

    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'],
                                    format='%Y-%m-%d %H:%M:%S')
    df = df.drop('date', 1)
    df = df.drop('time', 1)

    return df


def load_pressure_log(day_list):
    """
    Load several day of log temperature
    """
    df = []
    for day in day_list:
        df.append(load_temperature_log_single_day(day))
    return pd.concat(df)
