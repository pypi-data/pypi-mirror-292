# # cx_Oracle==7.3
# import cx_Oracle
#
# dsn = cx_Oracle.makedsn('10.135.136.11', 2883, service_name='E_TYXB')
# conn = cx_Oracle.connect(
#     'E_TYXB@nj_test#nj_test_cluster', 'wbZjqc9V_psWGqZY9f', dsn
# )
#
# # conn_str = 'E_TYXB@nj_test#nj_test_cluster/wbZjqc9V_psWGqZY9f@10.135.136.11:2883/E_TYXB'
# # conn = cx_Oracle.connect(conn_str)
#
# cursor = conn.cursor()
# try:
#     cursor.execute("select 1 from dual")
#
#     conn.commit()
#     for row in cursor:
#         print row
# finally:
#     cursor.close()
#     conn.close()
