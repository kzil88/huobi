# -*- coding:utf8 -*-
import numpy as np
import pymysql
import json
import time
import talib as ta
import My_CAP
import Operator as op
import matplotlib.pyplot as plt
from pylab import *

#自定义均价 每日（开盘价+收盘价）/2,然后取n日平均值
def cma(open,close):
    temp = (open + close)/2
    resu = 0.00
    for i in range(len(temp)):
        resu = resu + float(temp[i])
    resu_fin = resu/len(temp)
    return  resu_fin

def singal(pre_date_seq,para_min):
    # 建立数据库连接,清空相关表
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    sql = "select * from btc_%smin a where a.state_dt >= '%s' and a.state_dt <= '%s'"%(para_min,pre_date_seq[0],pre_date_seq[-1])
    cursor.execute(sql)
    done_set = cursor.fetchall()
    close = np.array([float(x[2]) for x in done_set])

    # 计算
    good_factor = 0.007
    bad_factor = 0.03
    list_open = np.array([x[1] for x in done_set])
    list_high = np.array([x[3] for x in done_set])
    list_low = np.array([x[4] for x in done_set])
    list_close = np.array([x[2] for x in done_set])

    avg = cma(list_open, list_close)
    good_buy = avg * (1.00 - good_factor)
    good_sell = avg * (1.00 + good_factor)
    bad_sell = avg * (1.00 - bad_factor)

    cnt_bad_sell = cnt_good_buy = cnt_good_sell = cnt_risk = 0
    for i in range(len(list_close)):
        if list_close[i] <= bad_sell:
            cnt_bad_sell += 1
        if bad_sell < list_close[i] <= good_buy:
            cnt_good_buy += 1
        if list_close[i] >= good_sell:
            cnt_good_sell += 1
        if list_low[i] <= list_close[-1]:
            cnt_risk += 1

    # 振幅af = (high-low)/len   频率 freq = 从good_selld到good_buy（或反之）的所需步长之和除以len
    af = ((list_high - list_low).sum()) / len(list_high)
    start_flag = 0
    list_index = 0
    for k in range(len(list_high)):
        if list_high[len(list_high) - k - 1] >= good_sell:
            start_flag = 1
            list_index = len(list_high) - k - 1
        elif bad_sell < list_low[len(list_high) - k - 1] <= good_buy:
            start_flag = 2
            list_index = len(list_high) - k - 1
    freq_list = []

    for l in range(list_index, len(list_high)):
        if start_flag > 0:
            if (divmod(start_flag, 2)[1] == 1) and (bad_sell < list_low[l] <= good_buy):
                freq_list.append(l)
                start_flag = start_flag + 1
            elif (divmod(start_flag, 2)[1] == 0) and (list_high[l] >= good_sell):
                freq_list.append(l)
                start_flag = start_flag + 1
        else:
            freq = 0
    freq_step = []
    if len(freq_list) == 1:
        freq = (len(list_high) - freq_list[0] - 1) / 60;
    elif len(freq_list) > 1:
        for m in range(1, len(freq_list)):
            freq_step.append(freq_list[len(freq_list) - m] - freq_list[len(freq_list) - 1 - m])
        freq = np.array(freq_step).sum() / (len(freq_step) * 60)

    if list_close[-1] < bad_sell:
        return -1
    elif bad_sell < list_close[-1] <= good_buy:
        return 1
    elif list_close[-1] > good_sell:
        return -1

if __name__ == '__main__':

    para_min = '5'

    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()


    sql_dele = "delete from btc_my_cap where seq != 1"
    cursor.execute(sql_dele)
    db.commit()

    sql_dt_seq = "select distinct state_dt from btc_%smin order by state_dt asc"%(para_min)
    cursor.execute(sql_dt_seq)
    done_set_dt = cursor.fetchall()
    date_seq = [x[0] for x in done_set_dt]
    for i in range(200,len(date_seq)):
        print(date_seq[i])
        ans = singal(date_seq[:i],para_min)
        cap = My_CAP.My_CAP()
        if ans == 1:
            op.buy('BTC',date_seq[i],cap.usdt_acct,para_min)
        elif ans == -1:
            op.sell('BTC',date_seq[i],-1,para_min)
    db.commit()
    print('ALL Finished!!')



    sql_show_btc = "select * from btc_%smin order by state_dt asc"%(para_min)
    cursor.execute(sql_show_btc)
    done_set_show_btc = cursor.fetchall()
    btc_x = [int(x[-1]) for x in done_set_show_btc]
    btc_y = [x[2]/done_set_show_btc[0][2] for x in done_set_show_btc]
    dict_anti_x = {}
    dict_x = {}
    for a in range(len(btc_x)):
        dict_anti_x[btc_x[a]] = done_set_show_btc[a][0][6:]
        dict_x[done_set_show_btc[a][0]] = btc_x[a]


    sql_show_profit = "select * from btc_my_cap order by state_dt asc"
    cursor.execute(sql_show_profit)
    done_set_show_profit = cursor.fetchall()
    profit_x = [dict_x[x[-2]] for x in done_set_show_profit if x[-1] != 1]
    profit_y = [x[0]/done_set_show_profit[0][0] for x in done_set_show_profit if x[-1] != 1]


    # 绘制收益率曲线（含大盘基准收益曲线）
    def c_fnx(val, poz):
        if val in dict_anti_x.keys():
            return dict_anti_x[val]
        else:
            return ''


    fig = plt.figure(figsize=(20, 12))
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_formatter(FuncFormatter(c_fnx))

    plt.plot(btc_x, btc_y, color='blue')
    plt.plot(profit_x, profit_y, color='red')

    # plt.plot(total_mon_x,total_mon_y)
    #plt.plot(index_x, index_y, color='red')
    # xticks(c_xticks)

    # 绘制柱图月统计
    #bx = fig.add_subplot(212)

    plt.show()