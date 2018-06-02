import pymysql
import talib as ta
import numpy as np
import My_CAP
import Operator as op

def singal(stock_code,pre_date_seq,para_min,para_up,para_low):
    # 建立数据库连接,清空相关表
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    sql = "select * from %s_%smin a where a.state_dt >= '%s' and a.state_dt <= '%s' order by a.state_dt asc "%(stock_code,para_min,pre_date_seq[0],pre_date_seq[-1])
    cursor.execute(sql)
    done_set = cursor.fetchall()
    close = np.array([float(x[2]) for x in done_set])

    macd_temp = ta.MACD(close,12,26,9)
    up_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x > 0]).max()*para_up
    low_limit = np.array([x for x in macd_temp[2] if str(x) != 'nan' and x < 0]).min()*para_low

    macd = macd_temp[2][-1]

    action_flag = 0
    # flag
    if (((macd_temp[2][-1] + macd_temp[2][-2] + macd_temp[2][-3]) * 2) < low_limit) and (
            macd_temp[2][-2] < macd_temp[2][-1]) and (macd_temp[2][-2] < macd_temp[2][-3]) and (
            macd_temp[2][-1] < 0) and (macd_temp[2][-3] < 0):
        action_flag = 1
    elif (((macd_temp[2][-1] + macd_temp[2][-2] + macd_temp[2][-3]) * 2) > up_limit) and (
            macd_temp[2][-2] > macd_temp[2][-1]) and (macd_temp[2][-2] > macd_temp[2][-3]) and (
            macd_temp[2][-1] > 0) and (macd_temp[2][-3] > 0):
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

    price_avg_long = float(amount.sum()/vol.sum())
    price_avg_short = float(amount[-1]/vol[-1])

    action_flag = 0
    if price_avg_short - price_avg_long > para_up:
        action_flag = -1
    elif price_avg_short - price_avg_long < para_low:
        action_flag = 1


    db.close()
    return action_flag

def Bot_BactTest(stock_code,date_seq,para_min,para_up_limit,para_low_limit):

    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    sql_dele = "delete from %s_my_cap where seq != 1"%(stock_code)
    cursor.execute(sql_dele)
    db.commit()

    for i in range(200,len(date_seq)):

        ans = singal2(stock_code,date_seq[i-200:i],para_min,para_up_limit,para_low_limit)

        #ans2 = warning_macd(date_seq[i-200:i],para_warning)
        ans2 = 0
        print('State_Dt : ' + str(date_seq[i]) + '   Singal : '+str(ans) + '   Warning : ' + str(ans2))
        cap = My_CAP.My_CAP(stock_code)
        buy_money = cap.usdt_acct
        if ans == 1 and ans2 == 0:
            op.buy(stock_code,date_seq[i-1],buy_money,para_min)
        elif ans == -1:
            op.sell(stock_code,date_seq[i-1],-1,para_min)
        elif ans == -1:
            op.sell(stock_code,date_seq[i-1],0,para_min)
    db.commit()
    print('ALL Finished!!')

    sql_resu_select = "select * from %s_my_cap order by seq desc limit 1"%(stock_code)
    cursor.execute(sql_resu_select)
    done_set_resu_select = cursor.fetchall()
    final_cap = done_set_resu_select[0][0]
    sql_resu = "insert into coordinate_descent(Bot_Name,up_limit,low_limit,final_cap,state_dt)values('%s','%.2f','%.2f','%.2f','%s')"%(str(str(stock_code)+str(para_min))+str('Signal2'),float(para_up_limit),float(para_low_limit),float(final_cap),date_seq[-1])
    cursor.execute(sql_resu)
    db.commit()
    db.close()

def CoordinateDescentMain(para_min,coin,para_len,para_state_dt):

    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    sql_dt_seq = "select distinct state_dt from %s_%smin where state_dt < '%s' order by state_dt desc limit %i" % (coin,para_min,para_state_dt,int(para_len))
    cursor.execute(sql_dt_seq)
    done_set_dt = cursor.fetchall()
    db.commit()
    bot_name = str(coin) + str(para_min)+str('Signal2')
    date_seq = [x[0] for x in done_set_dt][::-1]
    sql_done = "select * from coordinate_descent a where a.state_dt = '%s' and bot_name = '%s'"%(date_seq[-1],bot_name)
    cursor.execute(sql_done)
    done_set_done = cursor.fetchall()
    db.commit()
    if len(done_set_done) > 0:
        done_list = [(str(int(x[1]*100)/100)[:3],str(int(x[2]*100)/100)[:3]) for x in done_set_done]
    else:
        done_list = []

    if coin == 'eos':
        up_list = np.arange(0,1,0.1)
        low_list = np.arange(-1, 0, 0.1)
    elif coin == 'btc':
        up_list = np.arange(0, 200, 20)
        low_list = np.arange(-200, 0, 20)
    for i in range(len(up_list)):
        for j in range(len(low_list)):
            comp = (str(float(up_list[i]*100)/100)[:3],str(float(low_list[j]*100)/100)[:3])
            if comp in done_list:
                continue
            else:
                Bot_BactTest(coin,date_seq,para_min,up_list[i],low_list[j])
            #print('up : ' + str(up_list[i]) + '   low : ' + str(low_list[j]))
    print('Coordinate Descent ALL FINISHED !!!')
    sql = "select * from coordinate_descent order by final_cap desc,low_limit desc,up_limit asc limit 1"
    cursor.execute(sql)
    para_set = cursor.fetchall()
    db.commit()
    resu_up_limit = para_set[0][1]
    resu_low_limit = para_set[0][2]
    db.close()
    return float(resu_up_limit),float(resu_low_limit)



if __name__ == '__main__':
    para_min = '15'
    stock_code = 'eos'

    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    sql_dt_seq = "select distinct state_dt from %s_%smin order by state_dt desc limit 1000" % (stock_code,para_min)
    cursor.execute(sql_dt_seq)
    done_set_dt = cursor.fetchall()
    db.commit()
    bot_name = str(stock_code) + str(para_min)+str('Signal2')
    date_seq = [x[0] for x in done_set_dt][::-1]
    sql_done = "select * from coordinate_descent a where a.state_dt = '%s' and bot_name = '%s'"%(date_seq[-1],bot_name)
    cursor.execute(sql_done)
    done_set_done = cursor.fetchall()
    db.commit()
    done_list = [(str(x[1])[:3],str(x[2])[:3]) for x in done_set_done]
    db.close()

    up_list = np.arange(0,1,0.1)
    low_list = np.arange(-1, 0, 0.1)
    for i in range(len(up_list)):
        for j in range(len(low_list)):
            comp = (str(up_list[i])[:3],str(low_list[j])[:3])
            if comp in done_list:
                continue
            else:
                Bot_BactTest(stock_code,date_seq,para_min,up_list[i],low_list[j])
            #print('up : ' + str(up_list[i]) + '   low : ' + str(low_list[j]))
    print('ALL FINISHED !!!')
