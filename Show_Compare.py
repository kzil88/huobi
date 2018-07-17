import pymysql
import numpy as np
import time
import talib as ta
import datetime
import HuobiServices as hb
import matplotlib.pyplot as plt
import math
import copy


if __name__ == '__main__' :

    coin_code_src = 'btc'
    coin_code_comp = 'eos'
    para_min = '15min'
    para_interval = 2.0
    para_delt_fator = 100.0
    para_window_size = 1500


    response_src = hb.get_kline(str(coin_code_src) + 'usdt', para_min, 2000)
    resu_src = response_src['data']
    response = hb.get_kline(str(coin_code_comp) + 'usdt', para_min, 2000)
    resu_comp = response['data']


    price_list_src = []
    price_list_comp = []
    delt_list = []
    price_x_src = []
    price_x_comp = []
    std_list = []
    v_line = []
    ts_list = []
    avg_list = []
    up_list = []
    low_list = []
    stat_x_list = []
    temp_lock_ts = 0
    for i in range(len(resu_comp)):
        print(str(i+1) + '  of  ' + str(len(resu_comp)))
        if len(resu_src) > 0:
            for j in range(len(resu_src)):
                c_index = min(len(resu_src)-1-(i+j),len(resu_src)-1)
                if int(resu_src[c_index]['id']) > int(resu_comp[len(resu_comp)-1-i]['id']):
                    price_list_comp.append(float(resu_comp[len(resu_comp)-1-i]['close'])*para_delt_fator)
                    price_x_comp.append(i)
                    if int(resu_src[c_index]['id']) > temp_lock_ts :
                        temp_lock_ts = int(resu_src[c_index]['id'])
                        price_list_src.append(float(resu_src[c_index]['close']))
                        price_x_src.append(i)
                        delt = float(float(resu_comp[len(resu_comp)-1-i]['close'])*para_delt_fator) - float(resu_src[c_index]['close'])
                        delt_list.append(delt)
                        if len(delt_list) >= para_window_size:
                            std = np.array(delt_list[len(delt_list)-para_window_size:len(delt_list)-1]).std()
                            mean = np.array(delt_list[len(delt_list)-para_window_size:len(delt_list)-1]).mean()
                            stat_x_list.append(i)
                            avg_list.append(mean)
                            up_list.append(mean+std*para_interval)
                            low_list.append(mean-std*para_interval)
                            if abs(delt - mean) > abs(std)*para_interval:
                                v_line.append(i)
                                ts_list.append(int(resu_comp[len(resu_comp)-1-i]['id']))
                    break


    print(ts_list)

    fig = plt.figure(figsize=(20, 12))
    ax = fig.add_subplot(311)
    plt.plot(price_x_src,price_list_src,color='blue')
    # plt.axvline(v_line[0], color='green')
    # for a in range(len(v_line)):
    #     plt.axvline(v_line[a], color='green')
    ax2 = fig.add_subplot(312)
    plt.plot(price_x_comp,price_list_comp,color='red')
    # plt.axvline(v_line[0], color='green')

    # for a in range(len(v_line)):
    #     plt.axvline(v_line[a], color='green')
    ax3 = fig.add_subplot(313)
    plt.plot(price_x_src,delt_list,color='red')
    plt.plot(stat_x_list,avg_list,color='blue')
    #plt.plot(price_x_src,np.array(avg_list)*1.3,color='black')
    plt.plot(stat_x_list,up_list,color='black')
    plt.plot(stat_x_list,low_list,color='black')
    #plt.axvline(v_line[0], color='green')
    # for b in range(len(v_line)):
    #     plt.axvline(v_line[b], color='green')

    plt.show()






