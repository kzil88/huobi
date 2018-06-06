#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

import HuobiServices as hb
import pymysql
import datetime
import time

def get_data(stock_code):
    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    # 现货API 1min
    response = hb.get_kline(str(stock_code)+'usdt', '1min', 1000)
    resu = response['data']
    for i in range(1, len(resu)):
        state_dt = time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(resu[i]['id'])))
        sql = "INSERT INTO %s_1min(state_dt,open_usd,close_usd,high_usd,low_usd,amount,vol,timestamp) VALUES ('%s','%.2f','%.2f','%.2f','%.2f','%.6f','%.4f','%s')" % (stock_code,state_dt, float(resu[i]['open']), float(resu[i]['close']), float(resu[i]['high']), float(resu[i]['low']),
        float(resu[i]['vol']), float(resu[i]['amount']), str(resu[i]['id']))
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as exp:
            print(exp)
            continue
        print('Coin : ' +str(stock_code) + '   Type : 1min   State_Dt : ' + str(state_dt) + '   Open_Usd : ' + str(resu[i]['open']) + '   Close_Usd : ' + str(
            resu[i]['close']) + '   High_Usd : ' + str(resu[i]['high']) + '   Low_Usd : ' + str(
            resu[i]['low']) + '   Amount : ' + str(resu[i]['vol']) + '   Vol : ' + str(
            resu[i]['amount']) + '   TimeStamp : ' + str(resu[i]['id']))

    # 现货API 5min
    response2 = hb.get_kline(str(stock_code)+'usdt', '5min', 1000)
    resu2 = response2['data']
    for j in range(1, len(resu2)):
        state_dt2 = time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(resu2[j]['id'])))
        sql2 = "INSERT INTO %s_5min(state_dt,open_usd,close_usd,high_usd,low_usd,amount,vol,timestamp) VALUES ('%s','%.2f','%.2f','%.2f','%.2f','%.6f','%.4f','%s')" % (stock_code,
            state_dt2, float(resu2[j]['open']), float(resu2[j]['close']), float(resu2[j]['high']),
            float(resu2[j]['low']),
            float(resu2[j]['vol']), float(resu2[j]['amount']), str(resu2[j]['id']))
        try:
            cursor.execute(sql2)
            db.commit()
        except Exception as exp:
            print(exp)
            continue
        print('Coin : ' +str(stock_code) + '   Type : 5min   State_Dt : '+ str(state_dt2) + '   Open_Usd : ' + str(resu2[j]['open']) + '   Close_Usd : ' + str(
            resu2[j]['close']) + '   High_Usd : ' + str(resu2[j]['high']) + '   Low_Usd : ' + str(
            resu2[j]['low']) + '   Amount : ' + str(resu2[j]['vol']) + '   Vol : ' + str(
            resu2[j]['amount']) + '   TimeStamp : ' + str(resu2[j]['id']))

    # 现货API 15min
    response3 = hb.get_kline(str(stock_code)+'usdt', '15min', 1000)
    resu3 = response3['data']
    for k in range(1, len(resu3)):
        state_dt3 = time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(resu3[k]['id'])))
        sql3 = "INSERT INTO %s_15min(state_dt,open_usd,close_usd,high_usd,low_usd,amount,vol,timestamp) VALUES ('%s','%.2f','%.2f','%.2f','%.2f','%.6f','%.4f','%s')" % (stock_code,
            state_dt3, float(resu3[k]['open']), float(resu3[k]['close']), float(resu3[k]['high']),
            float(resu3[k]['low']),
            float(resu3[k]['vol']), float(resu3[k]['amount']), str(resu3[k]['id']))
        try:
            cursor.execute(sql3)
            db.commit()
        except Exception as exp:
            print(exp)
            continue
        print('Coin : ' +str(stock_code) + '   Type : 15min   State_Dt : ' + str(state_dt3) + '   Open_Usd : ' + str(resu3[k]['open']) + '   Close_Usd : ' + str(
            resu3[k]['close']) + '   High_Usd : ' + str(resu3[k]['high']) + '   Low_Usd : ' + str(
            resu3[k]['low']) + '   Amount : ' + str(resu3[k]['vol']) + '   Vol : ' + str(
            resu3[k]['amount']) + '   TimeStamp : ' + str(resu3[k]['id']))

    # 现货API 30min
    response4 = hb.get_kline(str(stock_code)+'usdt', '30min', 1000)
    resu4 = response4['data']
    for l in range(1, len(resu4)):
        state_dt4 = time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(resu4[l]['id'])))
        sql4 = "INSERT INTO %s_30min(state_dt,open_usd,close_usd,high_usd,low_usd,amount,vol,timestamp) VALUES ('%s','%.2f','%.2f','%.2f','%.2f','%.6f','%.4f','%s')" % (stock_code,
            state_dt4, float(resu4[l]['open']), float(resu4[l]['close']), float(resu4[l]['high']),
            float(resu4[l]['low']),
            float(resu4[l]['vol']), float(resu4[l]['amount']), str(resu4[l]['id']))
        try:
            cursor.execute(sql4)
            db.commit()
        except Exception as exp:
            print(exp)
            continue
        print('Coin : ' +str(stock_code) + '   Type : 30min   State_Dt : ' + str(state_dt4) + '   Open_Usd : ' + str(resu4[l]['open']) + '   Close_Usd : ' + str(
            resu4[l]['close']) + '   High_Usd : ' + str(resu4[l]['high']) + '   Low_Usd : ' + str(
            resu4[l]['low']) + '   Amount : ' + str(resu4[l]['vol']) + '   Vol : ' + str(
            resu4[l]['amount']) + '   TimeStamp : ' + str(resu4[l]['id']))

    # 现货API 60min
    response5 = hb.get_kline(str(stock_code)+'usdt', '60min', 1000)
    resu5 = response5['data']
    for m in range(1, len(resu5)):
        state_dt5 = time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(resu5[m]['id'])))
        sql5 = "INSERT INTO %s_60min(state_dt,open_usd,close_usd,high_usd,low_usd,amount,vol,timestamp) VALUES ('%s','%.2f','%.2f','%.2f','%.2f','%.6f','%.4f','%s')" % (stock_code,
            state_dt5, float(resu5[m]['open']), float(resu5[m]['close']), float(resu5[m]['high']),
            float(resu5[m]['low']),
            float(resu5[m]['vol']), float(resu5[m]['amount']), str(resu5[m]['id']))
        try:
            cursor.execute(sql5)
            db.commit()
        except Exception as exp:
            #print(exp)
            continue
        print('Coin : ' +str(stock_code) + '   Type : 60min   State_Dt : ' + str(state_dt5) + '   Open_Usd : ' + str(resu5[m]['open']) + '   Close_Usd : ' + str(
            resu5[m]['close']) + '   High_Usd : ' + str(resu5[m]['high']) + '   Low_Usd : ' + str(
            resu5[m]['low']) + '   Amount : ' + str(resu5[m]['vol']) + '   Vol : ' + str(
            resu5[m]['amount']) + '   TimeStamp : ' + str(resu5[m]['id']))

    db.close()

    #print("ALL Finished!!")

if __name__ == '__main__':

    # 建立要更新的币种列表,全部以usdt为标的
    coin_list = ['btc','eos','eth']
    #coin_list = ['eth']

    for i in range(len(coin_list)):
        print('=============>>>>>>>  '+str(coin_list[i]) + '  <<<<<<<<==============')
        get_data(coin_list[i])

    print("ALL Finished!!")
