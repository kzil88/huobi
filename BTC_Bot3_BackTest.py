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
import DC
from sklearn import svm

def singal(pre_date_seq,para_min):

    threshold = 1.0001
    # 建立数据库连接,清空相关表
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    dc = DC.data_collect2(pre_date_seq[0], date_seq[-1], para_min, threshold)
    train = dc.data_train
    target = dc.data_target
    test_case = [dc.test_case]
    if dc.cnt_pos == 0:
        print('No Positive Samples!')
        return 0
    w = (len(target) / dc.cnt_pos)
    if len(target) / dc.cnt_pos == 1:
        print('No Negtive Samples!')
        return 0
    # model = svm.SVC(class_weight={1: w})
    model = svm.SVC()
    model.fit(train, target)
    # print(model.score(train,target))
    ans2 = model.predict(test_case)
    return int(ans2[0])

def warning_macd(pre_date_seq,para_warning):
    # 建立数据库连接,清空相关表
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    sql = "select * from btc_%smin a where a.state_dt <= '%s' order by a.state_dt desc limit 200 "%(para_warning,pre_date_seq[-1])
    cursor.execute(sql)
    done_set = cursor.fetchall()
    close = np.array([float(x[2]) for x in done_set][::-1])

    macd_temp = ta.MACD(close,12,26,9)
    up_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).max()*2.5
    low_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).min()*3

    #print(up_limit)
    #print(low_limit)
    macd = macd_temp[2][-1]

    warning_flag = 0
    # flag
    if (low_limit < ((macd_temp[2][-1] + macd_temp[2][-2] + macd_temp[2][-3]) * 2) < up_limit) and (macd_temp[2][-1] < macd_temp[2][-2] < macd_temp[2][-3]):
        warning_flag = -1
    return warning_flag

def warning_ma(pre_date_seq,para_warning):
    # 建立数据库连接,清空相关表
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    if para_warning == 'day':
        sql = "select * from btc_day a where a.state_dt <= '%s' order by a.state_dt desc limit 200 "%(pre_date_seq[-1])
    else:
        sql = "select * from btc_%smin a where a.state_dt <= '%s' order by a.state_dt desc limit 200 "%(para_warning,pre_date_seq[-1])
    cursor.execute(sql)
    done_set = cursor.fetchall()
    close = np.array([float(x[2]) for x in done_set][::-1])

    ma20 = ta.MA(close,20)
    ma60 = ta.MA(close,60)

    warning_flag = 0
    # flag
    if close[-1] < ma20[-1] and close[-1] < ma60[-1]:
        warning_flag = -1
    return warning_flag

if __name__ == '__main__':

    para_min = '15'
    para_warning = '5'

    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    sql_dele = "delete from btc_my_cap where seq != 1"
    cursor.execute(sql_dele)
    db.commit()

    sql_dt_seq = "select distinct state_dt from btc_%smin order by state_dt asc"%(para_min)
    #sql_dt_seq = "select distinct state_dt from btc_%smin a where a.timestamp >= 1524137700 order by state_dt asc"%(para_min)
    #30  1522740600   60    1522382400

    cursor.execute(sql_dt_seq)
    done_set_dt = cursor.fetchall()
    date_seq = [x[0] for x in done_set_dt]
    for i in range(1000,len(date_seq)):
        ans = singal(date_seq[i-1000:i],para_min)
        #ans2 = warning_macd(date_seq[i-200:i],para_warning)
        ans2 = 0
        print('State_Dt : ' + str(date_seq[i]) + '   Singal : '+str(ans) + '   Warning : ' + str(ans2))
        cap = My_CAP.My_CAP()
        if ans == 1 and ans2 == 0:
            op.buy('BTC',date_seq[i],cap.usdt_acct,para_min)
        elif ans == -1:
            op.sell('BTC',date_seq[i],-1,para_min)
    db.commit()
    print('ALL Finished!!')



    sql_show_btc = "select * from btc_%smin order by state_dt asc"%(para_min)
    #sql_show_btc = "select * from btc_%smin a where a.timestamp >= 1524137700 order by state_dt asc"%(para_min)

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
    db.close()