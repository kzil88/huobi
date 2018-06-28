import pymysql.cursors

class My_CAP(object):
    capital = 0.00
    btc_acct = 0.000000
    usdt_acct = 0.00
    btc_avg_price = 0.00
    time_stamp = ''

    def __init__(self,stock_code):
        # 建立数据库连接
        db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
        cursor = db.cursor()
        try:
            sql_select = 'select * from %s_my_cap a order by seq desc limit 1'%(stock_code)
            cursor.execute(sql_select)
            done_set = cursor.fetchall()
            if len(done_set) > 0:
                self.capital = float(done_set[0][0])
                self.btc_acct = float(done_set[0][1])
                self.usdt_acct = float(done_set[0][2])
                self.btc_avg_price = float(done_set[0][3])
                #self.btc_avg_price = float(done_set[0][4])

        except Exception as excp:
            #db.rollback()
            print(excp)

        db.close()
