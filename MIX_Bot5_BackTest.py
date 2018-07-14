# -*- coding:utf8 -*-
import talib as ta
import My_CAP_MIX
import Operator_MIX2 as op
from pylab import *
import numpy as np
import datetime
import pymysql
import copy
import CoordinateDescent as cd

def singal(coin,pre_date_seq,para_min,para_up,para_low):
    # 建立数据库连接,清空相关表
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    sql = "select * from %s_%smin a where a.state_dt >= '%s' and a.state_dt <= '%s' order by a.state_dt asc "%(coin,para_min,pre_date_seq[0],pre_date_seq[-1])
    cursor.execute(sql)
    done_set = cursor.fetchall()
    if len(done_set) == 0:
        return 0
    close = np.array([float(x[2]) for x in done_set])

    macd_temp = ta.MACD(close,12,26,9)
    if len([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]) == 0 or len([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]) == 0:
        return 0
    up_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).max()*para_up
    low_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).min()*para_low

    up_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).mean()
    low_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).mean()
    macd = macd_temp[2][-1]

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
    db.close()
    return action_flag

def singal2(stock_code,pre_date_seq,para_min,para_up,para_low):
    # 建立数据库连接,清空相关表
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    sql = "select * from %s_%smin a where a.state_dt >= '%s' and a.state_dt <= '%s' order by a.state_dt asc "%(stock_code,para_min,pre_date_seq[0],pre_date_seq[-1])
    cursor.execute(sql)
    done_set = cursor.fetchall()
    close = np.array([float(x[2]) for x in done_set])
    vol = np.array([float(x[5]) for x in done_set])
    amount = np.array([float(x[6]) for x in done_set])

    std = close.std()
    up_limit = para_up * std
    low_limit = para_low * std
    macd_temp = ta.MACD(close, 12, 26, 9)
    action_flag1 = 0
    if (macd_temp[2][-2] < macd_temp[2][-1]) and (macd_temp[2][-2] < macd_temp[2][-3]) and (
            macd_temp[2][-1] < 0) and (macd_temp[2][-3] < 0) and (
            macd_temp[2][-3] + macd_temp[2][-2] + macd_temp[2][-1]) < -0.079:
        action_flag1 = 1
    elif (macd_temp[2][-2] > macd_temp[2][-1]) and (macd_temp[2][-2] > macd_temp[2][-3]) and (
            macd_temp[2][-1] > 0) and (macd_temp[2][-3] > 0) and (
            macd_temp[2][-3] + macd_temp[2][-2] + macd_temp[2][-1]) > 0.079:
        action_flag1 = -1

    price_avg_long = float(amount.sum()/vol.sum())
    price_avg_short = float(amount[-1]/vol[-1])

    action_flag2 = 0
    delt = price_avg_short - price_avg_long
    if price_avg_short - price_avg_long > para_up * std:
        action_flag2 = -1
    elif price_avg_short - price_avg_long < para_low * std:
        action_flag2 = 1

    action_flag = 0
    if action_flag1 == action_flag2 == 1:
        action_flag = 1
    elif action_flag1 == action_flag2 == -1:
        action_flag = -1
    db.close()
    return action_flag

def warning_ma(coin,pre_date_seq,para_warning):
    # 建立数据库连接,清空相关表
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    if para_warning == 'day':
        sql = "select * from %s_day a where a.state_dt <= '%s' order by a.state_dt desc limit 200 "%(coin,pre_date_seq[-1])
    else:
        sql = "select * from %s_%smin a where a.state_dt <= '%s' order by a.state_dt desc limit 200 "%(coin,para_warning,pre_date_seq[-1])
    cursor.execute(sql)
    done_set = cursor.fetchall()
    close = np.array([float(x[2]) for x in done_set][::-1])
    if len(close) == 0:
        return 0

    ma20 = ta.MA(close,20)
    ma60 = ta.MA(close,60)

    warning_flag = 0
    # flag
    if close[-1] > ma20[-1] * 1.03:
        warning_flag = -1

    db.close()
    return warning_flag


# 返回的resu中 特征值按由小到大排列，对应的是其特征向量
def get_portfolio(coin_list,state_dt,para_min):
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    para_len = 200

    list_return = []
    for i in range(len(coin_list)):
        sql = "select * from %s_%smin a where a.state_dt <= '%s' order by a.state_dt desc limit %i"%(coin_list[i],para_min,state_dt,para_len)
        cursor.execute(sql)
        done_set = cursor.fetchall()
        db.commit()
        if len(done_set) != para_len:
            return []
        ri = []
        ri = np.array([float(x[2]) for x in done_set][::-1])
        ri = ri/ri[0]
        ri = ri - 1.0
        ri = ri * 100
        del done_set
        list_return.append(ri)
    #list_return.append(np.array([float(0.00)] * 200))


    # 求协方差矩阵
    cov = np.cov(np.array(list_return))
    # 求特征值和其对应的特征向量
    ans = np.linalg.eig(cov)
    # 排序，特征向量中负数置0，非负数归一
    ans_index = copy.copy(ans[0])
    ans_index.sort()
    resu = []
    for k in range(len(ans_index)):
        con_temp = []
        con_temp.append(ans_index[k])
        content_temp1 = ans[1][np.argwhere(ans[0] == ans_index[k])[0][0]]
        content_temp2 = []
        #content_sum = np.array([x for x in content_temp1 if x >= 0.00]).sum()
        content_sum = np.array([abs(x) for x in content_temp1]).sum()
        for m in range(len(content_temp1)):
            content_temp2.append(abs(content_temp1[m]) / content_sum)
            # if content_temp1[m] >= 0 and content_sum > 0:
            #     content_temp2.append(content_temp1[m]/content_sum)
            # else:
            #     content_temp2.append(0.00)

        con_temp.append(content_temp2)
        resu.append(con_temp)
    return resu

def get_sell_quant(coin):
    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    sql_quant = "select a.seq,%s_acct,%s_avg_price from mix_my_cap a where seq != 1 and a.deal_action = 'buy' and bz is null order by a.seq asc"%(coin,coin)
    cursor.execute(sql_quant)
    db.commit()
    done_set_quant = cursor.fetchall()
    coin_quant = 0.00
    coin_avg_price = 0.00
    seq_list = []
    if len(done_set_quant) > 0:
        for i in range(len(done_set_quant)):
            seq_list.append(done_set_quant[i][0])
        coin_quant = float(done_set_quant[-1][1])*0.2
        coin_avg_price = float(done_set_quant[-1][2])
    return seq_list,coin_quant,coin_avg_price


if __name__ == '__main__':

    # coin_list = ['btc','eos','eth']
    # para_list = [(2.5,3),(3.5,2),(3,2.5)]
    coin_list = ['btc','eos']
    #para_list = [(2.5,3),(3.5,2)]
    # coin_list = ['btc', 'eth']
    para_list = [[1,-1],[1,-1]]
    para_min = '15'

    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    # 清空账单表
    sql_dele = "delete from mix_my_cap where seq != 1"
    cursor.execute(sql_dele)
    db.commit()
    # 建回测时间序列，以第一个coin为准
    # '2018-04-28-00-45'
    sql_dt_seq = "select distinct state_dt from %s_%smin where state_dt >= '2018-05-02-04-45' order by state_dt desc limit 2000"%(coin_list[0],para_min)
    cursor.execute(sql_dt_seq)
    done_set_dt = cursor.fetchall()
    date_seq = [x[0] for x in done_set_dt][::-1]

    #can_buy = [1, 1]
    #can_buy_release = [0,0]
    #bad_sell_lock = 0
    for i in range(200,len(date_seq)):
        # if bad_sell_lock > 0:
        #     bad_sell_lock += 1
        #     if divmod(bad_sell_lock,288)[1] == 0:
        #         bad_sell_lock = 0
        #     continue

        for j in range(len(coin_list)):
        #     if can_buy[j] == 0:
        #         can_buy_release[j] += 1
        #         if divmod(can_buy_release[j],12)[1] == 0:
        #             can_buy_release[j] = 0
        #             can_buy[j] = 1

            # 仓位管理
            #pos_temp = get_portfolio(coin_list,date_seq[i-1],para_min)
            pos = 1
            # if len(pos_temp) != 0:
            #     # 市场方向 或 最大收益方向
            #     pos = pos_temp[1][1][j]

            # if divmod(i-200, 200)[1] == 0 or i == 200:
            #     #sql_truncate = "truncate table coordinate_descent"
            #     #cursor.execute(sql_truncate)
            #     #db.commit()
            #     para_resu = []
            #     while len(para_resu) == 0:
            #
            #         try :
            #             para_resu = cd.CoordinateDescentMain(para_min,coin_list[j],1000,date_seq[i])
            #         except Exception as exp:
            #             continue

            ans = singal2(coin_list[j],date_seq[i-200:i],para_min,para_list[j][0],para_list[j][1])
            # ans2 是预警信号，留待后用
            #ans2 = warning_ma(coin_list[j],date_seq[i-200:i],para_min)
            ans2 = 0
            print('State_Dt : ' + str(date_seq[i]) +'   Coin : ' + str(coin_list[j])+ '   Singal : '+str(ans) + '   Warning : ' + str(ans2) + '   Pos : ' + str(pos))
            cap = My_CAP_MIX.My_CAP_MIX()
            buy_money = cap.usdt_acct*pos*0.2

            #if ans == 1 and ans2 == 0 and can_buy[j] == 1:
            if ans == 1 and ans2 == 0 :
                lock = op.buy(coin_list[j],date_seq[i-1],buy_money,para_min)
                # if lock == 1:
                #     can_buy[j] = 0
            elif ans == -1:
                seq_list,coin_quant,coin_avg_price = get_sell_quant(coin_list[j])
                op.sell(coin_list[j],date_seq[i-1],-1,coin_quant,para_min)
                for a in range(len(seq_list)):
                    sql_sell_update = "update mix_my_cap w set w.bz = '1' where w.bz is null and w.seq = %i" % (seq_list[a])
                    cursor.execute(sql_sell_update)
                    db.commit()

            lock = op.sell(coin_list[j],date_seq[i-1],0,0,para_min)
            # if lock == 77:
            #     bad_sell_lock = 0



    db.commit()
    print('ALL Finished!!')

    #绘制收益曲线，以btc为大盘



    sql_show_btc = "select * from btc_%smin a where a.state_dt >= (select min(b.state_dt) from mix_my_cap b where state_dt is not null) order by state_dt asc"%(para_min)

    cursor.execute(sql_show_btc)
    done_set_show_btc = cursor.fetchall()
    btc_x = [int(x[-1]) for x in done_set_show_btc]
    btc_y = [x[2]/done_set_show_btc[0][2] for x in done_set_show_btc]
    dict_anti_x = {}
    dict_x = {}
    for a in range(len(btc_x)):
        dict_anti_x[btc_x[a]] = done_set_show_btc[a][0][6:]
        dict_x[done_set_show_btc[a][0]] = btc_x[a]


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



    # 绘制其他币种的收益曲线
    for k in range(len(coin_list)):
        if coin_list[k] == 'btc':
            continue
        sql_coin_graph = "select * from %s_%smin a where a.state_dt >= (select min(b.state_dt) from mix_my_cap b where state_dt is not null) order by state_dt asc"%(coin_list[k],para_min)
        cursor.execute(sql_coin_graph)
        done_graph = cursor.fetchall()
        coin_x = [int(x[-1]) for x in done_graph]
        coin_y = [x[2] / done_graph[0][2] for x in done_graph]
        plt.plot(coin_x, coin_y, color='green')

    sql_show_profit = "select * from mix_my_cap order by state_dt asc"
    cursor.execute(sql_show_profit)
    done_set_show_profit = cursor.fetchall()
    profit_x = [dict_x[x[-2]] for x in done_set_show_profit if x[-1] != 1]
    #profit_y = [x[0]/done_set_show_profit[0][0] for x in done_set_show_profit if x[-1] != 1]
    profit_y = [x[0] / done_set_show_profit[0][0] for x in done_set_show_profit if x[-1] != 1]

    plt.plot(profit_x, profit_y, color='red')

    # plt.plot(total_mon_x,total_mon_y)
    #plt.plot(index_x, index_y, color='red')
    # xticks(c_xticks)

    # 绘制柱图月统计
    #bx = fig.add_subplot(212)
    db.close()
    plt.show()
