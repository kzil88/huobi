import pymysql.cursors
import My_CAP

def buy(stock_code,opdate,buy_money,para_min):
    # 建立数据库连接
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    deal_buy = My_CAP.My_CAP(stock_code)
    #后买入
    if deal_buy.usdt_acct > 500:
        sql_buy = "select * from %s_%smin a where a.state_dt = '%s'" % (stock_code,para_min,opdate)

        cursor.execute(sql_buy)
        done_set_buy = cursor.fetchall()
        if len(done_set_buy) == 0:
            return -1
        buy_price = float(done_set_buy[0][2])
        # if buy_price >= 195:
        #     return 0
        vol = min(deal_buy.usdt_acct-500, buy_money)/buy_price

        if vol <= 0.001:
            return 0
        new_btc_acct = deal_buy.btc_acct + vol
        new_usdt_acct = deal_buy.usdt_acct - vol * buy_price * 1.002
        new_capital = new_btc_acct*buy_price +new_usdt_acct
        new_btc_avg_price = (deal_buy.btc_avg_price*deal_buy.btc_acct + vol * buy_price*1.002)/(vol+deal_buy.btc_acct)
        sql_buy_update2 = "insert into %s_my_cap(capital,btc_acct,usdt_acct,btc_avg_price,deal_action,stock_code,stock_vol,state_dt,deal_price)VALUES ('%.2f', '%.6f', '%.2f','%.2f','%s','%s','%i','%s','%.2f')" % (stock_code,new_capital, new_btc_acct,new_usdt_acct,new_btc_avg_price, 'buy', stock_code, vol, opdate, buy_price)
        cursor.execute(sql_buy_update2)
        db.commit()

        db.close()
        return 1
    db.close()
    return 0

def sell(stock_code,opdate,predict,para_min):
    # 建立数据库连接
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    deal = My_CAP.My_CAP(stock_code)
    init_price = deal.btc_avg_price
    hold_vol = deal.btc_acct
    #hold_mins = (int(cur_ts) - int(deal.time_stamp))/60
    #hold_days = (int(cur_ts) - int(deal.time_stamp))/1440
    sql_sell_select = "select * from %s_%smin a where a.state_dt = '%s'" % (stock_code,para_min, opdate)

    cursor.execute(sql_sell_select)
    done_set_sell_select = cursor.fetchall()
    if len(done_set_sell_select) == 0:
        return -1
    sell_price = float(done_set_sell_select[0][2])

    if sell_price < init_price*0.95 and hold_vol > 0:
        new_btc_acct = 0.000000
        new_usdt_acct = deal.usdt_acct + sell_price*hold_vol*0.998
        new_capital = new_usdt_acct
        new_btc_avg_price = sell_price*0.998
        new_profit = (sell_price*0.998-init_price)*hold_vol
        new_profit_rate = (sell_price*0.998)/init_price
        sql_sell_insert2 = "insert into %s_my_cap(capital,btc_acct,usdt_acct,btc_avg_price,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.6f','%.2f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" %(stock_code,new_capital,new_btc_acct,new_usdt_acct,new_btc_avg_price,'SELL',stock_code,hold_vol,new_profit,new_profit_rate,'BADSELL',opdate,sell_price)
        cursor.execute(sql_sell_insert2)
        db.commit()
        db.close()
        return 1

    # elif hold_days >= 1 and hold_vol > 0:
    #     new_btc_acct = 0.000000
    #     new_usdt_acct = deal.usdt_acct + sell_price * hold_vol * 0.998
    #     new_capital = new_usdt_acct
    #     new_profit = (sell_price * 0.998 - init_price) * hold_vol
    #     new_profit_rate = (sell_price * 0.998) / init_price
    #     sql_sell_insert2 = "insert into my_capital(capital,btc_acct,usdt_acct,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.6f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (
    #     new_capital, new_btc_acct, new_usdt_acct, 'SELL', stock_code, hold_vol, new_profit, new_profit_rate, 'OVERTIME',
    #     opdate, sell_price)
    #     cursor.execute(sql_sell_insert2)
    #     db.commit()
    #     db.close()
    #     return 1


    elif predict == -1 and hold_vol > 0 and sell_price > init_price:
    #elif predict == -1 and hold_vol > 0 :

        new_btc_acct = 0.000000
        new_usdt_acct = deal.usdt_acct + sell_price * hold_vol * 0.998
        new_capital = new_usdt_acct
        new_btc_avg_price = sell_price*0.998
        new_profit = (sell_price * 0.998 - init_price) * hold_vol
        if init_price == 0:
            new_profit_rate = 0.00
        else:
            new_profit_rate = (sell_price * 0.998) / init_price
        sql_sell_insert2 = "insert into %s_my_cap(capital,btc_acct,usdt_acct,btc_avg_price,deal_action,stock_code,stock_vol,profit,profit_rate,bz,state_dt,deal_price)values('%.2f','%.6f','%.2f','%.2f','%s','%s','%.2f','%.2f','%.2f','%s','%s','%.2f')" % (stock_code,new_capital, new_btc_acct, new_usdt_acct,new_btc_avg_price, 'SELL', stock_code, hold_vol, new_profit, new_profit_rate,
            'PredictSell',
            opdate, sell_price)
        cursor.execute(sql_sell_insert2)
        db.commit()
        db.close()
        return 1
    db.close()
    return 0

