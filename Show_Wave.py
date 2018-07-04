# -*- coding:utf8 -*-
import numpy as np
import time
import talib as ta
import datetime
import HuobiServices as hb
import matplotlib.pyplot as plt
import math
import copy

def Signal(coin_symbol,para_min,para_up,para_low,show_len):
    resu_temp = hb.get_kline(coin_symbol, para_min, 200+show_len)
    cur_kline_ts = resu_temp['data'][0]['id']
    date_seq = [time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(x['id']))) for x in resu_temp['data']][::-1]

    amount_temp = [x['vol'] for x in resu_temp['data']]
    amount = np.array(amount_temp[::-1])

    vol_temp = [x['amount'] for x in resu_temp['data']]
    vol = np.array(vol_temp[::-1])

    close_temp = [x['close'] for x in resu_temp['data']]
    close = np.array(close_temp[::-1])

    price_avg_long0 = []
    price_avg_long = []
    price_avg_short = []
    price_close = []
    delt_list = []
    for i in range(201,len(amount)):
        price_avg_long.append(float(amount[i-200:i+1].mean()/vol[i-200:i+1].mean()))
        price_avg_long0.append(float(amount[:i + 1].mean() / vol[:i + 1].mean()))
        if vol[i] == 0:
            temp_short = price_avg_short[-1]
            price_avg_short.append(temp_short)
        else:
            price_avg_short.append(float(amount[i]/vol[i]))
        price_close.append(close[i])
        delt_list.append(float(amount[i-200:i+1].mean()/vol[i-200:i+1].mean()) / float(amount[i-1-200:i].mean()/vol[i-1-200:i].mean()))

    resu = []
    color = []
    macd_temp = ta.MACD(close, 12, 26, 9)
    # up_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).max() * para_up
    # low_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).min() * para_low
    # up_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).mean()
    # low_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).mean()
    macd_list = macd_temp[2][len(macd_temp[2])-len(price_close):len(macd_temp[2])]

    #macd_list = [x for x in macd_temp[2] if str(x) != 'nan']

    deal_list = []
    for j in range(len(macd_list)):
        macd = macd_list[j]
        action_flag = 0
        if j > 1:
            if macd_list[j-2] > macd_list[j-1] and macd_list[j] > macd_list[j-1] and macd_list[j] < 0 :
                action_flag = 1
            elif macd_list[j-2] < macd_list[j-1] and macd_list[j] < macd_list[j-1] and macd_list[j] > 0 :
                action_flag = -1
        if action_flag != 0:
            deal_list.append(j)
        if macd >= 0:
            color.append('g')
        else:
            color.append('r')
        resu.append(macd)

    return price_avg_long0,price_avg_long,price_avg_short,price_close,delt_list,macd_list,color,deal_list


if __name__ == '__main__':


    coin_list = ['btc', 'eos']
    para_list = [(170, -470), (0.34, -0.34)]
    #para_list = [(4.5, 4), (3.5, 2)]
    para_min = '15min'
    show_len = 200

    fig = plt.figure(figsize=(20, 12))
    #plt.ion()

    #while True:
    for i in range(len(coin_list)):
        #signal,resu,color,up_limit,low_limit = Signal(str(coin_list[i])+'usdt',para_min,para_list[i][0],para_list[i][1])
        price_avg_long0,price_avg_long,price_avg_short,close,delt_list,macd_list,color,deal_list = Signal(str(coin_list[i])+'usdt',para_min,para_list[i][0],para_list[i][1],show_len)
        print('Coin : ' + str(coin_list[i])+'   Avg_Long0 : ' + str(round(price_avg_long0[-1]*100)/100)+'   Avg_Long : ' + str(round(price_avg_long[-1]*100)/100) + '   Avg_Short : ' + str(round(price_avg_short[-1]*100)/100) + '   Close : ' + str(round(close[-1]*100)/100) +'   Delt : ' + str(delt_list[-1]))
        a = 321+ i
        ax = fig.add_subplot(a)
        #plt.bar(range(len(resu)), resu)
        plt.plot(range(len(price_avg_long0)),price_avg_long0,color='black')
        plt.plot(range(len(price_avg_long)),price_avg_long,color='blue')
        plt.plot(range(len(close)),close,color='green')
        plt.plot(range(len(price_avg_short)),price_avg_short,color='red')

        # resu_bar = []
        # for j in range(len(price_avg_long)):
        #     resu_bar.append((price_avg_short[j]-price_avg_long[j])*delt_list[j])
        ax2 = fig.add_subplot(a+2)
        bar_value = np.array(price_avg_short)-np.array(price_avg_long)
        plt.bar(range(len(price_avg_long)), bar_value)
        plt.plot(range(len(price_avg_long)), [para_list[i][0]] * len(price_avg_long), color='red')
        plt.plot(range(len(price_avg_long)), [para_list[i][1]] * len(price_avg_long), color='red')
        #plt.bar(range(len(price_avg_long)), np.array(price_avg_short) - np.array(close))
        #plt.bar(range(len(price_avg_long)), resu_bar)
        ax3 = fig.add_subplot(a + 4)
        plt.bar(range(len(macd_list)), np.array(macd_list),color=color)
        for j in range(len(deal_list)):
            if bar_value[deal_list[j]] > para_list[i][0] or bar_value[deal_list[j]] < para_list[i][1]:
                plt.axvline(deal_list[j])
        #plt.plot(np.array(macd_list), range(min(macd_list),max(macd_list)), color='blue')
        #plt.plot(range(len(price_avg_long)), [para_list[i][1]] * len(price_avg_long), color='red')


    #plt.pause(2)

    plt.show()

