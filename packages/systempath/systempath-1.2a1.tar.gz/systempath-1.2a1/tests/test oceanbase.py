#!/usr/bin/env python3.6

import jaydebeapi


def ob_test():
    url = 'jdbc:oceanbase://10.135.136.11:2883/E_TYXB'
    user = 'E_TYXB@nj_test#nj_test_cluster'
    password = 'wbZjqc9V_psWGqZY9f'
    driver = 'com.alipay.oceanbase.jdbc.Driver'
    jarFile = './oceanbase-client-2.4.0.jar'
    sqlStr = 'select 1 from dual'  # SQL 测试语句
    # conn=jaydebeapi.connect('oracle.jdbc.driver.OracleDriver','jdbc:oracle:thin:@127.0.0.1:1521/orcl',['hwf_model','hwf_model'],'E:/pycharm/lib/ojdbc14.jar')
    conn = jaydebeapi.connect(driver, url, [user, password], jarFile)
    curs = conn.cursor()
    curs.execute(sqlStr)
    result = curs.fetchall()
    print(result)
    curs.close()
    conn.close()


ob_test()
