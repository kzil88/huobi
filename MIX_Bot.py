# -*- coding:utf8 -*-
import numpy as np
import time
import talib as ta
import datetime
import HuobiServices as hb
import math
import copy

def Signal(coin_symbol,para_min,para_up,para_low):
    resu_temp = hb.get_kline(coin_symbol, para_min, 201)
    cur_kline_ts = resu_temp['data'][0]['id']

    #date_seq = [time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(x['id']))) for x in resu_temp['data']][::-1]
    close_temp = [x['close'] for x in resu_temp['data']][1:]
    close = np.array(close_temp[::-1])

    macd_temp = ta.MACD(close, 12, 26, 9)
    up_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).max() * para_up
    low_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).min() * para_low

    up_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).mean()
    low_mean = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).mean()
    #macd = macd_temp[2][-1]
    #print(macd*2)

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
    return action_flag,cur_kline_ts,up_limit,low_limit

def Signal2(coin_symbol,para_min,para_up,para_low,show_len):
    resu_temp = hb.get_kline(coin_symbol, para_min,show_len)

    up_limit = para_up
    low_limit = para_low
    cur_kline_ts = resu_temp['data'][0]['id']
    date_seq = [time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(x['id']))) for x in resu_temp['data']][::-1]

    amount_temp = [x['vol'] for x in resu_temp['data']]
    amount = np.array(amount_temp[::-1])

    vol_temp = [x['amount'] for x in resu_temp['data']]
    vol = np.array(vol_temp[::-1])

    # close_temp = [x['close'] for x in resu_temp['data']][1:]
    # close = np.array(close_temp[::-1])

    price_avg_long = float(amount.sum() / vol.sum())
    price_avg_short = float(amount[-1] / vol[-1])

    action_flag = 0
    delt = price_avg_short - price_avg_long
    if price_avg_short - price_avg_long > para_up:
        action_flag = -1
    elif price_avg_short - price_avg_long < para_low:
        action_flag = 1

    return action_flag,cur_kline_ts,up_limit,low_limit,delt


# 返回的resu中 特征值按由小到大排列，对应的是其特征向量
def get_portfolio(coin_list,para_min):

    #获取 k 线数据，检查时间戳，不一致的话返回[]
    init_ts = ''
    list_return = []
    for i in range(len(coin_list)):
        resu_temp = hb.get_kline(str(coin_list[i]) + 'usdt', para_min, 201)
        cur_kline_ts = resu_temp['data'][0]['id']
        if i == 0:
            init_ts = cur_kline_ts
        elif init_ts != cur_kline_ts:
            return []

        #date_seq = [time.strftime("%Y-%m-%d-%H-%M", time.localtime(int(x['id']))) for x in resu_temp['data']][::-1]
        close_temp = [x['close'] for x in resu_temp['data']][1:]
        close = np.array(close_temp[::-1])

        if len(close) != 200:
            return []

        ri = []
        ri = close/close[0]
        ri = ri - 1.0
        ri = ri * 100
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


def Acct_Info(coin):
    resu = hb.get_balance(378)
    print(resu)
    if resu['status'] == 'error':
        print('Acct_Info Errrrrr')
        return -1
    else:
        resu_data = resu['data']['list']
        for i in range(len(resu_data)):
            if resu_data[i]['currency'] == str(coin) and resu_data[i]['type'] == 'trade':
                return float(resu_data[i]['balance'])
        return 0

def get_last_order(coin_symbol,type):
    # 获取上一次市价买单的成交价(即成本价)
    last_order_temp = hb.orders_list(symbol=coin_symbol, states='filled', direct='next',types=type)
    last_order_dict = last_order_temp['data']
    last_price = 0.00
    for i in range(len(last_order_dict)):
        if str(last_order_dict[i]['type'])[:4] == str(type)[:4]:
            last_order_id = last_order_dict[i]['id']
            last_price = float(last_order_dict[i]['field-cash-amount']) / float(last_order_dict[i]['field-amount'])
            break
    return last_price

def get_avg_order(coin_symbol,cur_price):
    # 获取上一次市价买单的成交价(即成本价)
    resu_orders_temp = hb.orders_matchresults(symbol=coin_symbol, direct='next')
    resu_orders_dict = resu_orders_temp['data']
    his_amount = []
    his_vol = []
    last_buy_ts = 0
    for i in range(len(resu_orders_dict)):
        if str(resu_orders_dict[i]['type'])[:4] == 'sell':
            break
        elif str(resu_orders_dict[i]['type'])[:3] == 'buy':
            his_amount.append(float(resu_orders_dict[i]['price'])*float(resu_orders_dict[i]['filled-amount']))
            his_vol.append(float(resu_orders_dict[i]['filled-amount']))
            last_buy_ts = max(last_buy_ts,int(resu_orders_dict[i]['created-at']))
    if len(his_amount) == 0:
        return 0.00,0
    else:
        ans = float((np.array(his_amount).mean())/(np.array(his_vol).mean()))
        return ans,math.floor(last_buy_ts/1000)
#
# def get_base_price():
#     resu = hb.get_balance(338)
#     if resu['status'] == 'error':
#         print('Acct_Info Errrrrr')
#         return -1
#     else:
#         resu_data = resu['data']['list']
#         for i in range(len(resu_data)):
#             if resu_data[i]['currency'] == curr_type and resu_data[i]['type'] == 'trade':
#                 return float(resu_data[i]['balance'])
#         return 0

if __name__ == '__main__':

    coin_list = ['btc','eos']
    #para_list_src = [(170,-340),(0.5,-0.7)]
    para_list = [(150,-470),(0.35,-1.7)]
    min_deal_limit = [0.0017,0.017]
    para_min = '15min'
    para_threshold = 1.003
    init_last_price = [0.00,14.30]

    pre_kline_ts = 0
    singal_time_cnt = 3
    can_buy = [1,1]
    buy_order_ts = ''
    while True:
        if singal_time_cnt > 4000:
            singal_time_cnt = 1
        else:
            singal_time_cnt += 1
        # 当前时间与时间戳
        state_dt = (datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = int(time.mktime(time.strptime(state_dt, "%Y-%m-%d %H:%M:%S")))

        break_flag = 0
        # id 378
        try:
            for i in range(len(coin_list)):
                coin_symbol = str(coin_list[i])+'usdt'
                # 获取最新行情，跌破10个点则止损，止损行情每17秒循环一次
                latest_price_temp = hb.get_ticker(coin_symbol)
                latest_price = float(latest_price_temp['tick']['close'])
                # 获取当前货币资产
                cap_coin_ori = Acct_Info(coin_list[i])
                cap_coin = math.floor(cap_coin_ori * 998) / 1000
                #print('Now State_Dt : ' + str(state_dt) + '   Coin : ' + str(coin_list[i]) + '   Cur_Close Price : ' + str(latest_price))

                # 获取上一次市价买单的成交价(即成本价)
                last_price,last_buy_ts = get_avg_order(coin_symbol,latest_price)
                if init_last_price[i] > 0 :
                    last_price = init_last_price[i]
                if last_buy_ts == 0:
                    last_buy_dt = 'NA'
                else:
                    last_buy_dt = datetime.datetime.fromtimestamp(last_buy_ts).strftime("%Y--%m--%d %H:%M:%S")
                if last_price == 0:
                    last_profit_rate = 1
                else:
                    last_profit_rate = float(latest_price/last_price)
                print('\033[0m'+'Now State_Dt : ' + str(state_dt) + '   Coin : ' + str(coin_list[i]) + '   Quant : ' +str(math.floor(cap_coin_ori*1000)/1000)+ '   Cur_Close Price : ' + str(latest_price) + '   Pre_Buy Price : '+ str(last_price)+'   Profit_Rate : '+ str(round(last_profit_rate*100-100,2)) + ' %')
                if last_profit_rate < 0.7 and cap_coin >= min_deal_limit[i]:
                    resp = hb.send_order(amount=cap_coin,source='api',symbol=coin_symbol,_type='sell-market')
                    print('\033[1;31;47m' + 'xxxxxxxBAD SELL !!   State_Dt : ' + str(state_dt) + '   Coin : ' + str(coin_list[i]) + '   Response : ' + str(resp))
                    break_flag = 1
                    break
                # 获取信号，返回值包含最新数据的时间戳，信号行情每 4*17=68 秒循环一次
                if divmod(singal_time_cnt,4)[1] == 0:
                    resu_single,cur_kline_ts,up_limit,low_limit,delt = Signal2(coin_symbol,para_min,para_list[i][0],para_list[i][1],200)
                    if resu_single == 0:
                        print('\033[0m' + '   ===>   Signal : ' + str(resu_single) + '   at   ' + str(state_dt) + '   on Coin : ' + str(coin_list[i]) + '   Cur_Price : ' + str(latest_price) + '   Up_Limit : ' + str(math.floor(up_limit * 1000) / 1000) + '   Low_Limit : ' + str(math.floor(low_limit * 1000) / 1000) + '   Delt : ' + str(math.floor(delt * 1000) / 1000))
                    elif resu_single == 1:
                        print('\033[1;31;0m' + '   ===>   Signal : ' + str(resu_single) + '   at   ' + str(state_dt) + '   on Coin : ' + str(coin_list[i]) + '   Cur_Price : ' + str(latest_price) + '   Up_Limit : ' + str(math.floor(up_limit * 1000) / 1000) + '   Low_Limit : ' + str(math.floor(low_limit * 1000) / 1000) + '   Delt : ' + str(math.floor(delt * 1000) / 1000))
                    elif resu_single == -1:
                        print('\033[1;32;0m' + '   ===>   Signal : ' + str(resu_single) + '   at   ' + str(state_dt) + '   on Coin : ' + str(coin_list[i]) + '   Cur_Price : ' + str(latest_price) + '   Up_Limit : ' + str(math.floor(up_limit * 1000) / 1000) + '   Low_Limit : ' + str(math.floor(low_limit * 1000) / 1000) + '   Delt : ' + str(math.floor(delt * 1000) / 1000))

                    time_delt = timestamp - cur_kline_ts
                    # 时间间隔大于15min 即900时间戳的话，说明最新的15分钟数据还没更新，每隔 17 秒取数一次直到更新。
                    if time_delt >= 900:
                        singal_time_cnt = 3
                        continue
                    else:
                        # 信号为 1 且资金余额可买大于最小单位0.001个币时，买入；为 -1 且 市价大于买入均价时，卖出
                        # 先更新订单状态，买单完成后 2 小时后再释放 买锁
                        if timestamp - last_buy_ts >= 10800:
                            can_buy[i] = 1

                        # 先判断卖出
                        if resu_single < 0 and latest_price > last_price*para_threshold:
                            # 获取币种资产
                            cap_coin_ori = Acct_Info(coin_list[i])
                            cap_coin = math.floor(cap_coin_ori * 998) / 1000
                            if cap_coin >= min_deal_limit[i]:
                                resp = hb.send_order(amount=cap_coin, source='api',symbol=coin_symbol, _type='sell-market')
                                coin_profit = (latest_price-last_price)*cap_coin*0.998
                                coin_profit_rt = ((latest_price*0.998)/(last_price/0.998)-1)*100
                                print('\033[1;32;0m' + '   *******PREDICT SELL !!   State_Dt : ' + str(state_dt) +'   Coin : ' +str(coin_list[i]) + '   Profit : ' +str(coin_profit) +'   Profit_rate : ' +str(coin_profit_rt) +' %   Response : ' + str(resp))

                        # 后判断买入
                        elif resu_single > 0 :
                            # 获取usdt资产
                            cap_usdt_ori = Acct_Info('usdt')
                            cap_usdt = math.floor(cap_usdt_ori * 998) / 1000
                            if cap_usdt/latest_price > 0.001:
                                # 仓位管理，确定配仓比例
                                pos_temp = get_portfolio(coin_list,para_min)
                                pos = pos_temp[1][1][i]
                                buy_money = math.floor(cap_usdt*pos*100)/100
                                if buy_money > 15 and can_buy[i] == 1:
                                    resp = hb.send_order(amount=buy_money, source='api',symbol=coin_symbol,_type='buy-market')
                                    if str(resp['status']) == 'ok':
                                        can_buy[i] = 0
                                        # if coin_list[i] == 'btc':
                                        #     para_list[i][1] = para_list[i][1] - 70
                                        # elif coin_list[i] == 'eos':
                                        #     para_list[i][1] = para_list[i][1] - 0.3
                                    print('\033[1;31;0m' + '   >>>>>>>   Signal Buy   State_Dt : ' + str(state_dt) +'   Coin : '+str(coin_list[i])+'   Cap_Usdt : '+str(math.floor(cap_usdt_ori*100)/100)+'   Buy_Money : ' + str(buy_money) + '   Pos : '+str(math.floor(pos*10000)/100) + ' %   Response : ' + str(resp))
                                else:
                                    print('\033[1;31;0m' + '   >>>>>>>   Signal Buy   State_Dt : ' + str(state_dt) + '   Coin : ' + str(
                                        coin_list[i])+'   Cap_Usdt : '+str(math.floor(cap_usdt_ori*100)/100)+'   Buy_Money : ' + str(buy_money) + '   Pos : '+str(math.floor(pos*10000)/100) + ' %   Not Enough Money !!')
                            else:
                                print('\033[1;31;0m' + '   *******Signal Buy   State_Dt : ' + str(state_dt) + '   Coin : ' + str(
                                    coin_list[i]) + '    Not Enough Money !!')
                time.sleep(1)
            if break_flag == 1:
                break
            time.sleep(17)
        except Exception as exp:
            singal_time_cnt = 3
            print(str(state_dt) + '   Exception : ' + str(exp))
            time.sleep(34)
            continue
