#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

import HuobiServices as hb
import pymysql
import datetime
import time

if __name__ == '__main__':



    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    #现货API
    response = hb.get_kline('btcusdt','1day',1000)
    resu = response['data']
    print(len(resu))

    for i in range(1,len(resu)):
        state_dt = time.strftime("%Y-%m-%d", time.localtime(int(resu[i]['id'])))
        sql = "INSERT INTO btc_day(state_dt,open_usd,close_usd,high_usd,low_usd,amount,vol,timestamp) VALUES ('%s','%.2f','%.2f','%.2f','%.2f','%.6f','%.4f','%s')"%(state_dt,float(resu[i]['open']),float(resu[i]['close']),float(resu[i]['high']),float(resu[i]['low']),float(resu[i]['vol']),float(resu[i]['amount']),str(resu[i]['id']))
        cursor.execute(sql)
        db.commit()
        print("State_Dt : " + str(state_dt) + '   Open_Usd : ' + str(resu[i]['open']) + '   Close_Usd : ' + str(resu[i]['close']) + '   High_Usd : ' + str(resu[i]['high']) + '   Low_Usd : ' + str(resu[i]['low']) + '   Amount : ' + str(resu[i]['vol']) + '   Vol : ' + str(resu[i]['amount']) + '   TimeStamp : ' + str(resu[i]['id']))
    db.close()
    print("ALL Finished!!")
