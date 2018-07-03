# -*- coding:utf8 -*-
import numpy as np
import time
import talib as ta
import datetime
import HuobiServices as hb
import matplotlib.pyplot as plt
import math
import copy
#
# def Signal(coin_symbol,para_min,para_up,para_low,show_len):
#     resu_temp = hb.get_kline(coin_symbol, para_min, 201+show_len-1)
#     cur_kline_ts = resu_temp['data'][0]['id']
#
#     date_seq = [time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(x['id']))) for x in resu_temp['data']][::-1]
#     close_temp = [x['close'] for x in resu_temp['data']][1:]
#     close = np.array(close_temp[::-1])
#
#     resu = []
#     color = []
#     for i in range(show_len-1):
#         macd_temp = ta.MACD(close[:200+i], 12, 26, 9)
#         up_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).max() * para_up
#         low_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).min() * para_low
#
#         up_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).mean()
#         low_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).mean()
#         macd = macd_temp[2][-1]*2
#         if macd >= 0:
#             color.append('g')
#         else:
#             color.append('r')
#         resu.append(macd)
#
#     action_flag = 0
#
#     # flag
#     if (((macd_temp[2][-1] + macd_temp[2][-2] + macd_temp[2][-3]) * 2) < low_limit) and (
#             macd_temp[2][-2] < macd_temp[2][-1]) and (macd_temp[2][-2] < macd_temp[2][-3]) and (
#             macd_temp[2][-1] < 0) and (macd_temp[2][-3] < 0) and (
#             macd_temp[2][-1] - macd_temp[2][-2] < abs(para_low * low_mean)):
#         action_flag = 1
#     elif (((macd_temp[2][-1] + macd_temp[2][-2] + macd_temp[2][-3]) * 2) > up_limit) and (
#             macd_temp[2][-2] > macd_temp[2][-1]) and (macd_temp[2][-2] > macd_temp[2][-3]) and (
#             macd_temp[2][-1] > 0) and (macd_temp[2][-3] > 0) and (
#             macd_temp[2][-2] - macd_temp[2][-1] < abs(para_up * up_mean)):
#         action_flag = -1
#     return action_flag,resu,color


def Signal(coin_symbol,para_min,para_up,para_low):
    resu_temp = hb.get_kline(coin_symbol, para_min, 200)
    cur_kline_ts = resu_temp['data'][0]['id']

    date_seq = [time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(x['id']))) for x in resu_temp['data']][::-1]
    close_temp = [x['close'] for x in resu_temp['data']][1:]
    close = np.array(close_temp[::-1])

    resu = []
    color = []
    macd_temp = ta.MACD(close, 12, 26, 9)
    up_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).max() * para_up
    low_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).min() * para_low
    up_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).mean()
    low_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).mean()
    macd_list = [x for x in macd_temp[2] if str(x) != 'nan']
    for i in range(len(macd_list)):
        macd = macd_list[i]
        if macd >= 0:
            color.append('g')
        else:
            color.append('r')
        resu.append(macd)

    action_flag = 0

    # flag
    if (((macd_temp[2][-1] + macd_temp[2][-2] + macd_temp[2][-3]) * 2) < low_limit) and (
            macd_temp[2][-2] < macd_temp[2][-1]) and (macd_temp[2][-2] < macd_temp[2][-3]) and (
            macd_temp[2][-1] < 0) and (macd_temp[2][-3] < 0) and (
            macd_temp[2][-1] - macd_temp[2][-2] < abs(para_low * low_mean)):
        action_flag = 1
    elif (((macd_temp[2][-1] + macd_temp[2][-2] + macd_temp[2][-3]) * 2) > up_limit) and (
            macd_temp[2][-2] > macd_temp[2][-1]) and (macd_temp[2][-2] > macd_temp[2][-3]) and (
            macd_temp[2][-1] > 0) and (macd_temp[2][-3] > 0) and (
            macd_temp[2][-2] - macd_temp[2][-1] < abs(para_up * up_mean)):
        action_flag = -1
    return action_flag,resu,color,up_limit,low_limit


if __name__ == '__main__':
    coin_list = ['btc', 'eos']
    para_list = [(2.5, 2.5), (1.5, 4.5)]
    #para_list = [(4.5, 4), (3.5, 2)]
    para_min = '15min'

    fig = plt.figure(figsize=(20, 12))
    for i in range(len(coin_list)):
        signal,resu,color,up_limit,low_limit = Signal(str(coin_list[i])+'usdt',para_min,para_list[i][0],para_list[i][1])
        a = 211+i
        ax = fig.add_subplot(a)
        plt.bar(range(len(resu)), resu, color=''.join(color))
        plt.plot(range(len(resu)), [up_limit/6]*len(resu), color='blue')
        plt.plot(range(len(resu)), [low_limit/6]*len(resu), color='blue')
    plt.show()

