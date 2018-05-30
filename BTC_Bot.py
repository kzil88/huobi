# -*- coding:utf8 -*-
import numpy as np
import pymysql
import json
import time
import talib as ta
import datetime
import HuobiServices as hb
import math

def Signal(para_min,para_up,para_low):
    resu_temp = hb.get_kline('btcusdt', para_min, 201)
    cur_kline_ts = resu_temp['data'][0]['id']

    date_seq = [time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(x['id']))) for x in resu_temp['data']][::-1]
    close_temp = [x['close'] for x in resu_temp['data']][1:]
    close = np.array(close_temp[::-1])

    macd_temp = ta.MACD(close, 12, 26, 9)
    up_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).max() * para_up
    low_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).min() * para_low

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
    return action_flag,cur_kline_ts

def Acct_Info(curr_type):
    resu = hb.get_balance(xxxxxxxx)
    if resu['status'] == 'error':
        print('Acct_Info Errrrrr')
        return -1
    else:
        resu_data = resu['data']['list']
        for i in range(len(resu_data)):
            if resu_data[i]['currency'] == curr_type and resu_data[i]['type'] == 'trade':
                return float(resu_data[i]['balance'])
        return 0



if __name__ == '__main__':

    para_min = '15min'
    para_up = 2.5
    para_low = 3

    pre_kline_ts = 0
    singal_time_cnt = 3
    while True:
        if singal_time_cnt > 4000:
            singal_time_cnt = 1
        else:
            singal_time_cnt += 1
        # 当前时间与时间戳
        state_dt = (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = int(time.mktime(time.strptime(state_dt, "%Y-%m-%d %H:%M:%S")))

        # id 3344078
        try:
            # 获取最新行情，跌破3个点则止损，止损行情每17秒循环一次
            latest_price_temp = hb.get_ticker('btcusdt')
            latest_price = float(latest_price_temp['tick']['close'])
            # 获取上一次市价卖单的成交价(即成本价)
            last_order_temp = hb.orders_list(symbol='btcusdt', states='filled', direct='next', types='buy_market')
            last_order_dict = last_order_temp['data'][0]
            last_order_id = last_order_dict['id']
            last_price = float(last_order_dict['field-cash-amount']) / float(last_order_dict['field-amount'])
            last_profit_rate = float(latest_price/last_price)
            print('Now State_Dt : ' + str(state_dt) + '   Cur_Close Price : ' + str(latest_price) + '   Pre_Deal Price : '+ str(last_price)+'   Profit_Rate : '+ str(round(last_profit_rate*100-100,2)) + ' %')
            if last_profit_rate < 0.95:
                cap_btc_ori = Acct_Info('btc')
                cap_btc = math.floor(cap_btc_ori * 998)/1000
                if cap_btc >= 0.001:
                    resp = hb.send_order(amount=cap_btc,source='api',symbol='btcusdt',_type='sell-market')
                    print('BAD SELL !!   State_Dt : ' + str(state_dt) + '   Response : ' + str(resp))
                    break


            # 获取信号，返回值包含最新数据的时间戳，信号行情每 4*17=68 秒循环一次
            if divmod(singal_time_cnt,4)[1] == 0:
                resu_single,cur_kline_ts = Signal(para_min,para_up,para_low)
                print('Signal : ' + str(resu_single) + '   at   ' + str(state_dt))
                time_delt = timestamp - cur_kline_ts
                # 时间间隔大于15min 即900时间戳的话，说明最新的15分钟数据还没更新，每隔 17 秒取数一次直到更新。
                if time_delt >= 900:
                    singal_time_cnt = 3
                    continue
                else:
                    # 信号为 1 且资金余额可买大于最小单位0.001个币时，买入；为 -1 且 市价大于买入均价时，或 市价低于 买入均价3个点时，卖出
                    # 先判断卖出
                    if resu_single < 0 and latest_price > last_price:
                        # 获取btc资产
                        cap_btc_ori = Acct_Info('btc')
                        cap_btc = math.floor(cap_btc_ori * 998) / 1000
                        if cap_btc >= 0.001:
                            resp = hb.send_order(amount=cap_btc, source='api',symbol='btcusdt', _type='sell-market')
                            print('PREDICT SELL !!   State_Dt : ' + str(state_dt) + '   Response : ' + str(resp))

                    # 后判断买入
                    elif resu_single > 0 :
                        # 获取usdt资产
                        cap_usdt_ori = Acct_Info('usdt')
                        cap_usdt = math.floor(cap_usdt_ori * 998) / 1000
                        if cap_usdt/latest_price > 0.001:
                            resp = hb.send_order(amount=cap_usdt, source='api',symbol='btcusdt',_type='buy-market')
                            print('Signal Buy   State_Dt : ' + str(state_dt) + '   Response : ' + str(resp))
            time.sleep(17)
        except Exception as exp:
            singal_time_cnt = 3
            print(str(state_dt) + '   Exception : ' + str(exp))
            time.sleep(34)
            continue
