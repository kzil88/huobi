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

    amount_temp = [x['vol'] for x in resu_temp['data']][1:]
    amount = np.array(amount_temp[::-1])

    vol_temp = [x['amount'] for x in resu_temp['data']][1:]
    vol = np.array(vol_temp[::-1])

    close_temp = [x['close'] for x in resu_temp['data']][1:]
    close = np.array(close_temp[::-1])

    price_avg_long0 = []
    price_avg_long = []
    price_avg_short = []
    price_close = []
    delt_list = []
    std = []
    for i in range(201,len(amount)):
        price_avg_long.append(float(amount[i-200:i+1].mean()/vol[i-200:i+1].mean()))
        price_avg_long0.append(float(amount[:i + 1].mean() / vol[:i + 1].mean()))
        if vol[i] == 0:
            temp_short = price_avg_short[-1]
            price_avg_short.append(temp_short)
        else:
            price_avg_short.append(float(amount[i]/vol[i]))
        price_close.append(close[i])
        std.append(np.array(close[i-200:i+1]).std())
        delt_list.append(float(amount[i-200:i+1].mean()/vol[i-200:i+1].mean()) / float(amount[i-1-200:i].mean()/vol[i-1-200:i].mean()))

    color = []
    #macd_temp = ta.MACD(close, 12, 26, 9)
    #macd_list = macd_temp[2][len(macd_temp[2])-len(price_close):len(macd_temp[2])]

    #macd_list = [x for x in macd_temp[2] if str(x) != 'nan']
    deal_list = []
    macd_list_resu = []
    for j in range(201,len(amount)):
        macd_list = ta.MACD(close[j-200:j+1], 12, 26, 9)[2]
        macd = macd_list[-1]
        macd_list_resu.append(macd)
        action_flag = 0
        if j > 1:
            if macd_list[-3] > macd_list[-2] and macd_list[-1] > macd_list[-2] and macd_list[-1] < 0 and macd_list[-3] < 0 and (macd_list[-3]+macd_list[-2]+macd_list[-1])<-0.079:
                action_flag = 1
            elif macd_list[-3] < macd_list[-2] and macd_list[-1] < macd_list[-2] and macd_list[-1] > 0 and macd_list[-3] > 0 and (macd_list[-3]+macd_list[-2]+macd_list[-1])>0.079:
                action_flag = -1
        if action_flag != 0:
            deal_list.append(j-201)
        if macd >= 0:
            color.append('g')
        else:
            color.append('r')

    return price_avg_long0,price_avg_long,price_avg_short,price_close,delt_list,macd_list_resu,color,deal_list,std


if __name__ == '__main__':


    coin_list = ['btc', 'eos']
    para_list_src = [(150, -150), (0.34, -0.34)]
    para_list = [[150, -150], [0.34, -0.34]]

    interval = [150,0.34]
    #para_list = [(4.5, 4), (3.5, 2)]
    para_min = '15min'
    show_len = 200

    fig = plt.figure(figsize=(20, 12))
    #plt.ion()
    #while True:
    for i in range(len(coin_list)):
        price_avg_long0,price_avg_long,price_avg_short,close,delt_list,macd_list,color,deal_list,std_src = Signal(str(coin_list[i])+'usdt',para_min,para_list[i][0],para_list[i][1],show_len)
        print('Coin : ' + str(coin_list[i])+'   Avg_Long0 : ' + str(round(price_avg_long0[-1]*100)/100)+'   Avg_Long : ' + str(round(price_avg_long[-1]*100)/100) + '   Avg_Short : ' + str(round(price_avg_short[-1]*100)/100) + '   Close : ' + str(round(close[-1]*100)/100) +'   Delt : ' + str(delt_list[-1]))
        a = 321+ i

        bar_value = np.array(price_avg_short)-np.array(price_avg_long)
        std = copy.copy(std_src)
        para_list[i][0] = np.array(std)
        para_list[i][1] = -np.array(std)

        ax = fig.add_subplot(a)
        plt.plot(range(len(price_avg_long0)),price_avg_long0,color='black')
        plt.plot(range(len(price_avg_long)),price_avg_long,color='blue')
        plt.plot(range(len(close)),close,color='green')
        plt.plot(range(len(price_avg_short)),price_avg_short,color='red')

        ax2_index = 0
        for j in range(len(deal_list)):
            if bar_value[deal_list[j]] > para_list[i][0][deal_list[j]] and macd_list[deal_list[j]] > 0:
                plt.axvline(deal_list[j],color = 'green')
                para_list[i][0][ax2_index:] += np.array(std)[ax2_index:]
                #para_list[i][1][ax2_index:] += np.array(std)[ax2_index:]
            elif bar_value[deal_list[j]] < para_list[i][1][deal_list[j]] and macd_list[deal_list[j]] < 0:
                plt.axvline(deal_list[j], color='red')
                #para_list[i][0][ax2_index:] -= np.array(std)[ax2_index:]
                para_list[i][1][ax2_index:] -= np.array(std)[ax2_index:]
        std = copy.copy(std_src)
        para_list[i][0] = np.array(std)
        para_list[i][1] = -np.array(std)


        ax2 = fig.add_subplot(a+2)
        plt.bar(range(len(price_avg_long)), bar_value,color = 'blue')
        plt.plot(range(len(para_list[i][0])), para_list[i][0], color='purple')
        plt.plot(range(len(para_list[i][1])), para_list[i][1], color='purple')
        ax2_index = 0
        for j in range(len(deal_list)):
            if bar_value[deal_list[j]] > para_list[i][0][deal_list[j]] and macd_list[deal_list[j]] > 0:
                ax2_index = deal_list[j]
                plt.axvline(deal_list[j],color = 'green')
                para_list[i][0][ax2_index:] += np.array(std)[ax2_index:]
                #para_list[i][1][ax2_index:] += np.array(std)[ax2_index:]
            elif bar_value[deal_list[j]] < para_list[i][1][deal_list[j]] and macd_list[deal_list[j]] < 0:
                ax2_index = deal_list[j]
                plt.axvline(deal_list[j], color='red')
                #para_list[i][0][ax2_index:] -= np.array(std)[ax2_index:]
                para_list[i][1][ax2_index:] -= np.array(std)[ax2_index:]
        plt.plot(range(len(para_list[i][0])),para_list[i][0],color = 'black')
        plt.plot(range(len(para_list[i][1])),para_list[i][1],color = 'black')
        std = copy.copy(std_src)
        para_list[i][0] = np.array(std)
        para_list[i][1] = -np.array(std)


        ax3 = fig.add_subplot(a + 4)
        plt.bar(range(len(macd_list)), np.array(macd_list),color=color)
        ax2_index = 0
        for j in range(len(deal_list)):
            if bar_value[deal_list[j]] > para_list[i][0][deal_list[j]] and macd_list[deal_list[j]] > 0:
                ax2_index = deal_list[j]
                plt.axvline(deal_list[j],color = 'green')
                para_list[i][0][ax2_index:] += np.array(std)[ax2_index:]
                #para_list[i][1][ax2_index:] += np.array(std)[ax2_index:]
            elif bar_value[deal_list[j]] < para_list[i][1][deal_list[j]] and macd_list[deal_list[j]] < 0:
                ax2_index = deal_list[j]
                plt.axvline(deal_list[j], color='red')
                #para_list[i][0][ax2_index:] -= np.array(std)[ax2_index:]
                para_list[i][1][ax2_index:] -= np.array(std)[ax2_index:]
        std = copy.copy(std_src)
        para_list[i][0] = np.array(std)
        para_list[i][1] = -np.array(std)

        #plt.pause(2)

    plt.show()

