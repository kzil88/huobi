import DC
import pymysql
from sklearn import svm
import numpy as np

def ModelEvaluate(para_min,threshold,date_seq):

    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    print_len = len(date_seq) - 5
    for i in range(len(date_seq)-5):
        sql_select = "select * from btc_%smin a where a.state_dt >= '%s' and a.state_dt <= '%s'"%(para_min,date_seq[i],date_seq[i+5])
        cursor.execute(sql_select)
        done_set2 = cursor.fetchall()
        close_list = [x[2] for x in done_set2]
        if len(close_list) <= 1:
            return 0,0,0,0
        # after_max = max(close_list[1:len(close_list)])
        # after_min = min(close_list[1:len(close_list)])
        # resu = 0
        # if after_max/close_list[0] >= 1.03:
        #     resu = 1
        # elif  after_min/close_list[0] < 0.97:
        #     resu = -1
        after_mean = np.array(close_list[1:len(close_list)]).mean()
        resu = 0
        if after_mean/close_list[0] >= threshold:
            resu = 1
        else:
            resu = -1
        sql_update = "update btc_model_test w set w.resu_real = '%i' where w.state_dt = '%s'"%(resu,date_seq[i+1])
        cursor.execute(sql_update)
        db.commit()
        print('Evaluating...  ' + str(date_seq[i+1]) + '   ' + str(i+1) + '  of  ' + str(print_len))

    sql_resu_acc_son = "select count(*) from btc_model_test a where a.resu_real is not null and a.resu_predict = 1 and a.resu_real = 1"
    cursor.execute(sql_resu_acc_son)
    acc_son = cursor.fetchall()[0][0]
    sql_resu_acc_mon = "select count(*) from btc_model_test a where a.resu_real is not null and a.resu_real = 1"
    cursor.execute(sql_resu_acc_mon)

    acc_mon = cursor.fetchall()[0][0]
    if acc_mon == 0:
        return 0,0,0,0
    acc = acc_son/acc_mon

    sql_resu_recall_son = "select count(*) from btc_model_test a where a.resu_real is not null and a.resu_predict = a.resu_real"
    cursor.execute(sql_resu_recall_son)
    recall_son = cursor.fetchall()[0][0]
    sql_resu_recall_mon = "select count(*) from btc_model_test a where a.resu_real is not null"
    cursor.execute(sql_resu_recall_mon)
    recall_mon = cursor.fetchall()[0][0]
    recall = recall_son / recall_mon

    sql_resu_acc_neg_son = "select count(*) from btc_model_test a where a.resu_real is not null and a.resu_predict = -1 and a.resu_real = -1"
    cursor.execute(sql_resu_acc_neg_son)
    acc_neg_son = cursor.fetchall()[0][0]
    sql_resu_acc_neg_mon = "select count(*) from btc_model_test a where a.resu_real is not null and a.resu_real = -1"
    cursor.execute(sql_resu_acc_neg_mon)
    acc_neg_mon = cursor.fetchall()[0][0]
    if acc_neg_mon == 0:
        acc_neg_mon = -1
    acc_neg = acc_neg_son / acc_neg_mon
    if acc+recall == 0:
        return 0,0,0,0
    f1 = (2*acc*recall)/(acc+recall)

    print(date_seq[-1] + '   ACC : ' + str(acc) + '   RECALL : ' + str(recall)+ '   ACC_NEG : ' + str(acc_neg) + '   F1 : ' + str(f1))

    return acc,recall,acc_neg,f1


if __name__ == '__main__':
    para_min = '15'
    threshold = 1.0001

    # 建立数据库连接,剔除已入库的部分
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    sql_truncate = "truncate table btc_model_test"
    cursor.execute(sql_truncate)
    db.commit()

    sql_dt_seq = "select distinct state_dt from btc_%smin order by state_dt asc" % (para_min)
    cursor.execute(sql_dt_seq)
    done_set_dt = cursor.fetchall()
    db.commit()
    date_seq = [x[0] for x in done_set_dt]

    print_len = len(date_seq)-1000
    for i in range(1900,len(date_seq)):
        dc = DC.data_collect2(date_seq[i-1000],date_seq[i],para_min,threshold)
        train = dc.data_train
        target = dc.data_target
        test_case = [dc.test_case]
        print(dc.cnt_pos)
        if dc.cnt_pos == 0:
            return_flag = 1
            print('No Positive Samples!')
            break
        w = (len(target) / dc.cnt_pos)
        if len(target) / dc.cnt_pos == 1:
            return_flag = 1
            print('No Negtive Samples!')
            break
        #model = svm.SVC(class_weight={1: w})
        model = svm.SVC()
        model.fit(train, target)
        #print(model.score(train,target))
        ans2 = model.predict(test_case)

        sql_insert = "insert into btc_model_test(state_dt,para_min,resu_predict)values('%s','%s','%i')"%(date_seq[i],para_min,int(ans2[0]))
        cursor.execute(sql_insert)
        db.commit()
        print('SVM Predicting...  ' + str(date_seq[i])  + '   ' + str(i-999) + '  of  ' + str(print_len))

    resu_ev = ModelEvaluate(para_min,threshold,date_seq[999:])

