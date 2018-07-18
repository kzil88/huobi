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

    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    coin_code_src = 'btc'
    coin_code_comp = 'eth'
    para_min = '30min'
    para_interval = 2.0
    para_delt_fator = 10.0


    sql_select_comp = "select * from %s_%s a order by a.timestamp desc limit 5000"%(coin_code_comp,para_min)
    cursor.execute(sql_select_comp)
    done_set_select_comp = cursor.fetchall()
    db.commit()
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
    temp_lock_ts = 0
    for i in range(0,len(done_set_select_comp)):
        print(str(i+1) + '  of  ' + str(len(done_set_select_comp)))
        sql_select_src = "select * from %s_%s a where a.timestamp > %i order by a.timestamp asc limit 1"%(coin_code_src,para_min,int(done_set_select_comp[-1-i][-1]))
        cursor.execute(sql_select_src)
        temp_done_set = cursor.fetchall()
        db.commit()
        if len(temp_done_set) > 0:
            price_list_comp.append(float(done_set_select_comp[i][2])*para_delt_fator)
            price_x_comp.append(i)
            if int(temp_done_set[0][-1]) > temp_lock_ts :
                temp_lock_ts = int(temp_done_set[0][-1])
                price_list_src.append(float(temp_done_set[0][2]))
                price_x_src.append(i)
                delt = float(float(done_set_select_comp[i][2])*para_delt_fator) - float(temp_done_set[0][2])
                std = np.array(delt_list).std()
                mean = np.array(delt_list).mean()
                avg_list.append(mean)
                up_list.append(mean+std*para_interval)
                low_list.append(mean-std*para_interval)
                if abs(delt - mean) > abs(std)*para_interval and len(delt_list) >= 200:
                    v_line.append(i)
                    ts_list.append(done_set_select_comp[i][-1])
                delt_list.append(delt)


    print(ts_list)

    fig = plt.figure(figsize=(20, 12))
    ax = fig.add_subplot(311)
    plt.plot(price_x_src,price_list_src,color='blue')
    plt.axvline(v_line[0], color='green')
    # for a in range(len(v_line)):
    #     plt.axvline(v_line[a], color='green')
    ax2 = fig.add_subplot(312)
    plt.plot(price_x_comp,price_list_comp,color='red')
    plt.axvline(v_line[0], color='green')

    # for a in range(len(v_line)):
    #     plt.axvline(v_line[a], color='green')
    ax3 = fig.add_subplot(313)
    plt.plot(price_x_src,delt_list,color='red')
    plt.plot(price_x_src,avg_list,color='blue')
    #plt.plot(price_x_src,np.array(avg_list)*1.3,color='black')
    plt.plot(price_x_src,up_list,color='black')
    plt.plot(price_x_src,low_list,color='black')
    plt.axvline(v_line[0], color='green')
    # for b in range(len(v_line)):
    #     plt.axvline(v_line[b], color='green')

    plt.show()






