import pymysql.cursors
import My_CAP_MIX

def buy(coin,opdate,buy_money,para_min):
    # 建立数据库连接
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    deal_buy = My_CAP_MIX.My_CAP_MIX()
    #后买入
    if deal_buy.usdt_acct > 500:
        new_price = {}
        coin_list = ['btc','eth','eos']
        for i in range(len(coin_list)):
            sql_buy = "select * from %s_%smin a where a.state_dt = '%s'" % (coin_list[i],para_min,opdate)
            cursor.execute(sql_buy)
            done_set_buy = cursor.fetchall()
            if len(done_set_buy) == 0:
                return -1
            new_price[coin_list[i]] = float(done_set_buy[0][2])
        buy_price = new_price[coin]
        vol = min(deal_buy.usdt_acct-500, buy_money)/buy_price
        if vol <= 0.001:
            return 0

        new_usdt_acct = deal_buy.usdt_acct - vol * buy_price * 1.002
        if coin == 'btc':
            new_btc_acct = deal_buy.btc_acct + vol
            new_capital = new_btc_acct * buy_price + new_usdt_acct + deal_buy.eth_acct*new_price['eth'] + deal_buy.eos_acct*new_price['eos']
            new_btc_avg_price = (deal_buy.btc_avg_price * deal_buy.btc_acct + vol * buy_price * 1.002) / (
                        vol + deal_buy.btc_acct)
            new_eth_acct = deal_buy.eth_acct
            new_eth_avg_price = new_price['eth']
            new_eos_acct = deal_buy.eos_acct
            new_eos_avg_price = new_price['eos']
        elif coin == 'eth':
            new_eth_acct = deal_buy.eth_acct + vol
            new_capital = new_eth_acct * buy_price + new_usdt_acct + deal_buy.btc_acct*new_price['btc'] + deal_buy.eos_acct*new_price['eos']
            new_eth_avg_price = (deal_buy.eth_avg_price * deal_buy.eth_acct + vol * buy_price * 1.002) / (
                    vol + deal_buy.eth_acct)
            new_btc_acct = deal_buy.btc_acct
            new_btc_avg_price = new_price['btc']
            new_eos_acct = deal_buy.eos_acct
            new_eos_avg_price = new_price['eos']
        elif coin == 'eos':
            new_eos_acct = deal_buy.eos_acct + vol
            new_capital = new_eos_acct * buy_price + new_usdt_acct + deal_buy.eth_acct*new_price['eth'] + deal_buy.btc_acct*new_price['btc']
            new_eos_avg_price = (deal_buy.eos_avg_price * deal_buy.eos_acct + vol * buy_price * 1.002) / (
                    vol + deal_buy.eos_acct)
            new_btc_acct = deal_buy.btc_acct
            new_btc_avg_price = new_price['btc']
            new_eth_acct = deal_buy.eth_acct
            new_eth_avg_price = new_price['eth']

        sql_buy_update2 = "insert into mix_my_cap(capital,usdt_acct,btc_acct,btc_avg_price,eth_acct,eth_avg_price,eos_acct,eos_avg_price,deal_action,stock_code,stock_vol,state_dt,deal_price)VALUES ('%.2f', '%.2f','%.6f','%.2f','%.6f','%.2f','%.6f','%.2f','%s','%s','%i','%s','%.2f')" % (new_capital, new_usdt_acct,new_btc_acct,new_btc_avg_price,new_eth_acct,new_eth_avg_price,new_eos_acct,new_eos_avg_price, 'buy', coin, vol, opdate, buy_price)
        cursor.execute(sql_buy_update2)
        db.commit()

        db.close()
        return 1
    db.close()
    return 0

def sell(coin,opdate,predict,para_min):
    para_threshold = 1.003
    bad_sell_threshold = 0.7

    # 建立数据库连接
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    deal = My_CAP_MIX.My_CAP_MIX()

    sql_sell_select = "select * from %s_%smin a where a.state_dt = '%s'" % (coin,para_min, opdate)

    cursor.execute(sql_sell_select)
    done_set_sell_select = cursor.fetchall()
    if len(done_set_sell_select) == 0:
        return -1
    sell_price = float(done_set_sell_select[0][2])

    if coin == 'btc':
        init_price = deal.btc_avg_price
        hold_vol = deal.btc_acct
        if sell_price < init_price * bad_sell_threshold and hold_vol > 0:
        #if (sell_price < init_price * 0.95 and hold_vol > 0) or (sell_price > init_price * 1.03 and hold_vol > 0):
            new_btc_acct = 0.000000
            new_usdt_acct = deal.usdt_acct + sell_price * hold_vol * 0.998
            new_capital = new_usdt_acct + deal.eth_acct*deal.eth_avg_price + deal.eos_acct*deal.eos_avg_price
            new_btc_avg_price = sell_price * 0.998
            new_profit = (sell_price * 0.998 - init_price) * hold_vol
            new_profit_rate = (sell_price * 0.998) / init_price
            new_eth_acct = deal.eth_acct
            new_eth_avg_price = deal.eth_avg_price
            new_eos_acct = deal.eos_acct
            new_eos_avg_price = deal.eos_avg_price

            sql_sell_insert2 = "insert into mix_my_cap(capital,usdt_acct,btc_acct,btc_avg_price,eth_acct,eth_avg_price,eos_acct,eos_avg_price,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.6f','%.2f','%.6f','%.2f','%.6f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
                new_capital, new_usdt_acct, new_btc_acct, new_btc_avg_price, new_eth_acct, new_eth_avg_price,
                new_eos_acct,
                new_eos_avg_price, 'SELL', coin, hold_vol, new_profit, new_profit_rate, 'BADSELL', opdate, sell_price)
            cursor.execute(sql_sell_insert2)
            db.commit()
            db.close()
            return 77
        elif predict == -1 and hold_vol > 0 and sell_price > init_price*para_threshold:
            new_btc_acct = 0.000000
            new_usdt_acct = deal.usdt_acct + sell_price * hold_vol * 0.998
            new_capital = new_usdt_acct + deal.eth_acct*deal.eth_avg_price + deal.eos_acct*deal.eos_avg_price
            new_btc_avg_price = sell_price * 0.998
            new_profit = (sell_price * 0.998 - init_price) * hold_vol
            if init_price == 0:
                new_profit_rate = 0.00
            else:
                new_profit_rate = (sell_price * 0.998) / init_price
            new_eth_acct = deal.eth_acct
            new_eth_avg_price = deal.eth_avg_price
            new_eos_acct = deal.eos_acct
            new_eos_avg_price = deal.eos_avg_price

            sql_sell_insert2 = "insert into mix_my_cap(capital,usdt_acct,btc_acct,btc_avg_price,eth_acct,eth_avg_price,eos_acct,eos_avg_price,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.6f','%.2f','%.6f','%.2f','%.6f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
            new_capital, new_usdt_acct, new_btc_acct, new_btc_avg_price, new_eth_acct, new_eth_avg_price, new_eos_acct,
            new_eos_avg_price, 'SELL', coin, hold_vol, new_profit, new_profit_rate, 'PREDICTSELL', opdate, sell_price)
            cursor.execute(sql_sell_insert2)
            db.commit()
            db.close()
            return 1

    elif coin == 'eth':
        init_price = deal.eth_avg_price
        hold_vol = deal.eth_acct
        if sell_price < init_price * bad_sell_threshold and hold_vol > 0:
        #if (sell_price < init_price * 0.95 and hold_vol > 0) or (sell_price > init_price * 1.03 and hold_vol > 0):

            new_eth_acct = 0.000000
            new_usdt_acct = deal.usdt_acct + sell_price * hold_vol * 0.998
            new_capital = new_usdt_acct + deal.btc_acct*deal.btc_avg_price + deal.eos_acct*deal.eos_avg_price
            new_eth_avg_price = sell_price * 0.998
            new_profit = (sell_price * 0.998 - init_price) * hold_vol
            new_profit_rate = (sell_price * 0.998) / init_price
            new_btc_acct = deal.btc_acct
            new_btc_avg_price = deal.btc_avg_price
            new_eos_acct = deal.eos_acct
            new_eos_avg_price = deal.eos_avg_price

            sql_sell_insert2 = "insert into mix_my_cap(capital,usdt_acct,btc_acct,btc_avg_price,eth_acct,eth_avg_price,eos_acct,eos_avg_price,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.6f','%.2f','%.6f','%.2f','%.6f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
                new_capital, new_usdt_acct, new_btc_acct, new_btc_avg_price, new_eth_acct, new_eth_avg_price,
                new_eos_acct,
                new_eos_avg_price, 'SELL', coin, hold_vol, new_profit, new_profit_rate, 'BADSELL', opdate, sell_price)
            cursor.execute(sql_sell_insert2)
            db.commit()
            db.close()
            return 77
        elif predict == -1 and hold_vol > 0 and sell_price > init_price*para_threshold:
            new_eth_acct = 0.000000
            new_usdt_acct = deal.usdt_acct + sell_price * hold_vol * 0.998
            new_capital = new_usdt_acct + deal.btc_acct*deal.btc_avg_price + deal.eos_acct*deal.eos_avg_price
            new_eth_avg_price = sell_price * 0.998
            new_profit = (sell_price * 0.998 - init_price) * hold_vol
            if init_price == 0:
                new_profit_rate = 0.00
            else:
                new_profit_rate = (sell_price * 0.998) / init_price
            new_btc_acct = deal.btc_acct
            new_btc_avg_price = deal.btc_avg_price
            new_eos_acct = deal.eos_acct
            new_eos_avg_price = deal.eos_avg_price

            sql_sell_insert2 = "insert into mix_my_cap(capital,usdt_acct,btc_acct,btc_avg_price,eth_acct,eth_avg_price,eos_acct,eos_avg_price,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.6f','%.2f','%.6f','%.2f','%.6f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
                new_capital, new_usdt_acct, new_btc_acct, new_btc_avg_price, new_eth_acct, new_eth_avg_price, new_eos_acct,
                new_eos_avg_price, 'SELL', coin, hold_vol, new_profit, new_profit_rate, 'PREDICTSELL', opdate, sell_price)
            cursor.execute(sql_sell_insert2)
            db.commit()
            db.close()
            return 1

    elif coin == 'eos':
        init_price = deal.eos_avg_price
        hold_vol = deal.eos_acct
        if sell_price < init_price * bad_sell_threshold and hold_vol > 0:
        #if (sell_price < init_price * 0.95 and hold_vol > 0) or (sell_price > init_price * 1.03 and hold_vol > 0):

            new_eos_acct = 0.000000
            new_usdt_acct = deal.usdt_acct + sell_price * hold_vol * 0.998
            new_capital = new_usdt_acct + deal.btc_acct*deal.btc_avg_price + deal.eth_acct*deal.eth_avg_price
            new_eos_avg_price = sell_price * 0.998
            new_profit = (sell_price * 0.998 - init_price) * hold_vol
            new_profit_rate = (sell_price * 0.998) / init_price
            new_btc_acct = deal.btc_acct
            new_btc_avg_price = deal.btc_avg_price
            new_eth_acct = deal.eth_acct
            new_eth_avg_price = deal.eth_avg_price

            sql_sell_insert2 = "insert into mix_my_cap(capital,usdt_acct,btc_acct,btc_avg_price,eth_acct,eth_avg_price,eos_acct,eos_avg_price,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.6f','%.2f','%.6f','%.2f','%.6f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
                new_capital, new_usdt_acct, new_btc_acct, new_btc_avg_price, new_eth_acct, new_eth_avg_price,
                new_eos_acct,
                new_eos_avg_price, 'SELL', coin, hold_vol, new_profit, new_profit_rate, 'BADSELL', opdate, sell_price)
            cursor.execute(sql_sell_insert2)
            db.commit()
            db.close()
            return 77
        elif predict == -1 and hold_vol > 0 and sell_price > init_price*para_threshold:
            new_eos_acct = 0.000000
            new_usdt_acct = deal.usdt_acct + sell_price * hold_vol * 0.998
            new_capital = new_usdt_acct  + deal.btc_acct*deal.btc_avg_price + deal.eth_acct*deal.eth_avg_price
            new_eos_avg_price = sell_price * 0.998
            new_profit = (sell_price * 0.998 - init_price) * hold_vol
            if init_price == 0:
                new_profit_rate = 0.00
            else:
                new_profit_rate = (sell_price * 0.998) / init_price
            new_btc_acct = deal.btc_acct
            new_btc_avg_price = deal.btc_avg_price
            new_eth_acct = deal.eth_acct
            new_eth_avg_price = deal.eth_avg_price

            sql_sell_insert2 = "insert into mix_my_cap(capital,usdt_acct,btc_acct,btc_avg_price,eth_acct,eth_avg_price,eos_acct,eos_avg_price,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.2f','%.6f','%.2f','%.6f','%.2f','%.6f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
                new_capital, new_usdt_acct, new_btc_acct, new_btc_avg_price, new_eth_acct, new_eth_avg_price, new_eos_acct,
                new_eos_avg_price, 'SELL', coin, hold_vol, new_profit, new_profit_rate, 'PREDICTSELL', opdate, sell_price)
            cursor.execute(sql_sell_insert2)
            db.commit()
            db.close()
            return 1





    db.close()
    return 0

